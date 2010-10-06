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
        if result != None:
            result.debugMsg(result.getSyntaxStructure(),-1)
            result.showMetadata()
        
        return result   
    def printStartBanner(self):
        print banner(sys._getframe(1).f_code.co_name,'#')
        
    def compareMetadata(self,p_metadata,p_refMetadata=''):
        for k, v in p_metadata.iteritems():
            if v != []:
                self.assertEqual(v,p_refMetadata[k])
 
        for k, v in p_refMetadata.iteritems():
            self.assertEqual(v,p_metadata[k])

    def test_case(self):
        '''test case '''
        self.printStartBanner()
        statement          = '''select case when x=y then z else 25  end '''
        refSyntaxStructure = ['select', ['case', [[['when', ['x', '=', 'y']], 'then', 'z'], 'else', '25'], 'end']]
        refMetadata    = dict(literal_all          = ['25']
                                 ,mappings_column      = [('x', 'x'), ('y', 'y'), ('z', 'z')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        #self.compareMetadata(result.getMetadata(),refMetadata)

    def test_cast_2(self):
        '''test cast 2'''
        self.printStartBanner()
        statement          = '''select cast(null as varchar(1024))'''
        refSyntaxStructure = ['select', ['cast', ['(', ['null', 'as', 'float'], ')']]]
        refMetadata    = dict(name_all        = ['cast','float']
                                 ,names_function  = ['cast']
                                 ,literal_all     = ['null']
                                 ,mappings_column = []
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_cast_1(self):
        '''test cast 1'''
        self.printStartBanner()
        statement          = '''select cast(null as float)'''
        refSyntaxStructure = ['select', ['cast', ['(', ['null', 'as', 'float'], ')']]]
        refMetadata    = dict(literal_all          = ['null']
                                 ,mappings_cast        = [('null', 'float')]

                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_and_or_1(self):
        '''test and or 1'''
        self.printStartBanner()
        statement          = '''where x=y and z=z'''
        refSyntaxStructure = ['where', [['x', '=', 'y'], 'and', ['z', '=', 'z']]]
        refMetadata    = dict(mappings_column      = [('x', 'x'), ('y', 'y'), ('z', 'z'), ('z', 'z')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_reserved_words(self):
        '''test and or 2'''
        self.printStartBanner()
        statement          = '''select andx, orx, integer'''
        #refSyntaxStructure = ['select', ['andx', ',', 'orx'',', 'integer']]
        #refMetadata    = dict(name_all       = ['andx','orx','integer']
        #                         ,names_column   = ['andx','orx','integer']
        #                         )
        #
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        #self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        #self.compareMetadata(result.getMetadata(),refMetadata)

    def test_is_null(self):
        '''test is null'''
        self.printStartBanner()
        statement          = '''where x is null'''
        refSyntaxStructure = ['where', ['x', 'is', 'null']]
        refMetadata    = dict(mappings_column  = [('x', 'x')]
                                 ,literal_all      = ['null']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_star_dot_1(self):
        '''test star dot 1'''
        self.printStartBanner()
        statement          = '''select t1.*'''
        refSyntaxStructure = ['select', ['t1', '.', '*']]
        refMetadata    = dict(mappings_column      = [('t1.*', 't1.*')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_star_dot_2(self):
        '''test star dot 2'''
        self.printStartBanner()
        statement          = '''select 1 * 2 as c1'''
        refSyntaxStructure = ['select', [['1', '*', '2'], 'as', 'c1']]
        refMetadata    = dict(literal_all          = ['1', '2']
                                 ,mappings_column      = [('1 * 2', 'c1')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_star_dot_3(self):
        '''test star dot 3'''
        self.printStartBanner()
        statement          = '''select pack.func(t1.x)'''
        refSyntaxStructure = ['select', [['pack', '.', 'func'], ['(', ['t1', '.', 'x'], ')']]]
        refMetadata    = dict(mappings_column      = [('t1.x', 't1.x')]
                                 ,mappings_function    = [('pack.func', 'pack.func')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_star_dot_4(self):
        '''test star dot 4'''
        self.printStartBanner()
        statement          = '''select t1.*, 1 * 2 as c1, pack.func(t1.x)'''
        refSyntaxStructure = ['select', [[['t1', '.', '*'], ',', [['1', '*', '2'], 'as', 'c1']], ',', [['pack', '.', 'func'], ['(', ['t1', '.', 'x'], ')']]]]
        refMetadata    = dict(literal_all          = ['1', '2']
                                 ,mappings_column      = [('t1.*', 't1.*'), ('1 * 2', 'c1'), ('t1.x', 't1.x')]
                                 ,mappings_function    = [('pack.func', 'pack.func')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_star_dot_5(self):
        '''test star dot 5'''
        self.printStartBanner()
        statement          = '''select c1 * c2'''
        refSyntaxStructure = ['select', ['c1', '*', 'c2']]
        refMetadata    = dict(mappings_column      = [('c1', 'c1'), ('c2', 'c2')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_star_dot_6(self):
        '''test star dot 6'''
        self.printStartBanner()
        statement          = '''select c1 * 5'''
        refSyntaxStructure = ['select', ['c1', '*', '5']]
        refMetadata    = dict(literal_all          = ['5']
                                 ,mappings_column      = [('c1', 'c1')]
                                 )
       
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_partition_by_1(self):
        '''partition by 1'''
        self.printStartBanner()
        statement          = '''select sum(x) over (partition by y order by z)'''
        refSyntaxStructure = ['select', [['sum', ['(', 'x', ')']], 'over', ['(', [['partition by', 'y'], ['order by', 'z']], ')']]]
        refMetadata    = dict(mappings_column      = [('y', 'y'), ('z', 'z'), ('x', 'x')]
                                 ,mappings_function    = [('sum', 'sum')]
                                 )

        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_partition_by_2(self):
        '''partition by 2'''
        self.printStartBanner()
        statement          = '''select sum(x) over (partition by y)'''
        refSyntaxStructure = ['select', [['sum', ['(', 'x', ')']], 'over', ['(', ['partition by', 'y'], ')']]]
        refMetadata    = dict(mappings_column      = [('y', 'y'), ('x', 'x')]
                                 ,mappings_function    = [('sum', 'sum')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_view_1(self):
        '''view test'''
        self.printStartBanner()
        statement          = '''create view v as select * from dual;'''
        refSyntaxStructure = ['create', 'view', ['v', 'as', [['select', '*'], ['from', 'dual']]]]
        refMetadata    = dict(mappings_column      = [('*', '*')]
                                 ,mappings_table       = [('dual', 'dual')]
                                 ,mappings_view        = [('v', 'select * from dual')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)
 
    def test_join_1(self):
        '''join test'''
        self.printStartBanner()
        statement          = '''join table2 t2 on t1.x = t2.x'''
        refSyntaxStructure = ['join', ['table2', 't2'], 'on', [['t1', '.', 'x'], '=', ['t2', '.', 'x']]]
        refMetadata    = dict(mappings_column   = [('t1.x', 't1.x'), ('t2.x', 't2.x')]
                                 ,mappings_table    = [('table2', 't2')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_function_1(self):
        '''function test'''
        self.printStartBanner()
        statement          = '''select substr(x,1,2)'''
        refSyntaxStructure = ['select', ['substr', ['(', [['x', ',', '1'], ',', '2'], ')']]]
        refMetadata    = dict(mappings_column   = [('x', 'x')]
                                 ,mappings_function = [('substr', 'substr')]
                                 ,literal_all       = ['1','2']
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_alias_1(self):
        '''alias test from tables'''
        self.printStartBanner()
        statement          = '''from c1 as C1'''
        refSyntaxStructure = ['from', ['c1', 'as', 'C1']]
        refMetadata    = dict(mappings_table  = [('c1','C1')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_alias_2(self):
        '''aliases test select columns'''
        self.printStartBanner()
        statement          = '''from c1 C1'''
        refSyntaxStructure = ['from', ['c1', 'C1']]
        refMetadata    = dict(mappings_table  = [('c1','C1')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_alias_3(self):
        '''aliases test with'''
        self.printStartBanner()
        statement          = '''with w as (select c1)'''
        refSyntaxStructure = ['with', ['w', 'as', ['(', ['select', 'c1'], ')']]]
        refMetadata    = dict(mappings_column = [('c1', 'c1')]
                                 ,mappings_with   = [('w','( select c1 )')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

    def test_1(self):
        '''simple sql test'''
        self.printStartBanner()
        statement          = '''select c1 from t1'''
        refSyntaxStructure = [['select', 'c1'], ['from', 't1']]
        refMetadata    = dict(mappings_column   = [('c1','c1')]
                                 ,mappings_table    = [('t1','t1')]
                                 )
        
        result             = self.parseStatement(statement)
        self.assertNotEqual(result,None)
        self.assertEqual(result.getSyntaxStructure(),refSyntaxStructure)
        self.compareMetadata(result.getMetadata(),refMetadata)

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

def tearDown(self):
        self.lexer = None
        self.parser = None
        
unittest.main()
