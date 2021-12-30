import ply.yacc as yacc
import sys
from mistas_lex import tokens


"""
f ∷ p1,p2,...,pn → r1,r2,...,rk

start
pushn k
push p1
push p2
...
push pn

pusha f
call
pop n // remove arguments from stack
// k top args are the result of f
stop

f:
pushl -n        // p1
pushl -n+1      // p2
...
pushl -1        // pn
storel (-n-k)   // r1
storel (-n-k+1) // r2
...
storel (-n-1)   // rn

return
"""


def push(p):
    try:
        v = int(p)
    except ValueError:
        try:
            v = float(p)
        except ValueError:
            v = p
    t = type(v)
    if t == int:
        return f'PUSHI {v}'
    elif t == float:
        return f'PUSHF {v}'
    elif t == str:
        return f'PUSHS {v}'


def write(p):
    if p == 'int':
        return f'WRITEI'
    elif p == 'float':
        return f'WRITEF'
    elif p == 'str':
        return f'WRITES'


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


class Func:
    def __init__(self, name, n, k, label):
        self.name = name
        self.in_arity = n
        self.out_arity = k
        # self.args = args
        self.label = label

    def call(self):
        res = []
        res.append(push_n(self.out_arity))
        for arg in self.args:
            res.append(push(arg))
        res.append(push_a(self.label))
        res.append(CALL)
        res.append(pop(self.in_arity))
        return res

    def init_vars(self):
        res = []
        for i in range(-self.in_arity, 0):
            res.append(push_l(i))

    def end_call(self):
        res = []
        res.append(RETURN)


class Var:
    def __init__(self, name, order, var_type):
        self.name = name
        self.order = order
        self.var_type = var_type
        self.value = None


commands = []

"""
LIST : LP ELEMS RP
     | LP RP

ELEMS : ELEM
      | ELEM ELEMS

ELEM : ATOM
     | LIST

ATOM : WORD
     | NUM

NUM : INT
    | REAL
"""


def eval_expr(p):
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
                    parser.ids[var_name].end = parser.ids[var_name].order + pair[2] - 1
                    parser.global_vars += pair[2]
                    commands.append(pair[2])
                else:
                    parser.global_vars += 1
                    commands.append(push_n(1))
        case 'let':
            for pair in p[1:]:
                var_name = pair[0]
                var_value = pair[1]
                if type(var_value) != list and var_value != list and var_value in parser.ids and type(parser.ids[var_value]) == Var:
                    commands.append(push_l(parser.ids[var_value].order))
                elif type(var_value) != list:
                    commands.append(push(var_value))
                commands.append(store_l(parser.ids[var_name].order))
        case 'aref':
             if type(p[1]) != list and p[1] in parser.ids and type(parser.ids[p[1]]) == Var:
                 commands.append(push_l(parser.ids[p[1]].order + p[2]))
        case ('mul' | 'add' | 'sub' | 'div' |
              'fmul' | 'fadd' | 'fsub' | 'fdiv' | 'mod' |
              'inf' | 'infeq' | 'sup' | 'supeq'
              'finf' | 'finfeq' | 'fsup' | 'fsupeq'):
            for arg in p[1:]:
                if type(arg) != list:
                    if arg in parser.ids and type(parser.ids[p[1]]) == Var:
                        commands.append(push_l(parser.ids[arg].order))
                    else:
                        commands.append(push(arg))
            commands.append(p[0].upper())
        case 'writei' | 'writef' | 'writes':
            if type(p[1]) != list and p[1] in parser.ids and type(parser.ids[p[1]]) == Var:
                commands.append(push_l(parser.ids[p[1]].order))
            elif type(p[1]) != list:
                commands.append(push(p[1]))
            commands.append(p[0].upper())
        case 'read':
            commands.append(p[0].upper())
        # case 'defun':
        #     parser.ids[p[1][0]] = Func(p[1][0],p[1][1],p[1][2],parser.label_count)
        #     parser.label_count += 1
    print(commands)


