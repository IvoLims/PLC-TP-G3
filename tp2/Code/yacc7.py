import ply.yacc as yacc
import sys
from lex7 import tokens
import re
"""
expr : ID | STR | num | list
num  : REAL | INT
list : ( seq )
seq  : ε | expr seq
"""

def get_label1():
    lab = f'la{parser.label_count1}'
    parser.label_count1 += 1
    return lab

class Var:
    def __init__(self, name, order, var_type):
        self.name = name
        self.order = order
        self.var_type = var_type
        self.value = None

class FUNC:
    def __init__(self,name,nargs,nouts,pos):
        self.name = name
        self.nargs = nargs
        self.nouts = nouts
        self.pos = pos
    def aref(self,argnum):
        return -self.nargs + int(argnum) - 1
    def rref(self,resnum):
        return -self.nargs - self.nouts + int(resnum) - 1

def is_id(p):
    return type(p) == str and p[0] != '"'

def is_str(p):
    return type(p) == str and p[0] == '"'

def is_var(p):
    return type(p) != list and p in parser.ids and type(parser.ids[p]) == Var

##########################################################################################
def push_rec(p,commands):
    parg = push(p)
    if parg:
        commands.append(parg)
    else:
        g_eval_expr(p,commands)

def push(p):
    t = type(p)
    if t == list:
        return False
    if t == int:
        return f'PUSHI {p}'
    elif t == float:
        return f'PUSHF {p}'
    elif t == FUNC:
        return f'PUSHA {p.pos}'
    elif is_str(p):
        return f'PUSHS {p}'
    elif is_var(p):
        return push_l(parser.ids[p].order)
    elif p[0] == '#':
        return push_l(parser.funcstack[-1].aref(p[1:]))
    elif p[0] == '$':
        return push_l(parser.funcstack[-1].rref(p[1:]))
    else:
        return False

def push_l(p):
    return f'PUSHL {p}'


def write(p):
    if p == 'int':
        return f'WRITEI'
    elif p == 'float':
        return f'WRITEF'
    elif p == 'str':
        return f'WRITES'


def dup(p):
    return f'DUP {p}'


def push_l(p):
    return f'PUSHL {p}'


def push_g(p):
    return f'PUSHL {p}'


def push_n(p):
    return f'PUSHN {int(p)}'


def push_a(p):
    return f'PUSHA {p}'


def pop(n):
    return f'POP {n}'


def store_l(p):
    return f'STOREL {p}'


def jump(label):
    return f'JUMP {label}'


def jz(label):
    return f'JZ {label}'


CALL = 'CALL'
RETURN = 'RETURN'
MULT = 'MUL'
EQUAL = 'EQUAL'
START = 'START'
STOP = 'STOP'

##########################################################################################

