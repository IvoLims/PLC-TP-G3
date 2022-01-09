import ply.lex as lex
import sys

tokens = ["_INT", "WORD", "TAB", "DOUBLE_COLON", "DEF","NEW_LINE","SPACE"]

def t_DOUBLE_COLON(t):
    r'\:'
    return t

def t_NEW_LINE(t):
    r'\n'
    return t

def t_DEF(t):
    r"def"
    return t

def t__INT(t):
    r"[0-9]+"
    return t

def t_WORD(t):
    r"[a-zA-Z0-9_]+"
    return t

def t_TAB(t):
    r'\ {4}'
    return t


def t_SPACE(t):
    r'\ '

t_ignore = "\t"

def t_error(t):
    print("Carater ilegal: ", t.value)


lexer = lex.lex()

text ="""def func1:
    def func2:
        return r2
    return r1
"""

text2 ="""def func1:
    locs
    LAC
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
