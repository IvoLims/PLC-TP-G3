import ply.lex as lex
import sys

tokens = ["REAL", "INT", "ID", "STR" ,"LP", "RP"]

# declaração das Palavras-Reservadas e dos Simbolos de Classe (variáveis)
t_LP  = r"\("
t_RP  = r"\)"

def t_REAL(t):
    r"[+-]?[0-9]*\.[0-9]+"
    return t

def t_INT(t):
    r"[+-]?[0-9]+"
    return t

def t_ID(t):
    r"[-+*/!#$@%^&=.a-zA-Z0-9_]+"
    return t

def t_STR(t):
    r'"[^"]*"'
    return t

# declaração dos Carateres que podem aparecer no texto de entrada e que devem ser ignorados
t_ignore = " \n\t"

# declaração da ação a fazer relativa aos Carateres que NÃO podem aparecer no texto de entrada
def t_error(t):
    print("Carater ilegal: ", t.value)


lexer = lex.lex()

if __name__ == "__main__":
    for line in sys.stdin:
        lexer.input(line)
        tok = lexer.token()
        while tok:
            print(tok)
            tok = lexer.token()
