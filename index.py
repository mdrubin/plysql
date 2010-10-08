'''
t1.* levert geen t1.* kolom op.
'''


import sys
import re

import cgi

import ply.lex as lex    
import ply.yacc as yacc    

import plysql_token_rules    
import plysql_grammar_rules

from plysql_classes import banner
from plysql_classes import Node

import plysql_reference

# get the info from the html form
form = cgi.FieldStorage()

if len(form) == 0:
    print '''
    <html>
      <head>
        <title>Query graph visualizer</title> 
      </head>
      <body>
        <p align="left"> Parse | Metadata | SqlDoc | What is PlySql | Sqetl |</p> 
        <hr>
        <center>
          <img src="img/plysql-logo-100.png" alT'="PlySql"> 
          <p>Enter a select or create view statement.</p>
          <form name="form1" method="post" action="/" >
            <textarea name="p_statement" rows="20" cols="120"></textarea>
            <p>
              <button type="submit" > <div style="font-size:24px"> Parse </div> </button>
            </p>
        </form>
        </center>
      </body>
    </html>
    '''
else:
    p_statement = form['p_statement'].value.strip()

    print '''Content-Type: text/html\n
    <html>
    <head><title>Query</title></head>
    <body>
      <p align="left"> Parse | Metadata | SqlDoc </p> 
      <hr>
        <form name="form1" method="post" action="/">
          <img src="img/plysql-logo-060.png" alT'="PlySql"> 
          <textarea name="p_statement" rows="6" cols="60">'''
    print p_statement
    print '''</textarea>
          <button type="submit" > <div style="font-size:24px"> Parse </div> </button>
        </form>
     '''
    
    #print'''<pre>'''
    #ref = plysql_reference.PlySqlReference()
    #ref.showReference()
    #print'''</pre>'''
    
    lexer  = lex.lex(module=plysql_token_rules, reflags = re.IGNORECASE, debug=0, optimize=1, lextab=None)
    lexer.input(p_statement)    
    
    #print'''<pre>'''
    #for tok in lexer:    
        #print tok.type.rjust(16) + ' : ' + tok.value    
    #print'''</pre>'''
    
    parser = yacc.yacc(module=plysql_grammar_rules, debug=0, optimize=1, write_tables=0)
    result = parser.parse(p_statement) 
    
    print'''<pre>'''
    if result != None:
        #result.debugMsg(result.getSyntaxStructure(),-1,sys._getframe().f_code.co_name)
        result.showMetadata()
    print'''</pre>'''
    
    print'''<pre>'''
    print p_statement
    print'''</pre>'''
    
    print '''
    </body>
    </html>
    '''
