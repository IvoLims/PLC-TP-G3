import ply.yacc as yacc
import sys
from mistas_lex import tokens

commands = []

"""
LIST : LP PELEMS RP
     | LP RP

ELEMS : ELEM
      | ELEM ELEMS
      | PELEMS

PELEMS : P ELEMS

ELEM : ATOM
     | LIST

ATOM : WORD
     | NUM

NUM : INT
    | REAL
"""

"""
ELEM : ATOM
     | LIST

LIST : LP ELEMS RP
     | LP RP

ELEMS : ELEM
      | ELEM ELEMS

ATOM : WORD
     | NUM

NUM : INT
    | REAL
"""

class Var:
    def __init__(self,name,order,value,var_type):
        assert type(value) == var_type
        self.name = name
        self.order = order
        self.value = value
        self.var_type = var_type

def push_n(p):
    return f'PUSHN {int(p)}'

def push(p):
    t = type(p)
    if t == int:
        return f'PUSHI {p}'
    elif t == float:
        return f'PUSHF {p}'
    elif t == str:
        return f'PUSHS {p}'

def push_l(p):
    return f'PUSHL {p}'

def label_function(name,n,k):
    """f ∷ p1,p2,...,pn → r1,r2,...,rk"""
    res = []
    res.append(f'{name}:')
    for i in range(-n,0):
        res.append(push_l(i))

def p_sexpr(p):
    """SEXPR : ATOM
             | LIST"""
    print('sexpr:',p[1])


def p_list_elems(p):
    """LIST : LP ELEMS RP"""
    p[0] = p[2]

def p_list_empty(p):
    """LIST : LP RP"""
    print('EMPTY')
    p[0] = None


def p_elems_1(p):
    """ELEMS : SEXPR"""
    p[0] = p[1]

def p_elems_2(p):
    """ELEMS : SEXPR ELEMS"""
    p[0] = p[2]


def p_atom_word(p):
    """ATOM : WORD"""
    if p[1] in parser.ids:
        match p[1]:
            case 'decl':
                parser.states.decl = True
            case 'while':
                parser.states._while = True
            case 'let':
                restart_states()
            case _:
                parser.states.decl = True
        print('ID')
    else:
        if parser.states.decl:
            if p[1] in parser.types:
                parser.decls[-1]['type'] = p[1]
            else:
                parser.decls.append({})
                parser.decls[-1]['id'] = p[1]
                parser.ids[p[1]] = None
        print('WORD')
    p[0] = p[1]


def p_atom_real(p):
    """ATOM : REAL"""
    print('REAL')
    p[0] = p[1]


def p_atom_int(p):
    """ATOM : INT"""
    print('INT')
    p[0] = p[1]


def p_error(p):
    print("Syntax error", p)
    parser.exito = False


parser = yacc.yacc()

class Object(object):
    pass


parser.states = Object()
parser.states.decl = False
# where identifiers will be stored
parser.types = {'int', 'real', 'string'}
parser.functions = {'decl', 'while', 'let'}
parser.ids = dict.fromkeys(parser.functions.union(parser.types))
parser.exito = True
parser.global_vars = {}
parser.local_vars = {}
parser.decls = []

def restart_states():
    for state in parser.states.__dict__.keys():
        setattr(parser.state,f'{state}',False)

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
