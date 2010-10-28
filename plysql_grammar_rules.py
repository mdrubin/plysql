import sys
from plysql_token_rules import tokens
from plysql_classes import NonTerminal

##########################################################
# precedence rules
##########################################################

# a = b and c = d  -> must be resolved as (a=b) and (b=c)  and not (a = (b and (c = d)))
# don't use nonassoc because it prevents 1+2+3+4 and results in an syntax error.
precedence = (
    ('left','AS'),              # - resolve syntax error
    ('left','LOG_OPERATOR'),    # - first apply normal operators
    ('left','NOT'),             #   then the
    ('left','OPERATOR','STAR'), #   operators before logical operators
    ('left','IDENTIFIER'),      #
    ('left','PLUS_MINUS'),      #   unary PLUS_MINUS before operators
)

##########################################################
# SCRIPT and STATEMENTS (create view, create table, select)
##########################################################
def p_script_next(p):
    '''script    : statement statement'''
    p[0] = NonTerminal(p)

def p_script_first(p):
    '''script    : statement'''
    p[0] = NonTerminal(p)

def p_statement(p):
    '''statement : create_view
                 | create_table
                 | select'''
    p[0] = NonTerminal(p)

def p_create_table(p):
    '''create_table : CREATE_TABLE expr_identifier expr_parent'''
    p[0] = NonTerminal(p)

def p_create_view(p):
    '''create_view : CREATE_VIEW expr_as'''
    p[0] = NonTerminal(p)
    p[0].moveAlias(p[2],'aliases_view')
    p[0].moveAliasIdentifier(p[2],0)

def p_select_next(p):
    '''select        : select clause'''
    p[0] = NonTerminal(p)

def p_select_first(p):
    '''select        : clause'''
    p[0] = NonTerminal(p)

##########################################################
# ANALYTIC FUNCTIONS
##########################################################
def p_analytic_function_next(p):
    '''analytic_function  : analytic_function clause'''
    p[0] = NonTerminal(p)

def p_analytic_function_first(p):
    '''analytic_function  : clause_partition_by'''
    p[0] = NonTerminal(p)

def p_clause_partition_by(p):
    '''clause_partition_by   : PARTITION_BY expr'''
    p[0] = NonTerminal(p)
    p[0].moveIdentifierstack(p[2],'identifiers_column')

##########################################################
# CLAUSES
##########################################################
def p_clause(p):
    '''clause : clause_with
              | clause_select
              | clause_from
              | clause_join
              | clause_where
              | clause_group_by
              | clause_having
              | clause_order_by'''
    p[0] = NonTerminal(p)

def p_clause_with(p):
    '''clause_with        : WITH expr_comma'''
    p[0] = NonTerminal(p)
    p[0].moveAliasstack(p[2],'aliases_with')
    p[0].moveIdentifierstack(p[2],'identifiers_alias')

def p_clause_select(p):
    '''clause_select      : SELECT expr_select_modifier expr_comma'''
    p[0] = NonTerminal(p)
    p[0].moveAliasIdentifiers(p[3],1)
    p[0].moveAliasstack(p[3],'aliases_column')
    p[0].moveIdentifierstack(p[0],'identifiers_column')

def p_clause_from(p):
    '''clause_from        : FROM expr_comma'''
    p[0] = NonTerminal(p)
    p[0].moveAliasIdentifiers(p[2],1)
    p[0].moveAliasstack(p[2],'aliases_table')
    p[0].moveIdentifierstack(p[0],'identifiers_table')

def p_clause_join(p):
    '''clause_join        : JOIN_OPERATOR expr ON    expr
                          | JOIN_OPERATOR expr USING expr_parent'''
    p[0] = NonTerminal(p)
    p[0].moveAlias(p[2],'aliases_table')
    p[0].moveAliasIdentifier(p[2],1)
    p[0].moveIdentifierstack(p[4],'identifiers_column')
    p[0].moveIdentifierstack(p[0],'identifiers_table')
 
def p_clause_where(p):
    '''clause_where       : WHERE expr'''
    p[0] = NonTerminal(p)
    p[0].moveIdentifierstack(p[2],'identifiers_column')

def p_clause_group_by(p):
    '''clause_group_by    : GROUP_BY expr_comma'''
    p[0] = NonTerminal(p)
    p[0].moveIdentifierstack(p[2],'identifiers_column')

def p_clause_having(p):
    '''clause_having      : HAVING expr'''
    p[0] = NonTerminal(p)
    p[0].moveIdentifierstack(p[2],'identifiers_column')

def p_clause_order_by(p):
    '''clause_order_by    : ORDER_BY expr_comma'''
    p[0] = NonTerminal(p)
    p[0].moveIdentifierstack(p[2],'identifiers_column')

