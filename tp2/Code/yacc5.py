import ply.yacc as yacc
import sys
from lex5 import tokens, text, text2

def p_func(p):
   """func : DEF WORD DOUBLE_COLON NEW_LINE IBLOCK"""
   p[0] = p[6]
   print(p[0])

def p_iblocks(p):
    """IBLOCKS : IBLOCK
               | TAB IBLOCKS"""
    p[0] = [p[1]]

def p_iblock(p):
    """IBLOCK : TAB words
              | IBLOCK NEW_LINE IBLOCK"""
    p[0] = [p[1]]

def p_words_word(p):
    """words : words WORD"""
    p[0].append(p[2])

# def p_grammar(p):
#     """
#     func : DEF WORD DOUBLE_COLON NEW_LINE TAB words

#     words : WORD
#           | words NEW_LINE WORD
#     """


def p_error(p):
    print("Syntax error", p)
    parser.exito = False

parser = yacc.yacc()

parser.parse(text2)
tok = parser.token()
while tok:
    print(tok)
    tok = parser.token()