def g_eval_expr(p,commands,astop=None):
    """
    3 relevant cases:
        - subexpression
        - variable
        - primitive value
    """
    match p[0]:
        case 'decl':
            for pair in p[1:]:
                var_name = pair[0]
                var_type = pair[1]
                parser.ids[var_name] = Var(
                    var_name,
                    parser.global_vars,
                    var_type)
                if var_type == 'array':
                    parser.ids[var_name].end = parser.ids[var_name].order + \
                        int(pair[2]) - 1
                    parser.global_vars += int(pair[2])
                    commands.append(push_n(pair[2]))
                else:
                    parser.global_vars += 1
                    commands.append(push_n(1))
        case 'let':
            for pair in p[1:]:
                var_name = pair[0]
                var_value = pair[1]
                push_rec(var_value,commands)
                # pcom = push(var_value)
                # if pcom :
                #     commands.append(pcom)
                # else:
                #     g_eval_expr(p[1],commands)
                if var_name[0] == '#':
                    ref = parser.funcstack[-1].aref(var_name[1:])
                elif var_name[0] == '$':
                    print('ref -------',var_name)
                    ref = parser.funcstack[-1].rref(var_name[1:])
                else:
                    ref = parser.ids[var_name].order
                commands.append(store_l(ref))
        case 'mirror':
            commands.append(r'⊕')
            commands.append(push(p[1])[6:])
            commands.append(r'⊕')
        case 'mdecl':
            parser.ids[p[1]] = Var(p[1],parser.global_vars,'matrix')
            parser.ids[p[1]].dim1 = p[2]
            parser.ids[p[1]].dim2 = p[3]
            commands.append(push_n(p[2]*p[3]))
            parser.global_vars += p[2]*p[3]
        case 'mref':
            commands.append(push_l(parser.ids[p[1]].order + p[2]*parser.ids[p[1]].dim2 + p[3]))
        case 'mset':
            commands.extend([push(p[4]), store_l(
                parser.ids[p[1]].order + p[2]*parser.ids[p[1]].dim2+p[3])])
        case 'aref':
            if type(p[1]) != list and p[1] in parser.ids and type(parser.ids[p[1]]) == Var:
                commands.append(push_l(parser.ids[p[1]].order + int(p[2])))
        case 'aset':
            commands.extend([push(p[3]), store_l(
                parser.ids[p[1]].order + int(p[2]))])
        case 'while':
            begin_while = get_label1()
            end_while = get_label1()
            commands.append(begin_while + ':')
            push_rec(p[1],commands)
            # pcond = push(p[1])
            # if pcond:
            #     commands.append(pcond)
            # else:
            #     g_eval_expr(p[1],commands)
            commands.append(jz(end_while))
            for body_part in p[2]:
                push_rec(body_part,commands)

            # pbody = push(p[2])
            # if pbody:
            #     commands.append(pbody)
            # else:
            #     g_eval_expr(p[2],commands)
            commands.append(jump(begin_while))
            commands.append(end_while + ':')
        case ('mul' | 'add' | 'sub' | 'div' |
              'fmul' | 'fadd' | 'fsub' | 'fdiv' | 'mod' |
              'inf' | 'infeq' | 'sup' | 'supeq'
              'finf' | 'finfeq' | 'fsup' | 'fsupeq'| 'equal'):
            for arg in p[1:]:
                push_rec(arg,commands)
                # parg = push(arg)
                # if parg:
                #     commands.append(parg)
                # else:
                #     g_eval_expr(arg,commands)
            commands.append(p[0].upper())
        case 'writei' | 'writef' | 'writes' | 'atoi' | 'atof' | 'itof' | 'ftoi' | 'stri' | 'strf':
            push_rec(p[1],commands)
            commands.append(p[0].upper())
        case 'read':
            commands.append(p[0].upper())
        case 'goto':
            commands.append('goto' + jump(p[1]))
        case 'label':
            commands.append('goto' + p[1])
        case 'call':
            parser.funcstack.append(parser.ids[p[1]])
            commands.append(push_n(parser.ids[p[1]].nouts))
            for arg in p[2:]:
                push_rec(arg,commands)
            push_rec(p[1],commands)
            commands.extend([push(parser.ids[p[1]]),CALL,pop(parser.ids[p[1]].nargs)])
        case 'defun':
            if astop is not None:
                astop.append(True)
            parser.ids[p[1]] = FUNC(p[1],p[2],p[3],get_label1())
            parser.funcstack.append(parser.ids[p[1]])
            commands.append(parser.ids[p[1]].pos + ":")
            for body_part in p[4]:
                push_rec(body_part,commands)
            commands.append(RETURN)
            # parser.funcstack.pop()
        case 'case':
            push_rec(p[1],commands)
            # pcond = push(p[1])
            # if pcond:
            #     commands.append(pcond)
            # else:
            #     g_eval_expr(p[1],commands)
            commands.append(dup(1))
            end_case = 'l' + str(parser.label_count + len(p[2:]))
            parser.label_count += 1
            for i,case0 in enumerate(p[2:]):
                expr1,expr2 = case0[0],case0[1]
                if i == 0:
                    push_rec(expr1,commands)
                    commands.append(EQUAL)
                    next_case_label = 'l' + str(parser.label_count)
                    parser.label_count += 1
                    commands.append(jz(next_case_label))
                    for body_part in expr2:
                        push_rec(body_part,commands)
                    commands.append(jump(end_case))
                else:
                    commands.append(next_case_label + ":")
                    commands.append(dup(1))
                    push_rec(expr1,commands)
                    commands.append(EQUAL)
                    next_case_label = 'l' + str(parser.label_count)
                    parser.label_count += 1
                    commands.append(jz(next_case_label))
                    push_rec(expr2,commands)
                    if i != len(p[2:]) - 1:
                        commands.append(jump(end_case))
            commands.append(next_case_label + ':')
    return commands

