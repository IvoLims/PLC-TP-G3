import ply.yacc as yacc
import sys
from lex8 import tokens

"""
coms : | coms com
com : BS ID
    | LP com RP
    | com LP coms RP
atom : ID | STR | REAL | INT

"""

class PFUNC:
    def __init__(self,name,nargs,body):
        self.name = name
        self.nargs = nargs
        self.body = body

# def p_grammar(p):
#     """
#     prog : LB atoms RB
#     atoms : atoms LB atom RB
#     atom  : STR
#           | REAL
#           | INT
#           | WORD
#           | ID
#     """
# def p_exprs(p):
#     """exprs : exprs expr"""
#     p[0] = p[1]
#     p[0].append(p[2])
#     print(p[0])
# def p_exprs_empty(p):
#     """exprs : """
#     p[0] = []
# def p_expr_id(p):
#     """expr : ID"""
#     p[0] = p[1]
# def p_expr_id_args(p):
#     """expr : arg"""
#     p[0] = p[1]
#     print(p[0])
# def p_expr_atom(p):
#     """expr : atom"""
#     p[0] = p[1]
# def p_arg(p):
#     """arg : LB expr RB"""
#     p[0] = p[2]

def p_prog(p):
    """prog : LB atoms RB"""
    p[0] = p[2]

def p_atoms(p):
    """atoms : atoms atom """
    p[0] = p[1]
    p[0].append(p[2])
def p_atoms_emp(p):
    """atoms : """
    p[0] = []

def p_atom_id(p):
    """atom : ID"""
    p[0] = p[1]
def p_atom_word(p):
    """atom : WORD"""
    p[0] = p[1]
def p_atom_str(p):
    """atom : STR"""
    p[0] = p[1]
def p_atom_real(p):
    """atom : REAL"""
    p[0] = float(p[1])
def p_atom_int(p):
    """atom : INT"""
    p[0] = int(p[1])



def p_error(p):
    print("Syntax error", p)
    parser.exito = False

##########################################################################################

parser = yacc.yacc()
parser.exito = True

if __name__ == "__main__":
    for line in sys.stdin:
        match line:
            case _:
                parser.parse(line)
                tok = parser.token()
                while tok:
                    print(tok)
                    tok = parser.token()

if parser.exito:
    print("Parsing finished successfully!")
