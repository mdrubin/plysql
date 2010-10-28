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

class Query():
    def initSqlMetadata(self):
        self.debugLevel = 0
        self.queryType  = None
        self.name       = None
        self.children   = []
        self.initMetadata()
    
    def initMetadata(self):
        self.metadata   = {  'literal_all':[]    
                          , 'identifier_stack':[]                                 , 'identifiers_table':[], 'identifiers_column':[], 'identifiers_function':[],'identifiers_cast':[], 'identifiers_alias':[]                  
                          , 'alias_stack':[], 'aliases_view':[], 'aliases_with':[], 'aliases_table':[]    , 'aliases_column':[]                               ,'aliases_cast':[]  
                          , 'subqueries':[],
                          }

    def getMetadata(self):
        return self.metadata

    def getMetadataInternal(self):
        metadata_all = self.metadata
        for q in self.metadata['subqueries']:
           metadata_all += q.getMetadata()
        return metadata_all

    def showMetadata(self):
        print banner('metadata','=')
        #print self.metadata
        for d, v in sorted(self.metadata.iteritems()):
            if v != []:
               print d.ljust(20) + ':'.center(3) + str(v)
        print banner('subquery','=')
        for q in sorted(self.metadata['subqueries']):
            q.showMetadata()
        
    def setLiteral(self,p_value):
        '''This methods is used by the literal rule to add literals (NUMBER,STRING,NULL) to the pool.'''
        self.debugMsg(p_value ,2)
        self.metadata['literal_all'] = [p_value]
        
    def setIdentifier(self,p_value):
        '''This methods is used by the identifier and star rule to add identifiers (INDENTIFIER,STAR) to the pool.'''
        self.debugVariable('identifier_stack')

        self.metadata['identifier_stack']  = [p_value]
        self.metadata['identifiers_all']   = [p_value]
        
        self.debugVariable('identifier_stack')
        
    def setIdentifierWithDots(self,p_value1,p_value2):
        '''This methods is used by the identifier and star rule to add dotted identifiers (IDENTIFIER.IDENTIFIER,IDENTIFIER.STAR) to the pool.'''
        self.debugVariable('identifier_stack')

        # override default value as set in addElementValues()
        self.value = p_value1.getValue() + '.' + p_value2
        self.debugMsg("self.value=" + self.value,2)

        self.metadata['identifier_stack']  = [self.value]
        self.metadata['identifiers_all']   = [self.value]
        
        self.debugVariable('identifier_stack')
        
    def moveIdentifier(self,p_element,p_target):
        '''This method is used to move a single element from the stack.'''
        self.debugVariable('identifier_stack')
        self.debugMsg("p_element.identifier_stack=" + str(p_element.getMetadata()['identifier_stack']),2)
        
        self.metadata[p_target] += p_element.getMetadata()['identifier_stack']
        self.metadata['identifier_stack'].remove(p_element.getMetadata()['identifier_stack'][0])

        self.debugVariable('identifier_stack')

    def moveIdentifierstack(self,p_element,p_target):
        '''This method is used to move the complete stack.'''
        self.debugMsg('p_element=' + str(p_element.getMetadata()),2)
        self.debugVariable('identifier_stack')
        self.debugVariable(p_target)

        identifierStack = self.metadata['identifier_stack']
        elementStack    = p_element.getMetadata()['identifier_stack']

        self.debugMsg('identifierStack='  + str(identifierStack),2)
        self.debugMsg('elementStack='     + str(elementStack),2)

        self.metadata[p_target] += elementStack
        self.metadata['identifier_stack']  =  [i for i in identifierStack if i not in elementStack]

        self.debugVariable('identifier_stack')

    def setAlias(self,p_expr1,p_expr2):
        '''This method is used by alias and as expressions to store names and their meaning.'''
        self.debugMsg( (p_expr1.getValue(),p_expr2.getValue()) , 2)
        self.debugVariable('alias_stack')
        
        self.metadata['alias_stack']   =  [(p_expr1.getValue(),p_expr2.getValue())]
        
        self.debugVariable('alias_stack')

    def moveAlias(self,p_element,p_target):
        '''This method is used to move a single element from the stack.'''
        self.debugVariable('alias_stack')
        self.debugMsg("p_element.alias_stack=" + str(p_element.getMetadata()['alias_stack']),2)
        
        self.metadata[p_target]      += p_element.getMetadata()['alias_stack']
        self.metadata['alias_stack'].remove(p_element.getMetadata()['alias_stack'][0])

        self.debugVariable('alias_stack')

    def moveAliasIdentifier(self,p_element,p_identifier):
        '''This method is used to move a single element from the stack.'''
        self.debugVariable('identifier_stack')
        self.debugVariable('alias_stack')
        self.debugMsg("p_element.alias_stack=" + str(p_element.getMetadata()['alias_stack']),2)
        
        self.metadata['identifiers_alias']  +=   [p_element.getMetadata()['alias_stack'][0][p_identifier]]
        try:
            self.metadata['identifier_stack'].remove(p_element.getMetadata()['alias_stack'][0][p_identifier])
        except ValueError:
            self.debugMsg('WARNING: AliasIdentifier cannot be removed from the identifierStack, probably a "cast as varchar()" or so.',2)
        self.debugVariable('alias_stack')
        self.debugVariable('identifier_stack')

    def moveAliasstack(self,p_element,p_target):
        '''This method is used to move the complete stack.'''
        self.debugVariable('alias_stack')

        self.metadata[p_target]      += p_element.getMetadata()['alias_stack']
        self.metadata['alias_stack']  = []

        self.debugVariable('alias_stack')

    def moveAliasIdentifiers(self,p_alias,p_identifier):
        '''This method is used to move the alias identifier.'''
        self.debugMsg('p_alias=' + str(p_alias.getMetadata()),2)
        self.debugVariable('identifier_stack')
        self.debugVariable('identifiers_alias')
        

        aliasStack       = p_alias.getMetadata()['alias_stack']
        aliasIdentifiers = [a[p_identifier]  for a in aliasStack]
        identifierStack  = self.metadata['identifier_stack']

        self.debugMsg('aliasStack='       + str(aliasStack),2)
        self.debugMsg('aliasIdentifiers=' + str(aliasIdentifiers),2)
        self.debugMsg('identifierStack='  + str(identifierStack),2)
        
        self.metadata['identifiers_alias'] += aliasIdentifiers
        self.metadata['identifier_stack']  =  [i for i in identifierStack if i not in aliasIdentifiers]

        self.debugVariable('identifiers_alias')
        self.debugVariable('identifier_stack')
        self.debugMsg('END moveAliasIdentifiers',2)
    def setSubquery(self,p_subquery):
        self.initMetadata()
        self.metadata['subqueries'] = [p_subquery]
        
