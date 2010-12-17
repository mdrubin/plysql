import unittest
import sys

import ply.lex as lex    
import ply.yacc as yacc    

import plysql_token_rules    
import plysql_grammar_rules
import re

from plysql_classes import banner
from plysql_classes import Node

class TestPlySql(unittest.TestCase):
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
            result.debugMsg(result.getSyntaxStructure(),1)
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


    def test_between_01(self):
        '''between 01'''
        self.printStartBanner()
        statement          = '''select c from t where c between 1 and 2 '''
        refSyntaxStructure = [[['select', 'c'], ['from', 't']], ['where', ['c', 'between', ['1', 'and', '2']]]]
        refDependencies    = dict(identifier_stack        = []
                                 ,identifiers_column      = ['c','c']
                                 ,literal_all             = ['1','2']
                                 ,identifiers_table       = ['t']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_create_table_1(self):
        '''create table test 1'''
        self.printStartBanner()
        statement          = '''create table tab1 (numbercol1 number);'''
        refSyntaxStructure = ['create table', 'tab1', ['(', ['numbercol1', 'number'], ')']]
        refDependencies    = dict(identifier_stack        = []
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

    def test_create_table_2(self):
        '''create table test 2'''
        self.printStartBanner()
        statement          = '''create table tab1 (col1 number(3,1));'''
        refSyntaxStructure = ['create table', 'tab1', ['(', ['col1', ['number', ['(', ['3', ',', '1'], ')']]], ')']]
        refDependencies    = dict(identifier_stack        = []
                                 ,literal_all             = ['3','1']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)
    #
    # SubQuery
    #
    def test_subquery_4(self):
        '''subquery 4'''
        self.printStartBanner()
        statement          = '''select (select 1) + 5'''
        refSyntaxStructure = ['select', [['(', ['select', '1'], ')'], '+', '5']]
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)

    def test_subquery_3(self):
        '''subquery 3'''
        self.printStartBanner()
        statement          = '''select c1 from (select c2 from t2) as q1 , (select c3 from (select c4 from t4) as q4)'''
        refSyntaxStructure = [['select', 'c1'], ['from', [[['(', [['select', 'c2'], ['from', 't2']], ')'], 'as', 'q1'], ',', ['(', [['select', 'c3'], ['from', [['(', [['select', 'c4'], ['from', 't4']], ')'], 'as', 'q4']]], ')']]]]
        refDependencies    = dict(identifiers_column      = ['c1', 'c2','c3']
                                 ,identifiers_table       = ['t2', 't3']
                                 ,subqueries              = ['select c2 from t2','select c4 from t4']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        #self.compareDependencies(result.getMetadata(),refDependencies)

    def test_subquery_2(self):
        '''subquery 2'''
        self.printStartBanner()
        statement          = '''select c1 from (select c2 from t2), (select c3 from t3)'''
        refSyntaxStructure = [['select', 'c1'], ['from', [['(', [['select', 'c2'], ['from', 't2']], ')'], ',', ['(', [['select', 'c3'], ['from', 't3']], ')']]]]
        refDependencies    = dict(identifiers_column      = ['c1', 'c2','c3']
                                 ,identifiers_table       = ['t2', 't3']
                                 ,subqueries              = ['select c2 from t2','select c3 from t3']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        #self.compareDependencies(result.getMetadata(),refDependencies)

    def test_subquery_1(self):
        '''subquery 1'''
        self.printStartBanner()
        statement          = '''select c1 from (select c2 from (select c3 from t1))'''
        refSyntaxStructure = [['select', 'c1'], ['from', ['(', [['select', 'c2'], ['from', ['(', [['select', 'c3'], ['from', 't1']], ')']]], ')']]]
        refDependencies    = dict(identifiers_column      = ['c1']
                                 ,identifiers_table       = ['t1']
                                 ,subqueries              = ['select c2 from (select c3 from t1)','select c3 from t1']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareDependencies(result.getMetadata(),refDependencies)

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
        refDependencies    = dict(literal_all           = ['1024']
                                 ,identifiers_column    = ['c1']
                                 ,identifiers_alias     = ['varchar ( 1024 )']
                                 ,aliases_cast          = [('c1', 'varchar ( 1024 )')]
                                 ,identifiers_function  = ['varchar']
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
        refSyntaxStructure = ['create view', ['v', 'as', [['select', '*'], ['from', 'dual']]]] 
        refDependencies    = dict(identifiers_column      = ['*']
                                 ,identifiers_table       = ['dual']
                                 ,aliases_view            = [('v', 'select * from dual')]
                                 ,identifiers_alias       = ['v']
                                 ,identifier_stack        = []
                                 ,subqueries              = ['select * from dual']
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
                                 ,subqueries         = ['select c1']     
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

    def test_statement1(self):
        '''test_statement1'''
        self.printStartBanner()
        statement          = '''
create view XMCARE_STG.STG_PRODUCTIE_AFSPRAKEN_VW
  as
select    'PRODAFSPR' bron
,         a.JAAR_MAAND
,         isnull(kpl.kstpl_code,'-1')             as KOSTENPLAATS
,         isnull(fin.financiering_id,'ONBEKEND')  as financiering_id
,         isnull(i.item_code,'ONBEKEND')          as ITEM_CODE
,         isnull(i.GROEP_ZORGVORM,'ONBEKEND')     as ZORGVORM
,         t.tarief
-- lookup calculaties
,         RealisatieIsAfspraak
,         FactProductie
,         ProductieGroep
,         AfspraakVerekenenMetRealisatieVan
,         CALC_REALISATIE_AANTAL                                                                                                
,         CALC_REALISATIE_EUROS                                                                                                 
,         CALC_AFSPRAAK_AANTAL                                                                                                  
,         CALC_AFSPRAAK_EUROS                                                                                                   
,         CALC_TARIEF
,         BEDBEZETTING_PERC
,         SemiAdditieveMeetwaarde_Tijd
,         CALC_REALISATIE_AANTAL_SAMTIJD
,         CALC_REALISATIE_EUROS_SAMTIJD                                                                                                 
,         CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                  
,         CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                   
,         CALC_TARIEF_SAMTIJD
,         a.AFSPRAAK
,         case
            when CALC_AFSPRAAK_AANTAL   = 'AFSPRAAK_AANTAL'                                 then afspraak
            else NULL
          end as AFSPRAAK_AANTAL
,         case
            when CALC_AFSPRAAK_EUROS    = 'AFSPRAAK_AANTAL X TARIEF'                        then afspraak * tarief
            when CALC_AFSPRAAK_EUROS    = 'AFSPRAAK_AANTAL X TARIEF_PER_MAAND'              then afspraak * (tarief/12)
            else NULL
          end as AFSPRAAK_EUROS
,         case
            when CALC_AFSPRAAK_AANTAL_SAMTIJD   = 'AFSPRAAK_AANTAL'                         then afspraak 
            else NULL
          end as AFSPRAAK_AANTAL_SAMTIJD
from      XMCARE_IMP.IMP_PRODAFSPR       a
-- lookup van de murale met afspraak item code om zo de financieringsvorm te kunnen bepalen.
left join XMCARE_STG.STG_productie_items i
on        a.rapportage_item = i.item_code
-- lookup van de financiering mbv afspraak financier en murale
left join XMCARE_IMP.IMP_GROEP_FINANCIERINGSVORMEN     fin
on        a.financiering =  fin.financiering
and       (fin.murale is null or i.murale   =  fin.murale)
-- lookup van de tarieven (tarief wordt uniek geidentificeerd door item_code, jaar en financiering)
left join xmcare_stg.stg_productie_tarieven as t
on        a.rapportage_item                   = t.item_code
and       convert(integer,left(JAAR_MAAND,4)) = t.jaar      
and       i.financiering_id                   = t.financiering_id
-- lookup van de kostenplaats (in het geval van een onbekende kostenplaats wil je een -1)
left join inforay_dwh.dbo.axi_cat_kostenplaatsstructuur  kpl
on        a.kostenplaats = kpl.kstpl_code
'''
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)

    def test_statement2(self):
        '''test_statement2'''
        self.printStartBanner()
        statement          = '''
create view [XMCARE_STG].[STG_PRODUCTIE_REALISATIE_VW]
as 
select    *
,         case
            when CALC_REALISATIE_AANTAL         = 'REALISATIE_AANTAL'                     then aantal
            else NULL
          end as REALISATIE_AANTAL
,         case
            when CALC_REALISATIE_EUROS          = 'REALISATIE_AANTAL X TARIEF'            then aantal * tarief
            when CALC_REALISATIE_EUROS          = 'REALISATIE_AANTAL X TARIEF_PER_MAAND'  then aantal * (12.0/52.0) * tarief/12
            when CALC_REALISATIE_EUROS          = 'AFSPRAAK_AANTAL X TARIEF_PER_MAAND'    then afspraak * tarief/12
            when CALC_REALISATIE_EUROS          = 'AFSPRAAK_AANTAL X TARIEF'              then afspraak * tarief
            else NULL
          end as REALISATIE_EUROS
,         case
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'UREN_OPENSTEL_GEM_PER_WK_VANAF_JAN'    then RealisatieGemiddeldOverLopendeJaar * (12.0/52.0)  -- .0 omdat SQL Server het getal interpreteert als integer en er dan 0 als uitkomst komt vreemd genoeg.
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'GEM_BB_PER_DAG_MET_BB_PERC_CORRECTIE'  then RealisatieGemiddeldOverLopendeJaar / (BEDBEZETTING_PERC / 100.0) / (day(dateadd(mm,datediff(mm,-1,cast( MAAND_VERANTWOORDING as varchar(6)) + '01'),-1)))
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'AFSPRAAK_AANTAL'                       then afspraak
            else NULL
          end as REALISATIE_AANTAL_SAMTIJD
,         (day(dateadd(mm,datediff(mm,-1,cast( MAAND_VERANTWOORDING as varchar(6)) + '01'),-1))) dagen_in_maand
from (select    prd.BRON                                                               
      ,         prd.NR_RUN                                                                     
      ,         prd.BOEK_PER                                                                                                               
      ,         prd.PROD_PER                                                                                                               
      ,         convert(varchar(1024),isnull(kpl.kstpl_code,-1)) as KOSTENPLAATS           
      ,         prd.C_CATEGORIE                                                                   
      ,         prd.C_PROJECT                                                                                                              
      ,         prd.OPN1                                                                                                                   
      ,         prd.C_BETAAL_INSTANTIE                                                                                                     
      ,         prd.AANTAL                                                                                                                 
      ,         prd.AFSPRAAK                                                                   
      ,         prd.RealisatieCummulatiefOverLopendeJaar                                       
      ,         prd.RealisatieGemiddeldOverLopendeJaar                                         
      ,         prd.BEDRAG                                                                                             
      ,         prd.FINANCIERING                                                               
      ,         prd.MAAND_VERANTWOORDING                                                       
      ,         prd.ITEM_CODE                                                                  
      ,         prd.ZORGVORM                                                                   
      ,         prd.RealisatieIsAfspraak                                                       
      ,         prd.FactProductie                                                              
      ,         prd.ProductieGroep
      ,         prd.CALC_REALISATIE_AANTAL                                                     
      ,         prd.CALC_REALISATIE_EUROS                                                                                                                       
      ,         prd.CALC_AFSPRAAK_AANTAL                                                                                                                        
      ,         prd.CALC_AFSPRAAK_EUROS                                                                                                                         
      ,         prd.CALC_TARIEF                                                                                                                                 
      ,         prd.BEDBEZETTING_PERC                                                          
      ,         prd.SemiAdditieveMeetwaarde_Tijd                                               
      ,         prd.CALC_REALISATIE_AANTAL_SAMTIJD                                             
      ,         prd.CALC_REALISATIE_EUROS_SAMTIJD                                                                                                                       
      ,         prd.CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                                        
      ,         prd.CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                                         
      ,         prd.CALC_TARIEF_SAMTIJD
      ,         fin.financiering_id  
      ,         tar.tarief  
      from      (select    [BRON]       
                 ,         [NR_RUN]                                                                                                      
                 ,         [BOEK_PER]                                                                                                    
                 ,         [PROD_PER]     
                 -- -1 is key voor onbekend record. Converteer kostenplaats naar string om conversieproblemen te voorkomen.   
                 ,         convert(varchar(1024),isnull([KOSTENPLAATS],-1)) as [KOSTENPLAATS]   
                 ,         [C_CATEGORIE]                                                                                                 
                 ,         [C_PROJECT]                                                                                                   
                 ,         [OPN1]                                                                                                        
                 ,         [C_BETAAL_INSTANTIE]                                                                                          
                 ,         [AANTAL]   
                 ,         null as [AFSPRAAK]          
                 ,         RealisatieCummulatiefOverLopendeJaar  
                 ,         RealisatieGemiddeldOverLopendeJaar                                                      
                 ,         [BEDRAG]   
                 -- bepaling van financiering volgens definitie                                                                          
                 ,         case                                                                                                          
                             when c_betaal_instantie is null         then isnull(groep_financiering,'ONBEKEND')  
                             when c_betaal_instantie = 'FPZ'         then 'FPZ'                                                          
                             when c_betaal_instantie = 'RW-WISSEL'   then 'ROOIJSEWISSEL'                                                
                             when c_betaal_instantie = 'ZRADELFT'    then 'ZRA'                                                          
                             when c_betaal_instantie = 'ZORGKANT'    then isnull(groep_financiering,'ONBEKEND')  
                             else                                           'OVERIGE'                                                    
                           end as FINANCIERING         
                 -- bepaling van verantwoordingsperiode volgens definitie                                                                
                 ,         case                                                                                                          
                             when groep_financiering = 'ZVW'   
                               then BOEK_PER                                                                           
                             else   PROD_PER                                                                           
                           end                                                  as MAAND_VERANTWOORDING     
                 -- lookup item attributen 
                 ,         isnull(i.item_code,'ONBEKEND')            as ITEM_CODE  
                 ,         isnull(i.groep_zorgvorm,'ONBEKEND')       as ZORGVORM
                 ,         i.RealisatieIsAfspraak
                 ,         i.FactProductie
                 ,         i.ProductieGroep
                 ,         i.CALC_REALISATIE_AANTAL                                                                                                           
                 ,         i.CALC_REALISATIE_EUROS                                                                                                            
                 ,         i.CALC_AFSPRAAK_AANTAL                                                                                                             
                 ,         i.CALC_AFSPRAAK_EUROS                                                                                                              
                 ,         i.CALC_TARIEF           
                 ,         i.BEDBEZETTING_PERC
                 ,         i.SemiAdditieveMeetwaarde_Tijd
                 ,         i.CALC_REALISATIE_AANTAL_SAMTIJD                                                                                                           
                 ,         i.CALC_REALISATIE_EUROS_SAMTIJD                                                                                                            
                 ,         i.CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                             
                 ,         i.CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                              
                 ,         i.CALC_TARIEF_SAMTIJD           
                 from      XMCARE_STG.STG_PRODUCTIE_REALISATIE_SRC                                p
                 -- lookup van de item attributen mbv. item_code  
                 join      XMCARE_STG.STG_PRODUCTIE_ITEMS                                         i  -- geen left join omdat er anders allemaal onbekende items/financiers etc. in de rapportage komen.
                 on        p.item_code    =  i.item_code                        
                )                                                                                 prd             
      -- lookup van de financiering mbv. murale. lookup via UK, wordt automatisch getest  
      left join XMCARE_IMP.IMP_GROEP_ZORGVORMEN                                                   zvm  
      on        prd.zorgvorm     =  zvm.zorgvorm                        
      -- lookup via UK, wordt automatisch getest  
      left join XMCARE_IMP.IMP_GROEP_FINANCIERINGSVORMEN                                          fin  
      on        prd.financiering =  fin.financiering                    
      and       (fin.murale is null or zvm.murale      =  fin.murale)  
      -- lookup van de tarieven via UK item_code, jaar en financiering, wordt automatisch getest  
      left join xmcare_stg.stg_productie_tarieven as                                              tar  
      on        prd.item_code                                 = tar.item_code  
      and       convert(integer,left(MAAND_VERANTWOORDING,4)) = tar.jaar        
      and       fin.financiering_id                           = tar.financiering_id  
      -- lookup van de kostenplaats (in het geval van een onbekende kostenplaats wil je een -1)
      left join inforay_dwh.dbo.axi_cat_kostenplaatsstructuur  kpl
      on        prd.kostenplaats = kpl.kstpl_code
        union ALL
      SELECT [bron]
      ,-1            rn
      ,[JAAR_MAAND]  jm1
      ,[JAAR_MAAND]  jm2
      ,[KOSTENPLAATS]
      ,cast(null as varchar(1024)) 
      ,cast(null as varchar(1024)) 
      ,cast(null as varchar(1024)) 
      ,cast(null as varchar(1024)) 
      ,cast(null as float)         
      ,AFSPRAAK
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as varchar(1024)) 
      ,[JAAR_MAAND]
      ,[ITEM_CODE]
      ,[ZORGVORM]
      ,[RealisatieIsAfspraak]
      ,[FactProductie]
      ,[ProductieGroep]
      ,[CALC_REALISATIE_AANTAL]
      ,[CALC_REALISATIE_EUROS]
      ,[CALC_AFSPRAAK_AANTAL]
      ,[CALC_AFSPRAAK_EUROS]
      ,[CALC_TARIEF]
      ,[BEDBEZETTING_PERC]
      ,[SemiAdditieveMeetwaarde_Tijd]
      ,[CALC_REALISATIE_AANTAL_SAMTIJD]
      ,[CALC_REALISATIE_EUROS_SAMTIJD]
      ,[CALC_AFSPRAAK_AANTAL_SAMTIJD]
      ,[CALC_AFSPRAAK_EUROS_SAMTIJD]
      ,[CALC_TARIEF_SAMTIJD]
      ,[financiering_id]
      ,[tarief]
      FROM [XMCARE_SRC].[XMCARE_STG].[STG_PRODUCTIE_AFSPRAKEN]
      WHERE [RealisatieIsAfspraak] = 1
        union ALL
      SELECT         [BRON]
      ,-1            [NR_RUN]
      ,[JAAR_MAAND]  [BOEK_PER]
      ,[JAAR_MAAND]  [PROD_PER]
      ,[KOSTENPLAATS]
      ,cast(null as varchar(1024))  [C_CATEGORIE]
      ,cast(null as varchar(1024))  [C_PROJECT]
      ,cast(null as varchar(1024))  [OPN1]
      ,cast(null as varchar(1024))  [C_BETAAL_INSTANTIE]
      ,AFSPRAAK                     [AANTAL] 
      ,cast(null as float)          [AFSPRAAK]
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as varchar(1024)) 
      ,[JAAR_MAAND]
      ,[ITEM_CODE]
      ,[ZORGVORM]
      ,[RealisatieIsAfspraak]
      ,[FactProductie]
      ,[ProductieGroep]
      ,[CALC_REALISATIE_AANTAL]
      ,[CALC_REALISATIE_EUROS]
      ,[CALC_AFSPRAAK_AANTAL]
      ,[CALC_AFSPRAAK_EUROS]
      ,[CALC_TARIEF]
      ,[BEDBEZETTING_PERC]
      ,[SemiAdditieveMeetwaarde_Tijd]
      ,[CALC_REALISATIE_AANTAL_SAMTIJD]
      ,[CALC_REALISATIE_EUROS_SAMTIJD]
      ,[CALC_AFSPRAAK_AANTAL_SAMTIJD]
      ,[CALC_AFSPRAAK_EUROS_SAMTIJD]
      ,[CALC_TARIEF_SAMTIJD]
      ,[financiering_id]
      ,[tarief]
      FROM [XMCARE_SRC].[XMCARE_STG].[STG_PRODUCTIE_AFSPRAKEN]
      WHERE [AfspraakVerekenenMetRealisatieVan] is not null
        union ALL
      SELECT         [BRON]
      ,-1            [NR_RUN]
      ,[JAAR_MAAND]  [BOEK_PER]
      ,[JAAR_MAAND]  [PROD_PER]
      ,[KOSTENPLAATS]
      ,cast(null as varchar(1024))  [C_CATEGORIE]
      ,cast(null as varchar(1024))  [C_PROJECT]
      ,cast(null as varchar(1024))  [OPN1]
      ,cast(null as varchar(1024))  [C_BETAAL_INSTANTIE]
      ,-AFSPRAAK                     [AANTAL]             -- negatieve afspraak
      ,cast(null as float)          [AFSPRAAK]
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as float)         
      ,cast(null as varchar(1024)) 
      ,[JAAR_MAAND]
      ,[ITEM_CODE]
      ,[ZORGVORM]
      ,[RealisatieIsAfspraak]
      ,[FactProductie]
      ,[ProductieGroep]
      ,[CALC_REALISATIE_AANTAL]
      ,[CALC_REALISATIE_EUROS]
      ,[CALC_AFSPRAAK_AANTAL]
      ,[CALC_AFSPRAAK_EUROS]
      ,[CALC_TARIEF]
      ,[BEDBEZETTING_PERC]
      ,[SemiAdditieveMeetwaarde_Tijd]
      ,[CALC_REALISATIE_AANTAL_SAMTIJD]
      ,[CALC_REALISATIE_EUROS_SAMTIJD]
      ,[CALC_AFSPRAAK_AANTAL_SAMTIJD]
      ,[CALC_AFSPRAAK_EUROS_SAMTIJD]
      ,[CALC_TARIEF_SAMTIJD]
      ,[AfspraakVerekenenMetRealisatieVan]  -- verrekenen met financier
      ,[tarief]
      FROM [XMCARE_SRC].[XMCARE_STG].[STG_PRODUCTIE_AFSPRAKEN]
      WHERE [AfspraakVerekenenMetRealisatieVan] is not null
      ) q
'''

        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)

    def test_statement3(self):
        '''test_statement1'''
        self.printStartBanner()
        statement          = '''
create view [XMCARE_STG].[STG_PRODUCTIE_REALISATIE_VW]
as 
select    *
,         case
            when CALC_REALISATIE_AANTAL         = 'REALISATIE_AANTAL'                     then aantal
            else NULL
          end as REALISATIE_AANTAL
,         case
            when CALC_REALISATIE_EUROS          = 'REALISATIE_AANTAL X TARIEF'            then aantal * tarief
            when CALC_REALISATIE_EUROS          = 'REALISATIE_AANTAL X TARIEF_PER_MAAND'  then aantal * (12.0/52.0) * tarief/12
            when CALC_REALISATIE_EUROS          = 'AFSPRAAK_AANTAL X TARIEF_PER_MAAND'    then afspraak * tarief/12
            when CALC_REALISATIE_EUROS          = 'AFSPRAAK_AANTAL X TARIEF'              then afspraak * tarief
            else NULL
          end as REALISATIE_EUROS
,         case
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'UREN_OPENSTEL_GEM_PER_WK_VANAF_JAN'    then RealisatieGemiddeldOverLopendeJaar * (12.0/52.0)  -- .0 omdat SQL Server het getal interpreteert als integer en er dan 0 als uitkomst komt vreemd genoeg.
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'GEM_BB_PER_DAG_MET_BB_PERC_CORRECTIE'  then RealisatieGemiddeldOverLopendeJaar / (BEDBEZETTING_PERC / 100.0) / (day(dateadd(mm,datediff(mm,-1,cast( MAAND_VERANTWOORDING as varchar(6)) + '01'),-1)))
            when CALC_REALISATIE_AANTAL_SAMTIJD = 'AFSPRAAK_AANTAL'                       then afspraak
            else NULL
          end as REALISATIE_AANTAL_SAMTIJD
,         (day(dateadd(mm,datediff(mm,-1,cast( MAAND_VERANTWOORDING as varchar(6)) + '01'),-1))) dagen_in_maand
from (select    prd.BRON                                                               
      ,         prd.NR_RUN                                                                     
      ,         prd.BOEK_PER                                                                                                               
      ,         prd.PROD_PER                                                                                                               
      ,         convert(varchar(1024),isnull(kpl.kstpl_code,-1)) as KOSTENPLAATS           
      ,         prd.C_CATEGORIE                                                                   
      ,         prd.C_PROJECT                                                                                                              
      ,         prd.OPN1                                                                                                                   
      ,         prd.C_BETAAL_INSTANTIE                                                                                                     
      ,         prd.AANTAL                                                                                                                 
      ,         prd.AFSPRAAK                                                                   
      ,         prd.RealisatieCummulatiefOverLopendeJaar                                       
      ,         prd.RealisatieGemiddeldOverLopendeJaar                                         
      ,         prd.BEDRAG                                                                                             
      ,         prd.FINANCIERING                                                               
      ,         prd.MAAND_VERANTWOORDING                                                       
      ,         prd.ITEM_CODE                                                                  
      ,         prd.ZORGVORM                                                                   
      ,         prd.RealisatieIsAfspraak                                                       
      ,         prd.FactProductie                                                              
      ,         prd.ProductieGroep
      ,         prd.CALC_REALISATIE_AANTAL                                                     
      ,         prd.CALC_REALISATIE_EUROS                                                                                                                       
      ,         prd.CALC_AFSPRAAK_AANTAL                                                                                                                        
      ,         prd.CALC_AFSPRAAK_EUROS                                                                                                                         
      ,         prd.CALC_TARIEF                                                                                                                                 
      ,         prd.BEDBEZETTING_PERC                                                          
      ,         prd.SemiAdditieveMeetwaarde_Tijd                                               
      ,         prd.CALC_REALISATIE_AANTAL_SAMTIJD                                             
      ,         prd.CALC_REALISATIE_EUROS_SAMTIJD                                                                                                                       
      ,         prd.CALC_AFSPRAAK_AANTAL_SAMTIJD                                                                                                                        
      ,         prd.CALC_AFSPRAAK_EUROS_SAMTIJD                                                                                                                         
      ,         prd.CALC_TARIEF_SAMTIJD
      ,         fin.financiering_id  
      ,         tar.tarief  
      from      (select    case                                                                                                          
                             when c_betaal_instantie is null         then isnull(groep_financiering,'ONBEKEND')  
                             when c_betaal_instantie = 'FPZ'         then 'FPZ'                                                          
                             when c_betaal_instantie = 'RW-WISSEL'   then 'ROOIJSEWISSEL'                                                
                             when c_betaal_instantie = 'ZRADELFT'    then 'ZRA'                                                          
                             when c_betaal_instantie = 'ZORGKANT'    then isnull(groep_financiering,'ONBEKEND')  
                             else                                           'OVERIGE'                                                    
                           end as FINANCIERING         
                )                                                                                 prd             
      ) q
'''
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
    #def suite(self):
    #    #suite = unittest.TestLoader().loadTestsFromTestCase(TestPlySql)
    #    suite = unittest.Testsuite()
    #    suite.addTest(TestPlySql('test case'))

    #def tearDown(self):
    #    self.lexer = None
    #    self.parser = None

