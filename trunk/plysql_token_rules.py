token_lookup = {    
    'CREATE':       'CREATE',          
    'VIEW':         'VIEW',          
    'AS':           'AS',       
    'WITH':         'WITH',          
    'SELECT':       'SELECT',       
    'FROM':         'FROM',    
    'ON':           'ON',    
    'USING':        'USING',    
    'WHERE':        'WHERE',    
    'NOT':          'NOT',    
    'ASC':          'ASC',    
    'DESC':         'DESC',    
    'HAVING':       'HAVING',    
    '(':            'PARENT_L',    
    ')':            'PARENT_R',    
    ',':            'COMMA',    
    '*':            'STAR',    
    'DISTINCT':     'DISTINCT',    
    'UNIQUE':       'UNIQUE',    
    'ALL':          'ALL',    
    'NULL':         'NULL',    
    'AND':          'LOG_OPERATOR',    
    'OR':           'LOG_OPERATOR',    
    'IN':           'OPERATOR',    
    'OVER':         'OPERATOR',    
    'IS':           'OPERATOR',    
}    
    
tokens = [    
    'STRING',    
    'IDENTIFIER',    
    'NUMBER',    
    'GROUP_BY',    
    'ORDER_BY',    
    'SET_OPERATOR',    
    'LOG_OPERATOR',
    'OPERATOR',    
    'JOIN_OPERATOR',
    'PLUS_MINUS',
    'PARTITION_BY',
    'DOT',    
] + list(token_lookup.values()) 

'''The sequence of the tokens rules is as follows
    - first the multiline tokens
    - tokens that can be ignored
    - other tokens
    
    1. Comment is ignored
    2. String literals is multiline 
    3. whitespace is ignored
    4. Separotors GO and semicolon ; ignored
    5. new line is ignored
    6. Number
    7. special characters (,) and *
    8. Some common reserved words like GROUP BY. JOIN, HAVING etc.
    9. set, logical and other operators
   10. identifiers and unknown reserved words
'''
    
'''matches /* ... */ or --... and does nothing with it.
/\*       -> matches /* 
 (.|\n)*? -> matches 0 or more characters or newlines, but lazy (until the next match)
 (--.*)   -> matches -- and everything after it
'''
def t_COMMENT(t):    
    r'(/\*(.|\n)*?\*/)|(--.*)'    
    pass
    

'''matches n'...' q'...' nq'...'

n?q?            -> may start with n q
(.|\n)*?        -> matches 0 or more characters or newlines, but lazy (until the next match)
\'              -> matches a quote '
(\'(.|\n)*?\')  -> matches '...'
              + -> matches '...''...' etc. This way double qoutes are included in the string  

References:
Oracle text literals: http://download.oracle.com/docs/cd/E11882_01/server.112/e17118/sql_elements003.htm#i42617
Microsoft Constants : http://msdn.microsoft.com/en-us/library/ms179899.aspx

MS Sql Server. If SET QUOTED_IDENTIFIER is OFF the double qoutes "" can be used for qouting strings too. 
However this parser does not support it.
'''
def t_STRING(t):    
    r'n?q?(\'(.|\n)*?\')+'
    return t    

'''matches tabs and spaces and does nothing with them'''    
def t_WHITESPACE(t):    
    r'[ \t]+'    
    pass    

'''matches GO and ; and does nothing with them
We only want the GO command in MS Sql Server but not a table or column with the GO in Oracle.
\n[ \t]*GO[ \t]*\n -> Matches the GO command that is the only token on a single line. 
\;                 -> a ; 
'''    
def t_SEPARATOR(t):    
    r'\n[ \t]*GO[ \t]*\n|\;'    
    pass

'''matches a new line and does nothing with it.'''
def t_NEW_LINE(t):    
    r'[\n]+'    
    pass    

'''Matches number datatypes ( including money, signtific notation, binary constant)
minus               -> is handled as a unaray operator
\$?                 -> $ for money datatype
[0-9\.]             -> matches a number or dot. Numbers must start with it.
[0-9\.xabcdf]*      -> matches a number, plus, minus dot. E for signtific notation. F,d are float and double indicator in Oracle. xabcdef are used in binary constant
(e[\+\-][0-9]*)?    -> optional exponent of scientific number 
Oracle numeric literals: http://download.oracle.com/docs/cd/E11882_01/server.112/e17118/sql_elements003.htm#i139891
Microsoft Constants :    http://msdn.microsoft.com/en-us/library/ms179899.aspx
'''    
def t_NUMBER(t):    
    r'([0-9]|\.[0-9]|\$[0-9]|0x)[0-9\.abcdef]*(e[\+\-]?[0-9]*)?[fd]?'    
    return t    

'''
matches some special characters: , ( ) * 
These are looked up in the token_lookup list.
Complex commands like GROUP BY and ORDER BY cannot be looked up because they can differ in their whitspace.
'''
def t_SPECIAL_CHARACTERS(t):    
    r'[\,\(\)\*]'    
    t.type = token_lookup.get(t.value.upper())    
    return t    

'''Matches GROUP BY'''    
def t_GROUP_BY(t):    
    r'GROUP[ \t\n]+BY'    
    return t    
        
'''Matches ORDER BY'''    
def t_ORDER_BY(t):    
    r'ORDER[\ \t\n]+BY'    
    return t    

'''Matches the join operators'''    
def t_JOIN_OPERATOR(t):
    r'(NATURAL[ \t\n]+)?(FULL[ \t\n]+|LEFT[ \t\n]+|RIGHT[ \t\n]+)?(OUTER[ \t\n]+|INNER[ \t\n]+|CROSS[ \t\n]+)?JOIN'
    return t
    
'''Matches the set operators'''    
def t_SET_OPERATOR(t):    
    r'UNION[\ \t\n]+ALL|UNION|MINUS|INTERSECT|EXCEPT'    
    return t    

'''Matches the numeric, character and comparison operators. Some operators like >= contain more than one characters.'''    
def t_OPERATOR(t):    
    r'[\/\^\|\=\<\>\!]+'
    return t    
    
def t_PLUS_MINUS(t):    
    r'[\+\-]'
    return t    

def t_PARTITION_BY(t):    
    r'PARTITION[ \t]BY'    
    return t    

''' Matches identifiers and reserved words
If a match is found a lookup is done to check if it is a reserved word. Otherwise it is an IDENTIFIER.
MS Sql Server [] are also allowed.    
[\"\[]?                 -> a word can start or end with " or [
[a-zA-Z]                -> first character must be an alphabettical character.
[a-zA-Z0-9\_\$\#\@]*  -> other characters can be alphanumerical or _ $ # . @
'''
def t_WORDS(t):    
    r'[\"\[]?[a-zA-Z][a-zA-Z0-9\_\$\#\@]*[\"\]]?'    
    t.type = token_lookup.get(t.value.upper(),'IDENTIFIER')    
    return t    

def t_DOT(t):
    r'\.'
    return t    

def t_error(t):    
    #print "?:%s" % t.value[0]    
    t.lexer.skip(1)    
