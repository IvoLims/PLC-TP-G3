import ply.lex as lex
import sys

tokens = ["REAL", "INT", "ID", "STR" ,"LB", "RB","AT","SC", "WORD"]

# declaração das Palavras-Reservadas e dos Simbolos de Classe (variáveis)
t_LB  = r"\{"
t_RB  = r"\}"
t_AT  = r"\@"
t_SC  = r"\;"

def t_REAL(t):
    r"[0-9]*\.[0-9]+"
    return t

def t_INT(t):
    r"[0-9]+"
    return t

def t_ID(t):
    r"@[-+*/!%^&=.a-zA-Z0-9_]+"
    return t

def t_WORD(t):
    r'[-+*/!%^&=.a-zA-Z0-9_]+'
    return t

def t_STR(t):
    r'"([^"]+|.)*"'
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
