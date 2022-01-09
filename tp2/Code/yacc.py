import ply.yacc as yacc
import sys
from mistas_lex import tokens

def add_atoms(atoms):
    pass


def p_expr(p):
    """EXPR : LP ATOMS RP"""

def p_atoms(p):
    """ATOMS : ATOM
             | ATOMS ATOM"""
    match p[1]:
        case 'decl':
            p.global_vars = True
    # if p.global_vars == True:

def p_atom(p):
    """ATOM : WORD
            | NUMBER
            | EXPR
            | EMPTY"""
    print(p[1])

def p_emtpy(p):
    """EMPTY :"""
    pass

def p_number(p):
    """NUMBER : INT
              | REAL"""

def p_error(p):
    print("Syntax error", p)
    parser.exito = False


parser = yacc.yacc()
parser.global_vars = {}
parser.declare = False

parser.exito = True

# fonte = ""
# for linha in sys.stdin:
#     fonte += linha
# parser.parse(fonte)

if __name__ == "__main__":
    for line in sys.stdin:
        parser.parse(line)
        tok = parser.token()
        while tok:
            print(tok)
            tok = parser.token()


if parser.exito:
    print("Parsing finished successfully!")
