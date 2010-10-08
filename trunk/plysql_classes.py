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

class SqlMetadata():
    def initSqlMetadata(self):
        self.debugLevel = 0
        self.metadata = {  'literal_all':[]    
                        , 'name_stack':[], 'mappings_view':[], 'mappings_with':[], 'mappings_table':[], 'mappings_column':[], 'mappings_function':[], 'mappings_cast':[]  
                        , 'mapping_stack':[], 'mappings_view':[], 'mappings_with':[], 'mappings_table':[], 'mappings_column':[], 'mappings_function':[], 'mappings_cast':[]  
                        }
    
    def debugMsg(self, p_msg,p_debugLevel):
        if self.debugLevel >= p_debugLevel:
            method= self.__class__.__name__ + '.' + sys._getframe(1).f_code.co_name
            print str(p_debugLevel).rjust(2) + ' : ' + self.type.rjust(24) + ' : ' + method.rjust(30) + ' : ' + str(p_msg)

    def debugVariable(self,p_varname):
        self.debugMsg(p_varname + str(self.metadata[p_varname]),2)

    def getMetadata(self):
        return self.metadata

    def showMetadata(self):
        print banner('metadata','=')
        for d in sorted(self.metadata):
            print d.ljust(20) + ':'.center(3) + str(self.metadata[d])
        #print str(self.metadata)
        print 

    def setLiteral(self,p_value):
        '''This methods is used by the literal rule to add literals (NUMBER,STRING,NULL) to the pool.'''
        self.debugMsg(p_value ,2)
        self.metadata['literal_all'] = [p_value]
        
    def setIdentifier(self,p_value):
        '''This methods is used by the identifier and star rule to add identifiers (INDENTIFIER,STAR) to the pool.'''
        self.debugVariable('mapping_stack')

        self.metadata['mapping_stack']  = [(p_value,p_value)]
        self.metadata['mappings_all']   = [(p_value,p_value)]
        
        self.debugVariable('mapping_stack')
        
    def setIdentifierWithDots(self,p_value1,p_value2):
        '''This methods is used by the identifier and star rule to add dotted identifiers (IDENTIFIER.IDENTIFIER,IDENTIFIER.STAR) to the pool.'''
        self.debugVariable('mapping_stack')

        # override default value as set in addElementValues()
        self.value = p_value1.getValue() + '.' + p_value2
        self.debugMsg("self.value=" + self.value,2)

        self.metadata['mapping_stack']  = [(self.value,self.value)]
        self.metadata['mappings_all']   = [(self.value,self.value)]
        
        self.debugVariable('mapping_stack')
        
    def addMapping(self,p_expr1,p_expr2):
        '''This method is used by alias and as expressions to store names and their meaning.'''
        self.debugMsg( (p_expr1.getValue(),p_expr2.getValue()) , 2)
        self.debugVariable('mapping_stack')
        
        self.metadata['mapping_stack']  += [(p_expr1.getValue(),p_expr2.getValue())]
        #self.metadata['mappings_all']   += [(p_expr1.getValue(),p_expr2.getValue())]

        self.debugVariable('mapping_stack')

    def moveMapping(self,p_element,p_target):
        '''This method is used to move a single element from the stack.'''
        self.debugMsg("mapping_stack=" + str(self.metadata['mapping_stack']),2)
        self.debugMsg("p_element.mapping_stack=" + str(p_element.getMetadata()['mapping_stack']),2)
        
        self.metadata[p_target] += p_element.getMetadata()['mapping_stack']
        self.metadata['mapping_stack'].remove(p_element.getMetadata()['mapping_stack'][0])

        self.debugVariable('mapping_stack')

    def moveMappingstack(self,p_element,p_target):
        '''This method is used to move the complete stack.'''
        self.debugVariable('mapping_stack')

        self.metadata[p_target] += p_element.getMetadata()['mapping_stack']
        self.metadata['mapping_stack'] = []

        self.debugVariable('mapping_stack')

class Node(SqlMetadata):    
    def initNode(self):
        self.initSqlMetadata()

        self.type = sys._getframe(2).f_code.co_name
        self.elements = []
        self.SyntaxStructure = []
        self.branche = []
        self.value  = ''
        
    def getElements(self):
        return self.elements

    def getType(self):
        return self.type

    def getValue(self):
        return self.value

    def getSyntaxStructure(self):
        return self.SyntaxStructure 

    def wrap(self,p_element):
        '''Add getter methods to an element. This method is used for grammar rules that return terminals (e.g. operators, identifiers) that have string datatype.'''
        if type(p_element) != types.InstanceType:
            return Terminal(p_element)
        else: 
            return p_element
        
class Terminal(Node):
    def __init__(self,p_value):
        self.initNode()
        self.value = p_value
        self.type  = 'terminal'

class NonTerminal(Node):
    def __init__(self,p_elements):
        self.initNode()

        self.addElements(p_elements)
        self.addElementValues()
        self.propagate()

        self.debugMsg('value=' + self.value,1)
        
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
            self.debugMsg(e.type, 1)    
            self.value += ' '+ e.getValue()
            # when we have a pass through rule e.g. expr : NUMBER a space is added.These spaces must be stripped.
            self.value = self.value.lstrip(' ')

    # Propagate
    def propagate(self):
        '''Per element add the metadata to this object. This method is used for propagating metadata from one node to another.'''
        
        # set metadata
        for e in self.elements:
            self.debugMsg(e,3)
        
            #create simple SyntaxStructure
            # no brackets around terminals
            # ignore empty elements (does this occur ?)
            # no brackets around a single element. 
            if e.type == 'terminal':
                self.debugMsg('e.type == terminal',3)
                self.branche.append(e.getValue())
            elif e.SyntaxStructure != []:
                self.debugMsg('e.SyntaxStructure != []',3)
                self.branche.append(e.SyntaxStructure)
            self.debugMsg(self.branche,3)
                
            for d in self.metadata:
                # Dependencies    
                self.metadata[d] += e.getMetadata()[d]
                
        if len(self.branche)   > 1:
            self.debugMsg('len(e.branche)   > 1',3)
            self.SyntaxStructure = self.branche
        elif len(self.branche) == 1:
            self.debugMsg('len(e.branche) == 1',3)
            self.SyntaxStructure = self.branche[0]
        self.debugMsg('SyntaxStructure=' + str(self.SyntaxStructure),2)