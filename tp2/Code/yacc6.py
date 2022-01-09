import ply.yacc as yacc
import sys
from lex6 import tokens, text2

"""
Not sure if `commands0` is needed.

```
<commands0>
start
<commands1>
stop
<commands2>
```
"""

commands0 = []
commands1 = []
commands2 = []
stack0 = []

def p_grammar(p):
    """
    expr : commands

    commands : command
             | commands command

    command : definition
            | declaration
            | basic_command

    basic_commands : basic_command
                   | basic_commands SEMI_COLON basic_command

    basic_command : cases
                  | goto
                  | labelling
                  | PINT _INT
                  | PFLOAT _FLOAT
                  | PSTR _STRING
                  | PREF _RESTRICTED_WORD
                  | GVAL
                  | SREF
                  | calling
                  | transclusion_declaration
                  | SEMI_COLON

    calling : function_call

    function_call : CALL

    cases : case
          | cases case

    case : CASE _INT COLON LEFT_BRACE basic_commands RIGHT_BRACE

    goto : GOTO label

    definition : function_definition
               | primitive_function_definition
               | transclusion_definition

    function_definition : DEF FUNC _NAME names DOUBLE_COLON names LEFT_BRACE expr RIGHT_BRACE
                        | DEF FUNC _NAME names LEFT_BRACE expr RIGHT_BRACE
                        | DEF FUNC _NAME LEFT_BRACE expr RIGHT_BRACE

    primitive_function_definition : DEF BFUNC _NAME LEFT_BRACE basic_commands RIGHT_BRACE

    transclusion_definition : TRANS _NAME LEFT_BRACE basic_commands RIGHT_BRACE

    declaration : variable_declaration
                | transclusion_declaration

    transclusion_declaration : LESS_THAN_SIGN _NAME GREATER_THAN_SIGN
    variable_declaration : _NAME COLON type

    type : STRING
         | INT
         | FLOAT
         | array

    array : ARRAY _INT

    labelling : LABEL COLON label

    label : DOUBLE_QUOTE _NAME DOUBLE_QUOTE

    names : _NAME
          | names _NAME
    """

def p_error(p):
    print("Syntax error", p)
    parser.exito = False

parser = yacc.yacc()

parser.parse(text2)
tok = parser.token()
while tok:
    print(tok)
    tok = parser.token()
