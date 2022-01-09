from __future__ import division
import ply.yacc as yacc
import sys
from lex7 import tokens
import re

import math
import operator as op


"""
expr : ID | STR | num | list
num  : REAL | INT
list : ( seq )
seq  : ε | expr seq
"""

def get_order():
    order = parser.global_vars
    parser.global_vars += 1
    return order

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
def push_rec(p,commands,parse_state):
    parg = push(p)
    if parg:
        commands.append(parg)
    else:
        g_eval_expr(p,commands,None,parse_state)

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

def repeat(n,stack,parse_state):
    push_rec(n,stack,parse_state,parse_state)
    push_rec(1,stack,parse_state,parse_state)
    push_rec(SUB,stack,parse_state,parse_state)
    rstart = get_label1()
    rend = get_label1()
    stack.append(rstart + ':')
    push_rec(n,stack,parse_state,parse_state)
    stack.append(jz(rend))
    stack.append(push(0))
    push_rec(n,stack,parse_state,parse_state)
    stack.append(push(-1))
    stack.append(ADD)
    stack.append(store_l(parser.ids['n'].order))
    stack.append(jump(rstart))
    stack.append(rend + ':')

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

def vms(instructions,opt_write_ins=''):
    import os
    if 'STOP' not in instructions:
        instructions = ['START'] + instructions + ['STOP']
    stop_index = instructions.index('STOP')
    instructions = instructions[:stop_index] + ['WRITE' + opt_write_ins.upper()] + instructions[stop_index:]

    VMS_PROG = '../vms/vms'
    CODE_DIR = '.vms_codes'
    if not os.path.exists(CODE_DIR):
        os.mkdir(CODE_DIR)
    code = '\n'.join(instructions)
    i = 0
    while os.path.exists(f"{CODE_DIR}/.vms_code{i}.vm"):
        i += 1
    fh = open(f"{CODE_DIR}/.vms_code{i}.vm", "w")
    fh.write(code)
    fh.close()
    stream = os.popen(f'{VMS_PROG} {f"{CODE_DIR}/.vms_code{i}.vm"}')
    return stream.read()

CALL = 'CALL'
RETURN = 'RETURN'
MULT = 'MUL'
EQUAL = 'EQUAL'
START = 'START'
STOP = 'STOP'
ADD = 'ADD'
SUB = 'SUB'
PADD = 'PADD'
##########################################################################################

