import sys   
import re    

import ply.lex as lex    

tokens = [
    'TOKEN_FUNCTION',
    'TOKEN_RULE',
    'GRAMMAR_RULE',
    'GRAMMAR_SPEC',
    'CLASS_SPEC'
]

def t_TOKEN_FUNCTION(t):
    r'def[ \t]+t_[^\(]*'
    return t

def t_TOKEN_RULE(t):
    r'^[ \t]*r\'.*\''
    return t

def t_GRAMMAR_SPEC(t):
    r'\'{3}.*?\:(.|\n)*?\'{3}'
    return t

def t_CLASS_SPEC(t):
    r'class[ /t].+?[^:]*'
    return t
    
def t_error(t):    
    #print "?:%s" % t.value[0]    
    t.lexer.skip(1)    

class PlySqlReference():
    def showReference(self):
        self.lexer = lex.lex(reflags = re.MULTILINE)    
        
        self.filename='plysql_token_rules.py'
        print
        print '- ' + self.filename + '  -----------------------------------------'
        self.lexer.input(open(self.filename,'r').read())    
        for tok in self.lexer:    
            if tok.type == 'TOKEN_FUNCTION':
                str = tok.value.replace("def","").replace("t_","")
            elif tok.type == 'TOKEN_RULE':
                print str.rjust(20) + ' : ' + tok.value[5:]
        
        self.filename='plysql_grammar_rules.py'
        print
        print '- ' + self.filename + '  -----------------------------------------'
        self.lexer.input(open(self.filename,'r').read())    
        for tok in self.lexer:    
            if tok.type == 'GRAMMAR_SPEC':
                print '       ' + tok.value.replace("'","")
        
        self.filename='plysql_classes.py'
        print
        print '- ' + self.filename + '  -----------------------------------------'
        self.lexer.input(open(self.filename,'r').read())    
        for tok in self.lexer:    
            if tok.type == 'CLASS_SPEC':
                print tok.value.replace("'"," ")

        self.filename='plysql_grammar_rules.py'
        print
        print '- ' + self.filename + '  -----------------------------------------'
        self.lexer.input(open(self.filename,'r').read())    
        for tok in self.lexer:    
            if tok.type == 'CLASS_SPEC':
                print tok.value.replace("'"," ")
