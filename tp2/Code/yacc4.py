import ply.yacc as yacc
import sys
from lex4 import tokens, text2

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
             | commands SEMI_COLON command

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

    calling : function_call

    function_call : CALL

    cases : case
          | cases case

    case : CASE _INT COLON LEFT_BRACE basic_commands RIGHT_BRACE

    goto : GOTO label

    definition : function_definition
               | primitive_function_definition
               | transclusion_definition

    function_definition : DEF FUNC function_name function_arguments DOUBLE_COLON function_results LEFT_BRACE basic_commands RIGHT_BRACE
                        | DEF FUNC function_name function_arguments LEFT_BRACE basic_commands RIGHT_BRACE
                        | DEF FUNC function_name LEFT_BRACE basic_commands RIGHT_BRACE
        function_name : _RESTRICTED_WORD
    primitive_function_definition : DEF BFUNC primitive_function_name LEFT_BRACE basic_commands RIGHT_BRACE
        primitive_function_name : _RESTRICTED_WORD
    transclusion_definition : transclusion_declaration LEFT_BRACE basic_commands RIGHT_BRACE

    declaration : variable_declaration
                | transclusion_declaration

    transclusion_declaration : LESS_THAN_SIGN transclusion_name GREATER_THAN_SIGN
        transclusion_name : _RESTRICTED_WORD
    variable_declaration : variable_name COLON type
        variable_name : _RESTRICTED_WORD

    type : STRING
         | INT
         | FLOAT
         | array

    array : ARRAY array_size

        array_size : _INT

    labelling : LABEL COLON label

    label : _STRING


    restricted_words : _RESTRICTED_WORD
                     | restricted_words _RESTRICTED_WORD

    function_arguments : restricted_words
    function_results : restricted_words
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