def eval_expr_dynamic_type(p):
    match p[0]:
        case 'decl':
            for pair in p[1:]:
                var_name = pair[0]
                var_type = pair[1]
                parser.ids[var_name] = Var(
                    var_name,
                    parser.global_vars,
                    var_type)
                parser.global_vars += 1
            commands.append(push_n(len(p[1:])))
        case 'let':
            for pair in p[1:]:
                var_name = pair[0]
                var_value = pair[1]
                if type(var_value) != list:
                    commands.append(push(var_value))
                commands.append(store_l(parser.ids[var_name].order))
        case ('mul' | 'add' | 'sub' | 'div' |
              'fmul' | 'fadd' | 'fsub' | 'fdiv' | 'mod' |
              'inf' | 'infeq' | 'sup' | 'supeq'
              'finf' | 'finfeq' | 'fsup' | 'fsupeq'):
            OP_COMMAND = p[0].upper()
            for arg in p[1:]:
                if arg in parser.ids and type(parser.ids[p[1]]) == Var:
                    commands.append(push_l(parser.ids[arg].order))
                    if parser.ids[arg].type == 'float':
                        OP_COMMAND = 'F' + OP_COMMAND
                elif type(arg) != list:
                    PUSH_COMMAND = push(arg)
                    commands.append(PUSH_COMMAND)
                    if PUSH_COMMAND[4] == 'F':
                        OP_COMMAND = 'F' + OP_COMMAND
            commands.append(OP_COMMAND)
        case 'write':
            if type(p[1]) != list and p[1] in parser.ids and type(parser.ids[p[1]]) == Var:
                commands.extend([push_l(parser.ids[p[1]].order),
                                write(parser.ids[p[1]].var_type)])
            elif type(p[1]) != list:
                PUSH_COMMAND = push(p[1])
                commands.extend([PUSH_COMMAND, 'WRITE' + PUSH_COMMAND[4]])
            else:  # caso seja uma expressao a ser calculada
                commands.append('"WRITE"')
    print(commands)


def lista(p):
    """LIST : LP ELEMS RP"""
    p[0] = p[2]
    match p[2][0]:
        case 'decl':
            for pair in p[0][1:]:
                var_name = pair[0]
                var_type = pair[1]
                parser.ids[var_name] = Var(
                    var_name,
                    parser.global_vars,
                    var_type)
                parser.global_vars += 1
            commands.append(push_n(len(p[0][1:])))
        case 'let':
            for pair in p[0][1:]:
                var_name = pair[0]
                var_value = pair[1]
                commands.extend(
                    [push(var_value), store_l(parser.ids[var_name].order)])
        case 'mult':
            commands.extend([push(p[2][1]), push(p[2][2]), MULT])

    # print(parser.global_vars)
    print(commands)
    print(p[2])


def p_list(p):
    """LIST : LP ELEMS RP"""
    p[0] = p[2]
    eval_expr(p[0])
    print(p[0])


def p_list_empty(p):
    """LIST : LP RP"""
    p[0] = None


def p_elems_elem(p):
    """ELEMS : ELEM"""
    p[0] = [p[1]]


def p_elems_elem_elems(p):
    """ELEMS : ELEMS ELEM"""
    p[0] = p[1]
    p[0].append(p[2])


def p_elem_atom(p):
    """ELEM : ATOM"""
    p[0] = p[1]


def p_elem_list(p):
    """ELEM : LIST"""
    p[0] = p[1]


def p_atom(p):
    """ATOM : WORD
            | NUM"""
    p[0] = p[1]
    if p[0] in parser.ids:
        print('ID')


def p_atom_num(p):
    """NUM : INT
           | REAL"""
    p[0] = p[1]
    print('NUM')


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
parser.functions = {'decl', 'while', 'let', 'defprim', 'defun'}
parser.ids = dict.fromkeys(parser.functions.union(parser.types))
parser.exito = True
parser.global_vars = 0
parser.label_count = 0
parser.local_vars = {}
parser.decls = []


def restart_states():
    for state in parser.states.__dict__.keys():
        setattr(parser.state, f'{state}', False)

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
