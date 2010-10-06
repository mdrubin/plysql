class SqlMetadata:
    def __init__(self,p_type,p_args):
        # DEP
        self.deps = {  'literal_all':[]    
                     , 'mapping_stack':[], 'mappings_view':[], 'mappings_with':[], 'mappings_table':[], 'mappings_column':[], 'mappings_function':[], 'mappings_cast':[]  
                     }

    def debugMsg(self, p_msg,p_debugLevel):
        if self.debugLevel >= p_debugLevel:
            method= self.__class__.__name__ + '.' + sys._getframe(1).f_code.co_name
            print str(p_debugLevel).rjust(2) + ' : ' + self.type.rjust(24) + ' : ' + method.rjust(30) + ' : ' + str(p_msg)

    def debugVariable(self,p_varname):
        self.debugMsg(p_varname + str(self.deps[p_varname]),2)

    def getDeps(self):
        return self.deps

    def showDeps(self):
        print banner('dependencies','=')
        print str(self.deps)
        #for d in sorted(self.deps):
        #    print d.ljust(20) + ':'.center(3) + str(self.deps[d])
        #print 

    def addLiteral(self,p_value):
        '''This methods is used by the identifier rule to add identifiers to the pool.'''
        self.deps['literal_all']  += [p_value]
        
    ### DEP ###################
    def setName(self,p_value):
        '''This methods is used by the identifier and star rule to add identifiers to the pool.'''
        debugVariable('mapping_stack')

        self.deps['mapping_stack']  = [(p_value,p_value)]
        self.deps['mappings_all']    = [(p_value,p_value)]
        
        debugVariable('mapping_stack')
        
    def setNameWithDots(self,p_value1,p_value2):
        '''This methods is used by the identifier and star rule to add identifiers to the pool.'''
        debugVariable('mapping_stack')

        # override default value as set in addElementValues()
        self.value               = p_value1.getValue() + '.' + p_value2
        self.debugMsg("self.value=" + self.value,2)

        self.deps['mapping_stack']  = [(self.value,self.value)]
        self.deps['mappings_all']    =[(self.value,self.value)]
        
        debugVariable('mapping_stack')
        
    def setMapping(self,p_expr1,p_expr2):
        '''This method is used to store names and their meaning.'''
        self.debugMsg((p_expr1.getValue()                ,p_expr2.getValue())                , 2)
        debugVariable('mapping_stack')
        
        self.deps['mapping_stack']  = [(p_expr1.getValue(),p_expr2.getValue())]
        
        debugVariable('mapping_stack')

    def addMapping(self,p_expr1,p_expr2):
        '''This method is used to store names and their meaning.'''
        self.debugMsg((p_expr1.getValue()                ,p_expr2.getValue())                , 2)
        debugVariable('mapping_stack')
        
        self.deps['mapping_stack']  += [(p_expr1.getValue(),p_expr2.getValue())]
        
        debugVariable('mapping_stack')

    def moveMappingstack(self,p_element,p_target):
        '''This method is used to store names and their meaning.'''
        debugVariable('mapping_stack')

        self.deps[p_target] += p_element.getDeps()['mapping_stack']
        self.deps['mapping_stack'] = []

        debugVariable('mapping_stack')

    def moveMapping(self,p_element,p_target):
        '''This method is used to store names and their meaning.'''
        self.debugMsg("p_element.mapping_stack=" + str(p_element.getDeps()['mapping_stack']),2)
        debugVariable('mapping_stack')
        
        self.deps[p_target] += p_element.getDeps()['mapping_stack']
        self.deps['mapping_stack'].remove(p_element.getDeps()['mapping_stack'][0])

        debugVariable('mapping_stack')
