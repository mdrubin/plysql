import sys
import re
import types

def banner(text, ch='.', length=70): 
    if text == '':
        spaced_text = ''
    else:            
        spaced_text = ' %s ' % text 
    banner = spaced_text.center(length, ch).upper() 
    return banner            

    # store p[0]
    # transfer p[0] to string
    # add dependencies
    # add names
    #
    # get parameters
    #     wrap terminals (operators, identifiers) 
    # execute common actions
    #     initialize deps dictionary
    #     set value
    #     output value
    # add dependencies
    #     get dependencies from your arguments
    # 
    # patterns
    #    unary:         (operator, argument)                                      argument                      --> addDeps
    #    binary:        (left_argument, operator, right_argument)                 left_argument,right_argument  --> addDeps
    #    binary2:       (operator1, argument1, operator2, argument2)              argument1,argument2           --> addDeps
    #    recursive:     (element)  addElement (separator, element) -> elements[]  element                       --> addDeps
    #    parenthesized: (element)                                                 element                       --> addDeps
    #    named:         (content,name)                                            contenct                      --> addDeps    name --> namestack, names
    #    unary:         (operator,argument)                                       argument                      --> addDeps
    
class Node:    
    def __init__(self,p_type,p_args):
        self.debugLevel = 0
        self.type = p_type
        self.elements = []
        self.SyntaxStructure = []
        self.branche = []
        self.value  = ''
        self.deps = {  'literal_all':[]    
                     , 'mapping_stack':[], 'mappings_view':[], 'mappings_with':[], 'mappings_table':[], 'mappings_column':[], 'mappings_function':[], 'mappings_cast':[]  
                     }
        #self.subqueryLevel = 0
        #self.subqueryId    = 0    
        self.init2(p_args)                   
    def init2(self,p_args):                    
        pass
    def getElements(self):
        return self.elements
    def getType(self):
        return self.type
    def getValue(self):
        return self.value
    def getSyntaxStructure(self):
        return self.SyntaxStructure 
    def getDeps(self):
        return self.deps
    def debugMsg(self, p_msg,p_debugLevel):
        if self.debugLevel >= p_debugLevel:
            method= self.__class__.__name__ + '.' + sys._getframe(1).f_code.co_name
            print str(p_debugLevel).rjust(2) + ' : ' + self.type.rjust(24) + ' : ' + method.rjust(30) + ' : ' + str(p_msg)
    def showDeps(self):
        print banner('dependencies','=')
        print str(self.deps)
        #for d in sorted(self.deps):
        #    print d.ljust(20) + ':'.center(3) + str(self.deps[d])
        #print 
    def wrap(self,p_element):
        '''Add getter methods to an element. This method is used for grammar rules that return terminals (e.g. operators, identifiers) that have string datatype.'''
        if type(p_element) != types.InstanceType:
            return Terminal('term',p_element)
        else: 
            return p_element
        
class Terminal(Node):
    def init2(self,p_value):                    
        self.value = p_value
        self.type  = 'terminal'

class NonTerminal(Node):
    def init2(self,p_elements):
        self.addElements(p_elements)
        self.addElementValues()
        self.propagate()

        self.debugMsg('value=' + self.value,1)
        #self.showDeps()
        #self.debugMsg(self.SyntaxStructure,1)
        
    # Elements        
    def getType(self):
        return self.type[2:].replace('_first','').replace('_next','')
    def addElements(self,p_elements):
        '''Add the elements returned from the grammar rule to the object'''        
        for e in p_elements:
            # remove p[0] because p[0]= None, (This node is instantiated and p[0] has not yet been asigned this object.) and remove empty tokens 
            if type(e) != types.NoneType and self.wrap(e).getValue() != '':
                self.debugMsg(type(e), 1)    
                self.elements += [self.wrap(e)]
    def addElementValues(self):
        '''Per Element, concatenate the values to construct the sentence belonging to this object.'''        
        for e in self.elements:
            self.value += ' '+ e.getValue()
            # when we have a pass through rule e.g. expr : NUMBER a space is added.These spaces must be stripped.
            self.value = self.value.lstrip(' ')

    # Propagate
    def propagate(self):
        # '''Per element add the dependencies to this object. This method is used for propagating dependencies from one node to another.'''
        
        # set deps 
        for e in self.elements:
            self.debugMsg(e,3)
        
            #create simple SyntaxStructure
            if e.type == 'terminal':
                self.debugMsg('e.type == terminal',3)
                self.branche.append(e.getValue())
            elif e.SyntaxStructure != []:
                self.debugMsg('e.SyntaxStructure != []',3)
                self.branche.append(e.SyntaxStructure)
            self.debugMsg(self.branche,3)
                
            for d in self.deps:
                # Dependencies    
                self.deps[d] += e.getDeps()[d]
                
        if len(self.branche)   > 1:
            self.debugMsg('len(e.branche)   > 1',3)
            self.SyntaxStructure = self.branche
        elif len(self.branche) == 1:
            self.debugMsg('len(e.branche) == 1',3)
            self.SyntaxStructure = self.branche[0]
        self.debugMsg('SyntaxStructure=' + str(self.SyntaxStructure),2)
        
    def addLiteral(self,p_value):
        '''This methods is used by the identifier rule to add identifiers to the pool.'''
        self.debugMsg(p_value ,2)
        self.deps['literal_all']  += [p_value]
        
    def setName(self,p_value):
        '''This methods is used by the identifier and star rule to add identifiers to the pool.'''
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)

        self.deps['mapping_stack']  = [(p_value,p_value)]
        self.deps['mappings_all']    = [(p_value,p_value)]
        
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)
        
    def setNameWithDots(self,p_value1,p_value2):
        '''This methods is used by the identifier and star rule to add identifiers to the pool.'''
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)

        # override default value as set in addElementValues()
        self.value               = p_value1.getValue() + '.' + p_value2
        self.debugMsg("self.value=" + self.value,2)

        self.deps['mapping_stack']  = [(self.value,self.value)]
        self.deps['mappings_all']    =[(self.value,self.value)]
        
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)
        
    # Mappings
    def setMapping(self,p_expr1,p_expr2):
        '''This method is used to store names and their meaning.'''
        self.debugMsg((p_expr1.getValue()                ,p_expr2.getValue())                , 2)
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)
        
        self.deps['mapping_stack']  = [(p_expr1.getValue(),p_expr2.getValue())]
        
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)

    def addMapping(self,p_expr1,p_expr2):
        '''This method is used to store names and their meaning.'''
        self.debugMsg((p_expr1.getValue()                ,p_expr2.getValue())                , 2)
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)
        
        self.deps['mapping_stack']  += [(p_expr1.getValue(),p_expr2.getValue())]
        
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)

    def moveMappingstack(self,p_element,p_target):
        '''This method is used to store names and their meaning.'''
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)

        self.deps[p_target] += p_element.getDeps()['mapping_stack']
        self.deps['mapping_stack'] = []

        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)

    def moveMapping(self,p_element,p_target):
        '''This method is used to store names and their meaning.'''
        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)
        self.debugMsg("p_element.mapping_stack=" + str(p_element.getDeps()['mapping_stack']),2)
        
        self.deps[p_target] += p_element.getDeps()['mapping_stack']
        self.deps['mapping_stack'].remove(p_element.getDeps()['mapping_stack'][0])

        self.debugMsg("mapping_stack=" + str(self.deps['mapping_stack']),2)
