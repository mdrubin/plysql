'''
t1.* levert geen t1.* kolom op.
'''


import sys
import re

import cgi

import ply.lex as lex    
import ply.yacc as yacc    

import plysql_web

import plysql_token_rules    
import plysql_grammar_rules

from plysql_classes import banner
from plysql_classes import Node

import plysql_reference

# get the info from the html form
form = cgi.FieldStorage()

if len(form) == 0:
    p_statement='''-- just an example statement
select   t1.column01                       as c1
,        sum(t2.column03)                  as sum_c3
from     table01                           as t1
join     (select table02_id
          ,      column03
          from   table02
          where  t2.column02 = 'something'
         )                                 as t2
on       t1.table02_id = t2.table02_id
group by t1.column01

create table table01 
(table01_id number
,column01   varchar2(126)
,table02_id number)
'''

    print plysql_web.HttpHeader
    print '''<html>'''
    print plysql_web.htmlHead
    print '''<body>'''
    print plysql_web.pageHeader
    print '''
        <center>
          <img src="img/plysql-logo-100.png" alT'="PlySql"> 
          <p>To make a metadata analysis please enter your sql script below.</p>
          <form name="form1" method="post" action="index.py" >
            <textarea name="p_statement" rows="20" cols="120">'''
    print p_statement
    print '''
            </textarea>
            <p>
    '''
    print plysql_web.formButton
    print '''
            </p>
        </form>
    '''
    print plysql_web.pageFooter
    print '''
        </center>
      </body>
    </html>
    '''
else:
    p_statement = form['p_statement'].value.strip()

    print plysql_web.HttpHeader
    print '''<html>'''
    print plysql_web.htmlHead
    print '''<body>'''
    print plysql_web.pageHeader
    print '''
        <form name="form1" method="post" action="index.py">
          <img src="img/plysql-logo-060.png" alT'="PlySql"> 
          <textarea name="p_statement" rows="6" cols="60">'''
    print p_statement
    print '''</textarea>
    '''
    print plysql_web.formButton
    print '''
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
    
    #print'''<pre>'''
    #print p_statement
    #print'''</pre>'''
    
    print plysql_web.pageFooter
    print '''
    </body>
    </html>
    '''