class Node(Query):    
    def initNode(self):
        self.initSqlMetadata()

        self.nodeType = sys._getframe(2).f_code.co_name
        self.elements = []
        self.SyntaxStructure = []
        self.branche = []
        self.value  = ''
        
    def debugMsg(self, p_msg,p_debugLevel=0,p_frame=1):
        if self.debugLevel >= p_debugLevel:
            method= self.__class__.__name__ + '.' + sys._getframe(p_frame).f_code.co_name
            print str(p_debugLevel).rjust(2) + ' : ' + self.nodeType.rjust(32) + ' : ' + method.rjust(32) + ' : ' + str(p_msg)

    def debugVariable(self,p_varname):
        self.debugMsg('metadata[' + p_varname + ']=' + str(self.metadata[p_varname]),2,2)

    def getElements(self):
        return self.elements

    def getType(self):
        return self.nodeType

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
        self.nodeType  = 'terminal'

class NonTerminal(Node):
    def __init__(self,p_elements):
        self.initNode()

        # create tree synntax that follows the grammar rules exactly
        self.addElements(p_elements)
        # create the sentence belonging to this node.
        self.addElementValues()
        # set the metadata and create a simple syntax tree
        self.propagate()

        self.debugMsg('value=' + self.value,1)
        
    # Elements        
    def getType(self):
        return self.nodeType[2:].replace('_first','').replace('_next','')

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
            self.debugMsg(e.nodeType, 1)    
            self.value += ' '+ e.getValue()
            # when we have a pass through rule e.g. expr : NUMBER a space is added.These spaces must be stripped.
            self.value = self.value.lstrip(' ')

    # Propagate
    def propagate(self):
        '''Per element add the metadata to this object. This method is used for propagating metadata from one node to another.'''
        
        # per element add element metadata to the metadata of this node
        #             create simple syntax structure.
        for e in self.elements:
            self.debugMsg(e,3)
        
            for d in self.metadata:
                # Dependencies    
                self.metadata[d] += e.getMetadata()[d]
                
            #create simple SyntaxStructure
            # no brackets around terminals
            # ignore empty elements (does this occur ?)
            # no brackets around a single element. 
            if e.nodeType == 'terminal':
                self.debugMsg('e.type == terminal',3)
                self.branche.append(e.getValue())
            elif e.SyntaxStructure != []:
                self.debugMsg('e.SyntaxStructure != []',3)
                self.branche.append(e.SyntaxStructure)
            self.debugMsg(self.branche,3)

        # create a new list (syntax structure level) when there is more than 1 element
        if len(self.branche)   > 1:
            self.debugMsg('len(e.branche)   > 1',3)
            self.SyntaxStructure = self.branche
        # if there is just 1 element, don't create a new list (syntax structure level)
        elif len(self.branche) == 1:
            self.debugMsg('len(e.branche) == 1',3)
            self.SyntaxStructure = self.branche[0]
        self.debugMsg('SyntaxStructure=' + str(self.SyntaxStructure),2)