##########################################################################################

def p_expr_ID(p):
    """expr : ID"""
    p[0] = p[1]
    print('p_expr_ID =',p[0])

def p_expr_STR(p):
    """expr : STR"""
    p[0] = p[1]
    print('p_expr_STR =',p[0])

def p_expr_INT(p):
    """expr : INT"""
    p[0] = int(p[1])
    print('p_expr_INT =',p[0])

def p_expr_REAL(p):
    """expr : REAL"""
    p[0] = float(p[1])
    print('p_expr_REAL =',p[0])

##########################################################################################

def p_expr_list(p):
    """expr : list"""
    p[0] = p[1]
    print('p_expr_list =', p[0])
    if p[0][0] == 'do':
        res1 = [START]
        res2 = [STOP]
        for expr in p[0][1:]:
            astop = []
            res = g_eval_expr(expr,[],astop)
            print('astop',astop)
            if astop:
                res2.extend(res)
            else:
                res1.extend(res)
        tres = res1 + res2
        print(tres)
        pre_mirror = '\n'.join(tres)
        post_mirror = re.sub(r'\n⊕\n([^⊕]+)⊕\n',r' \1',pre_mirror)
        print(post_mirror)

# fim da expressao
def p_list(p):
    """list : LP seq RP"""
    p[0] = p[2]
    print('p_list =', p [2])

##########################################################################################

def p_seq(p):
    """seq : expr seq """
    p[0] = [p[1]] + p[2]
    print('p_seq =', [p[1]],'+',p[2])

def p_seq_empty(p):
    """seq : """
    p[0] = []

##########################################################################################

def p_error(p):
    print("Syntax error", p)
    parser.exito = False

##########################################################################################

parser = yacc.yacc()
parser.exito = True

##########################################################################################
class Object(object):
    pass

parser.funcs = {}
parser.states = Object()
parser.states.decl = False
# where identifiers will be stored
parser.types = {'int', 'real', 'string'}
parser.functions = {'decl', 'while', 'let', 'defprim', 'defun'}
parser.funcstack = []
parser.ids = dict.fromkeys(parser.functions.union(parser.types))
parser.exito = True
parser.label_count1 = 0
parser.global_vars = 0
parser.label_count = 0
parser.label_count1 = 0
parser.label_count2 = 0
parser.local_vars = {}
parser.decls = []
parser.whilestack = []
parser.casestack = []
##########################################################################################

# fonte = ""
# for linha in sys.stdin:
#     fonte += linha
# parser.parse(fonte)

# print(g_eval_expr(['decl', ['x', 'int']],[]))
# print(g_eval_expr(['while', ['infeq', 'x', 3], ['let', ['x', ['add', 'x', 1]]]],[]))
# print(g_eval_expr(['case', ['infeq', 1, 2], [3, ['add', 4, 5]], [6, ['sub', 7, 8]]],[]))
# print(g_eval_expr(['decl', ['n', 'int'], ['num', 'int'], ['min', 'int'], ['i', 'int']],[]))
# print(g_eval_expr(['let', ['min', 0], ['i', 0], ['n', 3]],[]))
# print(g_eval_expr(['while', ['inf', 'i', 'n'], ['let', ['num', ['read']]]],[]))
if __name__ == "__main__":
    text = ''
    for line in sys.stdin:
        match line:
            case '_@_\n':
                parser.parse(text)
                tok = parser.token()
                while tok:
                    print(tok)
                    tok = parser.token()
                text = ''
            case _:
                text += line

if parser.exito:
    print("Parsing finished successfully!")