def g_eval_expr(p,commands,astop=None,parse_state=None):
    """
    3 relevant cases:
        - subexpression
        - variable
        - primitive value
    """
    if parse_state is None:
        parse_state = []
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
                    if len(pair) > 2:
                        parser.ids[var_name].end = parser.ids[var_name].order + \
                            pair[2] - 1
                        parser.global_vars += int(pair[2])
                        commands.append(push_n(pair[2]))
                    else:
                        parser.ids[var_name].order = None
                else:
                    parser.global_vars += 1
                    commands.append(push_n(1))
        case 'setsize':
            if parser.ids[p[1]].var_type == 'array' and parser.ids[p[1]].order is None:
                instructions = parse_state['commands_so_far'] + g_eval_expr(p[2],[])
                arr_size = int(vms(instructions,'i'))
                commands.append(push_n(arr_size))
                parser.ids[p[1]].order = parser.global_vars
                parser.ids[p[1]].end = parser.ids[p[1]].order + arr_size - 1
                parser.global_vars += arr_size
        case 'let':
            for pair in p[1:]:
                var_name = pair[0]
                var_value = pair[1]
                push_rec(var_value,commands,parse_state)
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
            # (aset array_name index value)
            print('------------------aset')
            push_rec(p[3],commands,parse_state)
            # push_rec(p[1].order)
            # push_rec(p[2])
            instructions = parse_state['commands_so_far'] + g_eval_expr(p[2],[])
            commands.append(store_l(
                parser.ids[p[1]].order + int(vms(instructions,'i'))))
        case 'while':
            begin_while = get_label1()
            end_while = get_label1()
            commands.append(begin_while + ':')
            push_rec(p[1],commands,parse_state)
            # pcond = push(p[1])
            # if pcond:
            #     commands.append(pcond)
            # else:
            #     g_eval_expr(p[1],commands)
            commands.append(jz(end_while))
            for body_part in p[2]:
                push_rec(body_part,commands,parse_state)

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
                push_rec(arg,commands,parse_state)
                # parg = push(arg)
                # if parg:
                #     commands.append(parg)
                # else:
                #     g_eval_expr(arg,commands)
            commands.append(p[0].upper())
        case 'writei' | 'writef' | 'writes' | 'atoi' | 'atof' | 'itof' | 'ftoi' | 'stri' | 'strf':
            push_rec(p[1],commands,parse_state)
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
                push_rec(arg,commands,parse_state)
            push_rec(p[1],commands,parse_state)
            commands.extend([push(parser.ids[p[1]]),CALL,pop(parser.ids[p[1]].nargs)])
        case 'defun':
            if astop is not None:
                astop.append(True)
            parser.ids[p[1]] = FUNC(p[1],p[2],p[3],get_label1())
            parser.funcstack.append(parser.ids[p[1]])
            commands.append(parser.ids[p[1]].pos + ":")
            for body_part in p[4]:
                push_rec(body_part,commands,parse_state)
            commands.append(RETURN)
            # parser.funcstack.pop()
        case 'case':
            push_rec(p[1],commands,parse_state)
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
                    push_rec(expr1,commands,parse_state)
                    commands.append(EQUAL)
                    next_case_label = 'l' + str(parser.label_count)
                    parser.label_count += 1
                    commands.append(jz(next_case_label))
                    for body_part in expr2:
                        push_rec(body_part,commands,parse_state)
                    commands.append(jump(end_case))
                else:
                    commands.append(next_case_label + ":")
                    commands.append(dup(1))
                    push_rec(expr1,commands,parse_state)
                    commands.append(EQUAL)
                    next_case_label = 'l' + str(parser.label_count)
                    parser.label_count += 1
                    commands.append(jz(next_case_label))
                    push_rec(expr2,commands,parse_state)
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

commands31 = []
def p_expr_list(p): #quando programa termina
    """expr : list"""
    p[0] = p[1]
    print('p_expr_list =', p[0])
    parse_state = dict.fromkeys(['commands_so_far', 'astop', 'expr'])
    if p[0][0] == 'do':
        res1 = []
        res2 = []
        parse_state['commands_so_far'] = []
        for expr in p[0][1:]:
            astop = []
            res = g_eval_expr(expr,[],astop,parse_state)
            print('astop',astop)
            if astop:
                res2.extend(res)
            else:
                res1.extend(res)
            parse_state['commands_so_far'] = res1 + res2
        commands = parse_state['commands_so_far']
        commands = [START] + commands + [STOP]
        print(commands)
        vms(commands)
        pre_mirror = '\n'.join(commands)
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


################ Types

Symbol = str          # A Lisp Symbol is implemented as a Python str
List   = list         # A Lisp List is implemented as a Python list
Number = (int, float) # A Lisp Number is implemented as a Python int or float

################ Parsing: parse, tokenize, and read_from_tokens


################ Environments

def standard_env():
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        'abs':     abs,
        'append':  op.add,
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x,list),
        'map':     map,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'mul': lambda x,y : f"{x} ; {y} ; mul",
        'echo': lambda x : f"pushi {x}",
    })
    return env

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

global_env = standard_env()

################ Interaction: A REPL

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval1(parser.parse(input(prompt)))
        if val is not None:
            print(lispstr(val))

def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')'
    else:
        return str(exp)

################ Procedures

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval1(self.body, Env(self.parms, args, self.env))

################ eval

def eval1(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if eval1(test, env) else alt)
        return eval1(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = eval1(exp, env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval1(exp, env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = eval1(x[0], env)
        args = [eval1(exp, env) for exp in x[1:]]
        return proc(*args)

# print(eval1(['begin', ['define', 'r', 10], ['*', 'pi', ['*', 'r', 'r']]]))

# repl()
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
            case '!\n':
                print(vms(commands31[-1]))
                text = ''
            case _:
                text += line

if parser.exito:
    print("Parsing finished successfully!")

