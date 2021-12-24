import ply.lex as lex
import sys

tokens = ["SEP", "REAL", "INT", "WORD", "TRUE", "FALSE", "LP", "RP"]

# declaração das Palavras-Reservadas e dos Simbolos de Classe (variáveis)
t_LP = r"\("
t_RP = r"\)"
t_SEP = r"[;,]"


def t_TRUE(t):
    r"True"
    return t


def t_FALSE(t):
    r"False"
    return t


def t_WORD(t):
    r"[a-zA-Z]+"
    return t


def t_REAL(t):
    r"([1-9][0-9]*\.[0-9]+|0\.[0-9]+)"
    return t


soma = 0


def t_INT(t):
    r"[0-9]+"
    global soma
    soma += int(t.value)
    return t


# declaração dos Carateres que podem aparecer no texto de entrada e que devem ser ignorados
t_ignore = " \n\t}{"

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
            # print(f'SOMA: {soma}') #imprime a soma após a leitura de cada token
            tok = lexer.token()
        # print(f'SOMA: {soma}')    #imprime a soma no fim de cada linha
    print(f"SOMA: {soma}")  # imprime a soma só no fim do texto
