import ply.yacc as yacc
import sys
from mistas_lex import tokens

# AS: Atomic Symbol
# AP: Atom Part
def p_mistas_grammar(p):
    """
    SEXPR : AS
          | LP SEXPR DOT SEXPR RP
          | LP SLIST RP
    SLIST : EMPTY
          | SEXPR SLIST
    AS    : LETTER AP
    AP    : EMPTY
          | LETTER AP
          | NUMBER AP
    """

def p_error(p):
    print("Syntax error", p)
    parser.exito = False


parser = yacc.yacc()

parser.exito = True

fonte = ""
for linha in sys.stdin:
    fonte += linha

parser.parse(fonte)

if parser.exito:
    print("Parsing finished successfully!")
