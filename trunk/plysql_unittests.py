import sys
import unittest

import ply.lex as lex    
import ply.yacc as yacc    

import plysql_token_rules    
import plysql_grammar_rules
import re

from plysql_classes import banner
from plysql_classes import Node

import plysql_reference

ref = plysql_reference.PlySqlReference()
ref.showReference()

class TestPlySql(unittest.TestCase):
    pass
    def setUp(self):
        self.lexer = lex.lex(module=plysql_token_rules, reflags = re.IGNORECASE)    

    def parseStatement(self,p_statement,p_start='statement'):       
        print banner('Statement','=')        
        print p_statement
        print banner('Lexer Results','=')        
        self.lexer.input(p_statement)    
        for tok in self.lexer:    
            print tok.type.rjust(16) + ' : ' + tok.value    
        print banner('Create Parser','=')
        self.parser = yacc.yacc(start=p_start,module=plysql_grammar_rules,outputdir='out')    
        print banner('Parse','=')        
        result = self.parser.parse(p_statement) 
        print result

        print banner('Simple Syntax and Metadata','=')        
        if result != None:
            result.debugMsg(result.getSyntaxStructure(),-1)
            result.showMetadata()
        print banner('Statement','=')        
        print p_statement
        print banner('end testcase','=')        
        
        return result   
    def printStartBanner(self):
        print banner(sys._getframe(1).f_code.co_name,'#')
        
    def compareDependencies(self,p_metadata,p_refMetadata=''):
        for k, v in p_metadata.iteritems():
            if v != []:
                self.assertEqual(v,p_refMetadata[k])
 
        for k, v in p_refMetadata.iteritems():
            self.assertEqual(v,p_metadata[k])


    #
    # ALIAS tests
    #
    def test_case_alias(self):
        '''test case '''
        self.printStartBanner()
        statement          = '''select case when x=y then z else 25  end as a1'''
        refSyntaxStructure = ['select', [['case', [[['when', ['x', '=', 'y']], 'then', 'z'], 'else', '25'], 'end'], 'as', 'a1']]
        refDependencies    = dict(literal_all          = ['25']
                                 ,identifiers_column   = ['x', 'y', 'z']
                                 ,aliases_column       = [('case when x = y then z else 25 end', 'a1')]
                                 ,identifiers_alias    = [('a1')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_cast_2(self):
        '''test cast 2'''
        self.printStartBanner()
        statement          = '''select cast(c1 as varchar(1024))'''
        refSyntaxStructure = ['select', ['cast', ['(', ['c1', 'as', ['varchar', ['(', '1024', ')']]], ')']]]
        refDependencies    = dict(identifiers_function  = ['varchar']
                                 ,literal_all        = ['1024']
                                 ,identifiers_column = ['c1']
                                 ,identifiers_alias  = ['varchar ( 1024 )']
                                 ,aliases_cast       = [('c1', 'varchar ( 1024 )')]
                                 ,identifiers_cast   = []
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_cast_1(self):
        '''test cast 1'''
        self.printStartBanner()
        statement          = '''select cast(c1 as float)'''
        refSyntaxStructure = ['select', ['cast', ['(', ['c1', 'as', 'float'], ')']]]
        refDependencies    = dict(identifiers_column  = ['c1']
                                 ,aliases_cast        = [('c1', 'float')]
                                 ,identifiers_alias   = ['float']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_star_dot_4_alias(self):
        '''test star dot 4'''
        self.printStartBanner()
        statement          = '''select t1.*, 1 * 2 as c1, pack.func(t1.x)'''
        refSyntaxStructure = ['select', [[['t1', '.', '*'], ',', [['1', '*', '2'], 'as', 'c1']], ',', [['pack', '.', 'func'], ['(', ['t1', '.', 'x'], ')']]]]
        refDependencies    = dict(literal_all             = ['1', '2']
                                 ,identifiers_column      = ['t1.*', 't1.x']
                                 ,identifiers_function    = ['pack.func']
                                 ,identifiers_alias       = ['c1']
                                 ,aliases_column          = [('1 * 2', 'c1')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_star_dot_2_alias(self):
        '''test star dot 2'''
        self.printStartBanner()
        statement          = '''select 1 * 2 as c1'''
        refSyntaxStructure = ['select', [['1', '*', '2'], 'as', 'c1']]
        refDependencies    = dict(literal_all        = ['1', '2']
                                 ,identifiers_column = []
                                 ,aliases_column     = [('1 * 2', 'c1')]
                                 ,alias_stack        = []
                                 ,identifiers_alias  = ['c1']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_view_1(self):
        '''view test'''
        self.printStartBanner()
        statement          = '''create view v as select * from dual;'''
        refSyntaxStructure = ['create', 'view', ['v', 'as', [['select', '*'], ['from', 'dual']]]]
        refDependencies    = dict(identifiers_column      = ['*']
                                 ,identifiers_table       = ['dual']
                                 ,aliases_view            = [('v', 'select * from dual')]
                                 ,identifiers_alias       = ['v']
                                 ,identifier_stack        = []
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)
 
    def test_join_1(self):
        '''join test'''
        self.printStartBanner()
        statement          = '''join table2 t2 on t1.x = t2.x'''
        refSyntaxStructure = ['join', ['table2', 't2'], 'on', [['t1', '.', 'x'], '=', ['t2', '.', 'x']]]
        refDependencies    = dict(aliases_table        = [('table2', 't2')]
                                 ,identifiers_alias    = ['t2']
                                 ,identifiers_column   = ['t1.x', 't2.x']
                                 ,identifiers_table    = ['table2']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_alias_1(self):
        '''alias test from tables'''
        self.printStartBanner()
        statement          = '''from t1 as T1, t2 as T2'''
        refSyntaxStructure = ['from', [['t1', 'as', 'T1'], ',', ['t2', 'as', 'T2']]]
        refDependencies    = dict(identifiers_table  = ['t1','t2']
                                 ,aliases_table      = [('t1','T1'),('t2','T2')]
                                 ,identifiers_alias  = ['T1','T2']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_alias_2(self):
        '''aliases test select columns'''
        self.printStartBanner()
        statement          = '''from t1 T1'''
        refSyntaxStructure = ['from', ['t1', 'T1']]
        refDependencies    = dict(identifiers_table  = ['t1']
                                 ,aliases_table      = [('t1','T1')]
                                 ,identifiers_alias  = ['T1']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_alias_3(self):
        '''aliases test with'''
        self.printStartBanner()
        statement          = '''with w as (select c1)'''
        refSyntaxStructure = ['with', ['w', 'as', ['(', ['select', 'c1'], ')']]]
        refDependencies    = dict(identifiers_column = ['c1']
                                 ,aliases_with       = [('w','( select c1 )')]
                                 ,identifiers_alias  = ['w']
                                 ,alias_stack        = []
                                 ,identifier_stack   = []
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    #
    # NON ALIAS tests
    #
    def test_case_2(self):
        '''test case '''
        self.printStartBanner()
        statement          = '''select case when x=y then z else 25  end '''
        refSyntaxStructure = ['select', ['case', [[['when', ['x', '=', 'y']], 'then', 'z'], 'else', '25'], 'end']]
        refDependencies    = dict(literal_all          = ['25']
                                 ,identifiers_column      = ['x', 'y', 'z']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_subquery_2(self):
        '''test case'''
        self.printStartBanner()
        statement          = '''select c1 from (select c2 from t2), (select c3 from t3)'''
        refSyntaxStructure = [['select', 'c1'], ['from', [['(', [['select', 'c2'], ['from', 't2']], ')'], ',', ['(', [['select', 'c3'], ['from', 't3']], ')']]]]
        refDependencies    = dict(identifiers_column      = ['c1', 'c2','c3']
                                 ,identifiers_table       = ['t2', 't3']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_subquery_1(self):
        '''test case'''
        self.printStartBanner()
        statement          = '''select c1 from (select c2 from (select c3 from t1))'''
        refSyntaxStructure = [['select', 'c1'], ['from', ['(', [['select', 'c2'], ['from', ['(', [['select', 'c3'], ['from', 't1']], ')']]], ')']]]
        refDependencies    = dict(identifiers_column      = ['c1', 'c2', 'c3']
                                 ,identifiers_table       = ['t1']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_and_or_1(self):
        '''test and or 1'''
        self.printStartBanner()
        statement          = '''where x=y and z=z'''
        refSyntaxStructure = ['where', [['x', '=', 'y'], 'and', ['z', '=', 'z']]]
        refDependencies    = dict(identifiers_column      = ['x', 'y', 'z', 'z']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_reserved_words(self):
        '''test and or 2'''
        self.printStartBanner()
        statement          = '''select andx, orx, integer'''
        #refSyntaxStructure = ['select', ['andx', ',', 'orx'',', 'integer']]
        #refDependencies    = dict(name_all       = ['andx','orx','integer']
        #                         ,names_column   = ['andx','orx','integer']
        #                         )
        #
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        #self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        #self.compareDependencies(result.getMetadata(),refDependencies)

    def test_is_null(self):
        '''test is null'''
        self.printStartBanner()
        statement          = '''where x is null'''
        refSyntaxStructure = ['where', ['x', 'is', 'null']]
        refDependencies    = dict(identifiers_column  = ['x']
                                 ,literal_all      = ['null']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_star_dot_1(self):
        '''test star dot 1'''
        self.printStartBanner()
        statement          = '''select t1.*'''
        refSyntaxStructure = ['select', ['t1', '.', '*']]
        refDependencies    = dict(identifiers_column      = ['t1.*']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_star_dot_3(self):
        '''test star dot 3'''
        self.printStartBanner()
        statement          = '''select pack.func(t1.x)'''
        refSyntaxStructure = ['select', [['pack', '.', 'func'], ['(', ['t1', '.', 'x'], ')']]]
        refDependencies    = dict(identifiers_column      = ['t1.x']
                                 ,identifiers_function    = ['pack.func']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_star_dot_5(self):
        '''test star dot 5'''
        self.printStartBanner()
        statement          = '''select c1 * c2'''
        refSyntaxStructure = ['select', ['c1', '*', 'c2']]
        refDependencies    = dict(identifiers_column      = ['c1', 'c2']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_star_dot_6(self):
        '''test star dot 6'''
        self.printStartBanner()
        statement          = '''select c1 * 5'''
        refSyntaxStructure = ['select', ['c1', '*', '5']]
        refDependencies    = dict(literal_all          = ['5']
                                 ,identifiers_column      = ['c1']
                                 )
       
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_partition_by_1(self):
        '''partition by 1'''
        self.printStartBanner()
        statement          = '''select sum(x) over (partition by y order by z)'''
        refSyntaxStructure = ['select', [['sum', ['(', 'x', ')']], 'over', ['(', [['partition by', 'y'], ['order by', 'z']], ')']]]
        refDependencies    = dict(identifiers_column      = ['y', 'z', 'x']
                                 ,identifiers_function    = ['sum']
                                 )

        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_partition_by_2(self):
        '''partition by 2'''
        self.printStartBanner()
        statement          = '''select sum(x) over (partition by y)'''
        refSyntaxStructure = ['select', [['sum', ['(', 'x', ')']], 'over', ['(', ['partition by', 'y'], ')']]]
        refDependencies    = dict(identifiers_column      = ['y', 'x']
                                 ,identifiers_function    = ['sum']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_partition_by_2(self):
        '''partition by 2'''
        self.printStartBanner()
        statement          = '''select 2+ sum(x) over (partition by y)'''
        refSyntaxStructure = ['select', [['2', '+', ['sum', ['(', 'x', ')']]], 'over', ['(', ['partition by', 'y'], ')']]]
        refDependencies    = dict(literal_all          = ['2']
                                 ,identifiers_column      = ['y', 'x']
                                 ,identifiers_function    = ['sum']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_function_1(self):
        '''test case '''
        self.printStartBanner()
        statement          = '''select func()'''
        refSyntaxStructure = ['select', ['func', ['(', ')']]]
        refDependencies    = dict(identifiers_column      = []
                                 ,identifiers_function    = ['func']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_function_2(self):
        '''function test'''
        self.printStartBanner()
        statement          = '''select substr(x,1,2)'''
        refSyntaxStructure = ['select', ['substr', ['(', [['x', ',', '1'], ',', '2'], ')']]]
        refDependencies    = dict(identifiers_column   = ['x']
                                 ,identifiers_function = ['substr']
                                 ,literal_all       = ['1','2']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_1(self):
        '''simple sql test'''
        self.printStartBanner()
        statement          = '''select c1 from t1'''
        refSyntaxStructure = [['select', 'c1'], ['from', 't1']]
        refDependencies    = dict(identifiers_column   = ['c1']
                                 ,identifiers_table    = ['t1']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_2(self):
        '''unary MINUS test'''
        self.printStartBanner()
        statement          = '''select -12'''
        refSyntaxStructure = ['select', ['-', '12']]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)

    def test_3(self):
        '''binary MINUS test'''
        self.printStartBanner()
        statement          = '''select 24-12'''
        refSyntaxStructure = ['select', ['24','-', '12']]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)

    def test_4(self):
        '''subquery test'''
        self.printStartBanner()
        statement          = '''select (select 1) + 5'''
        refSyntaxStructure = ['select', [['(', ['select', '1'], ')'], '+', '5']]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)

    def test_5(self):
        '''select *'''
        self.printStartBanner()
        statement          = '''select *, 1 * 5'''
        refSyntaxStructure = ['select', ['*', ',', ['1', '*', '5']]]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        
    def test_6(self):
        '''inline view (from clause query)'''
        self.printStartBanner()
        statement          = '''from (select c1 from t1)'''
        refSyntaxStructure = ['from', ['(', [['select', 'c1'], ['from', 't1']], ')']]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        
    def test_7(self):
        '''nested queries'''
        self.printStartBanner()
        statement          = '''from (select c1 from (select c2 from t2) )'''
        refSyntaxStructure = ['from', ['(', [['select', 'c1'], ['from', ['(', [['select', 'c2'], ['from', 't2']], ')']]], ')']]        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)

    def test_8(self):
        '''with'''
        self.printStartBanner()
        statement          = '''with w1 as (select c1 from t1)'''
        refSyntaxStructure = ['with', ['w1', 'as', ['(', [['select', 'c1'], ['from', 't1']], ')']]]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        
    def test_9(self):
        '''multiple withs'''
        self.printStartBanner()
        statement          = '''with w1 as (select c1 from t1), w2 as (select c2 from t2)'''
        refSyntaxStructure = ['with', [['w1', 'as', ['(', [['select', 'c1'], ['from', 't1']], ')']], ',', ['w2', 'as', ['(', [['select', 'c2'], ['from', 't2']], ')']]]]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)

    #def suite(self):
    #    #suite = unittest.TestLoader().loadTestsFromTestCase(TestPlySql)
    #    suite = unittest.Testsuite()
    #    suite.addTest(TestPlySql('test case'))

    #def tearDown(self):
    #    self.lexer = None
    #    self.parser = None


#suite = TestPlySql().suite()
#unittest.TextTestRunner(verbosity=2).run(suite)

unittest.main()
