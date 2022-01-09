import ply.lex as lex
import sys

tokens = ["_INT", "_FLOAT", "_WORD", "DOUBLE_COLON", "DEF", "FUNC", "DOUBLE_QUOTE","LEFT_BRACE","RIGHT_BRACE","SEMI_COLON","PINT","PFLOAT","PSTR","PREF","GVAL","SREF","CALL", "GOTO", "CASE", "_RESTRICTED_WORD", "LABEL", "ARRAY", "INT", "FLOAT", "STRING", "LESS_THAN_SIGN", "GREATER_THAN_SIGN","_STRING","COLON", "BFUNC"]

def t__FLOAT(t):
    r"[0-9]*\.[0-9]+"
    return t

def t_LESS_THAN_SIGN(t):
    r'\<'
    return t

def t_GREATER_THAN_SIGN(t):
    r'\>'
    return t

def t_DOUBLE_COLON(t):
    r'\::'
    return t

def t_COLON(t):
    r'\:'
    return t

def t_BFUNC(t):
    r'bfunc'
    return t

def t_SEMI_COLON(t):
    r'\;'
    return t

def t_DEF(t):
    r"def"
    return t

def t_FUNC(t):
    r"func"
    return t

def t_PINT(t):
    r"pint"
    return t

def t_PFLOAT(t):
    r"pfloat"
    return t

def t_PSTR(t):
    r"pstr"
    return t

def t_PREF(t):
    r"pref"
    return t

def t_GVAL(t):
    r"gval"
    return t

def t_SREF(t):
    r"sref"
    return t

def t_CALL(t):
    r"call"
    return t

def t_GOTO(t):
    r"goto"
    return t

def t_CASE(t):
    r"case"
    return t

def t_LABEL(t):
    r"label"
    return t

def t_FLOAT(t):
    r"float"
    return t

def t_STRING(t):
    r"string"
    return t

def t_INT(t):
    r"int"
    return t

def t_ARRAY(t):
    r"array"
    return t

def t_LEFT_BRACE(t):
    r"\{"
    return t

def t_RIGHT_BRACE(t):
    r"\}"
    return t

def t__INT(t):
    r"[0-9]+"
    return t

def t__RESTRICTED_WORD(t):
    r"[a-zA-Z_]\w+"
    return t

def t__STRING(t):
    r'"[^"]+"'
    return t

t_ignore = " \n\t"

def t_error(t):
    print("Carater ilegal: ", t.value)


lexer = lex.lex()

text ="""def func1:
    def func2:
        return r2
    return r1
"""

text2 ="""
def func val2 val1
{
    pref ref1;
    pref val1;
    gval;
    sref;
}
"""

lexer.input(text2)
tok = lexer.token()
while tok:
    print(tok)
    tok = lexer.token()

# if __name__ == "__main__":
#     for line in sys.stdin:
#         lexer.input(line)
#         tok = lexer.token()
#         while tok:
#             print(tok)
#             tok = lexer.token()