##########################################################
# EXPRESSIONS
##########################################################
def p_expr_select_modifier(p):
    '''expr_select_modifier : empty
                            | DISTINCT
                            | UNIQUE
                            | ALL'''
    p[0] = NonTerminal(p)

# Alias expressions (x alias, x as alias)

# Concatenate expressions 
#def p_expr_concatenate(p):
#    '''expr_concatenate     : expr expr_identifier
#                            | expr expr_function
#    '''
#    p[0] = NonTerminal(p)

def p_expr_alias(p):
    '''expr_alias         : expr expr_identifier
                          | expr expr_function
    '''
    p[0] = NonTerminal(p)
    p[0].setAlias(p[1],p[2])

def p_expr_as(p):
    '''expr_as            : expr AS      expr
                          | expr AS      expr_identifier'''
    p[0] = NonTerminal(p)
    p[0].setAlias(p[1],p[3])

# case expressions
def p_expr_case(p):
    '''expr_case          : CASE expr_conditions END '''
    p[0] = NonTerminal(p)

def p_expr_conditions_next(p):
    '''expr_conditions          : expr_conditions WHEN expr 
                                | expr_conditions THEN expr 
                                | expr_conditions ELSE expr '''
    p[0] = NonTerminal(p)

def p_expr_conditions_first(p):
    '''expr_conditions          : WHEN  expr
                                | THEN  expr
                                | ELSE  expr'''
    p[0] = NonTerminal(p)

# Parenthesize expressions
def p_expr_function(p):
    '''expr_function      : expr_identifier expr_parent'''
    p[0] = NonTerminal(p)
    p[0].moveIdentifier(p[1],'identifiers_function')

def p_expr_function_cast(p):
    '''expr_function      : CAST expr_parent'''
    p[0] = NonTerminal(p)
    p[0].moveAlias(p[2],'aliases_cast')
    p[0].moveAliasIdentifier(p[2],1)

def p_expr_parent(p):
    '''expr_parent        : PARENT_L expr_comma PARENT_R
                          | PARENT_L empty      PARENT_R'''
    p[0] = NonTerminal(p)

# Comma expressions
def p_expr_comma_next(p):
    '''expr_comma         : expr_comma COMMA expr'''
    p[0] = NonTerminal(p)

def p_expr_comma_first(p):
    '''expr_comma         : expr'''
    p[0] = NonTerminal(p)

# Binary expressions (OPERATORS, +,-, SET_OPERATORS, LOG_OPERATORS, STAR)
def p_expr_binary(p):
    '''expr_binary        : expr OPERATOR       expr
                          | expr PLUS_MINUS     expr
                          | expr SET_OPERATOR   expr
                          | expr LOG_OPERATOR   expr
                          | expr STAR           expr'''
    p[0] = NonTerminal(p)

# Unary operators ASC, DESC, NOT, -, +
def p_expr_order(p):
    '''expr_order         : expr ASC
                          | expr DESC'''
    p[0] = NonTerminal(p)

def p_expr_plus_minus(p):
    '''expr_plus_minus    : PLUS_MINUS expr'''
    '''expr_plus_minus    : PLUS_MINUS expr %prec PLUS_MINUS'''
    p[0] = NonTerminal(p)

def p_expr_not(p):
    '''expr_not           : NOT expr'''
    p[0] = NonTerminal(p)

# Identifier expressions (id1.id2.id3...)
def p_expr_identifier_next(p):
    '''expr_identifier : expr_identifier DOT IDENTIFIER
                       | expr_identifier DOT STAR'''
    p[0] = NonTerminal(p)
    p[0].setIdentifierWithDots(p[1], p[3])

def p_expr_identifier_first(p):
    '''expr_identifier : IDENTIFIER
                       | STAR'''
    p[0] = NonTerminal(p)
    p[0].setIdentifier(p[1])

# select instead of select_parent to resolve reduce/reduce conflict.
def p_expr_select(p):
    '''expr : select'''
    p[0] = NonTerminal(p)
    p[0].setSubquery(p[1])

def p_expr(p):
    '''expr : expr_case
            | expr_function
            | expr_parent
            | expr_binary
            | expr_alias
            | expr_as
            | expr_order
            | expr_plus_minus
            | expr_not
            | expr_identifier
            | term_literal
            | analytic_function
            '''
    p[0] = NonTerminal(p)

##########################################################
# LITERALS and EMPTY
##########################################################
def p_term_literal(p):
    '''term_literal : NUMBER
                    | STRING
                    | NULL'''
    p[0] = NonTerminal(p)
    p[0].setLiteral(p[1])

def p_empty(t):
    '''empty :'''
    pass

##########################################################
# ERROR
##########################################################
def p_error(p):
    print "Syntax error in input!"
