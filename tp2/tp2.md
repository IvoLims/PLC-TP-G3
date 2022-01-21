---
title: tp2
export_on_save:
  html: true
---

$
\DeclareMathOperator{\INF}{inf}
\DeclareMathOperator{\JZ}{jz}
\DeclareMathOperator{\NOT}{not}
\DeclareMathOperator{\IF}{if}
\DeclareMathOperator{\JUMP}{jump}
\DeclareMathOperator{\addr}{addressof}
\DeclareMathOperator{\PUSHA}{pusha}
\DeclareMathOperator{\ADD}{add}
$

## Introdução

No âmbito da Unidade Curricular de Processamento de Linguagens e Compiladores foi-nos proposto a construção de um compilador de uma linguagem de programação, de forma a consolidar os conhecimentos adquiridos nas aulas sobre parsing, yacc e gramáticas independentes de contexto. O objetivo deste relatório é aumentar a nossa capacidade de escrever gramáticas, sendo estas independentes de contexto(GIC) ou tradutoras(GT) e   através delas, desenvolver processadores de linguagens segundo o método da tradução.

### Gramática

```txt
<expr> : ID | STR | INT | REAL | <list>
<list> : '(' <seq> ')'
<seq>  : ε | <expr> <seq>
```

### Declaração de variáveis

```lisp
(do
    (decl (x int) (y float) (z str)) `tipos simples`
    (decl (arr array 5)) `array`
    (mdecl mat 2 3) `matriz`
)
```

### Definição de funções

Sintaxe: `defun <nome> <n_args> <n_outs> (<body>)`

```lisp
(do
  (defun readInt 0 1 ((let ($1 (atoi (read))))))
)
```

### Estratégias

#### Ciclo

Para um ciclo simples:

```txt
l0:
<body>
jump l0
```

#### While

Para um ciclo condicional, while por exemplo, temos:

```txt
l0:
<cond>
jz l1
<body>
jump l0
l1:
```

#### If

Para `if ⟨cond⟩ then ⟨c1⟩ else ⟨c2⟩` basta fazer

```txt
⟨cond⟩
jz l0:
⟨c1⟩
jump l1
l0:
⟨c2⟩
l1:
```

##### Case (If dopado)

$$
\DeclareMathOperator{\CASE}{\color{blue}{case}}
\newcommand{\if}[2]{\operatorname{\color{blue}{if}}\ #1\!:\\\qquad{#2}}
\newcommand{\ELIF}[2]{\operatorname{\color{blue}{elif}}\ #1\!:\\\qquad{#2}}
\newcommand{\ELSE}[1]{\operatorname{\color{blue}{else}}\!:\\\qquad{#1}}
% \DeclareMathOperator{\IF}{if}
% \DeclareMathOperator{\ELIF}{elif}
% \DeclareMathOperator{\ELSE}{else}
\DeclareMathOperator{\RETURN}{\color{blue}{return}}
\DeclareMathOperator{\EVAL}{eval}
\newcommand{\NONE}{\textbf{None}}
$$

$$
\begin{array}{lccc}
(\CASE v\\
    &(v_1 && c_1)\\
    &(v_2 && c_2)\\
    &&\vdots\\
    &(v_n && c_n)\\
)
\end{array}
\qquad≡\qquad
\begin{array}{lc}
\if{v = v_1}{\EVAL c_1}\\
\ELIF{v = v_2}{\EVAL c_2}\\[.5em]
\qquad\vdots\\[.5em]
\ELIF{v = v_n}{\EVAL c_n}\\
\end{array}
$$

Note que "push" não é um comando.

```txt
push v

dup 1
push v_1
equal

jz e_2
c_1
jump e_f

e_2:
dup 1
push v_2
equal

jz e_3
c_2
jump e_f
.
.
.
e_n:
dup 1
push v_n
equal

jz e_f
c_n

e_f:
c_f
```

#### Funções

`f ∷ p1,p2,...,pn → r1,r2,...,rk`

```txt
start
pushn k
push pn
push pn-1
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
storel (-n-1)   // rk

return
```

## Organização da Máquina

### Elementos da Máquina

#### Pilhas

2 pilhas:

- Pilha de Execução (valores: Inteiros, Reais, Endereços)
- Pilha de Chamadas: contém pares de apontadores $(i,f)$. O endereço $i$ guarda o registo de instrução $pc$ e $f$ o registo $fp$ .

#### Heaps

2 heaps (são referenciadas por endereços):

- String Heap
- Structured Block Heap
  - Contem um certo número de valores (do mesmo tipo dos valores que se podem encontrar na pilha).

#### Registos

4 registos:

- $sp$ (stack pointer): aponta para o topo corrente da pilha. Ele aponta para a primeira célula livre da pilha.
- $fp$ (frame pointer): aponta para o endereço de base das variáveis locais.
- $gp$ (global pointer): contem o endereço de base das variáveis globais.
- $pc$ (program counter): aponta para a instrução corrente (da zona de código) por executar.

#### Auxiliar

- 1x Zona de Código

### Conceitos

#### Endereço

- Pode apontar para 4 tipos de informação:
  1. Código
  2. Pilha
  3. Bloco estruturado
  4. String

#### Instrução

Aceitam 1 ou 2 parâmetros. Estes podem ser:

- constantes inteiras
- constantes reais
- cadeias de caracteres delimitadas por aspas.
  - Estas cadeias de caracteres seguem as mesmas regras de formatação que as cadeias da linguagem C (em particular no que diz respeito aos caracteres especiais como \", \n ou \\ ),
- uma etiqueta simbólica designando uma zona no código.

### Convenção

- Empilhar um valor `x` ≡ `P[sp]:= x;sp++`
- Empilhar $n$ vezes um valor $x$ ≡ iterar $n$ vezes a operação anterior.
- Retirar, ou tirar da pilha $n$ valor consiste em decrementar de $n$ o valor de $sp$.
- O topo da pilha representa o último valor colocado na pilha, ou seja $P[sp − 1]$, o valor anterior representa o penúltimo valor, o sub-topo colocado na pilha, ou seja $P[sp −2]$.
- Se $x$ designar um endereço na pilha então $x[n]$ designa um endereço situada $n$ células por cima.

### Comparação

\begin{array}{l}
\operatorname{True}  &≡& 1\\
\operatorname{False} &≡& 0
\end{array}

O resultado duma operação de comparação é um inteiro que vale $0$ ou $1$.

### Operações

- $\INF ≡ P[sp-2] < P[sp-1]$
- $\JUMP \textrm{label} ≡ pc:=\addr(\textrm{label})$
- $\JZ \textrm{label}\ ≡\ \IF\ !P[sp-1]: pc = \textrm{label}\ ≈\ \IF\ !P[sp-1]: \JUMP\addr(\textrm{label})$
- $\PUSHA \textrm{label} ≡ \PUSHA \addr(\textrm{label})$
- $\ADD ≡ P[sp-2] + P[sp-1]$
- $\operatorname{STOREN} ≡ P[sp-3][P[sp-2]] := P[sp-1]$ ou seja, addr,pos,value.
- $\operatorname{PADD} ≡ P[sp-2] + P[sp-1]$ onde $P[sp-2] : \textrm{addr}$ e $P[sp-1] : \textrm{INT}$

### Exemplos

#### 1 - ler 4 números e dizer se podem ser os lados de um quadrado

```lisp
(do
    (decl (a int)
          (b int)
          (c int)
          (d int)
    )

    (let (a (atoi (read)))
         (b (atoi (read)))
         (c (atoi (read)))
         (d (atoi (read)))
    )

    (case (mul (equal a b) (mul (equal a c) (equal a d)))
      (1 ((writes "Pode ser")))
    )
)
```

```java
START
PUSHN 1
PUSHN 1
PUSHN 1
PUSHN 1
READ
ATOI
STOREL 0
READ
ATOI
STOREL 1
READ
ATOI
STOREL 2
READ
ATOI
STOREL 3
PUSHL 0
PUSHL 1
EQUAL
PUSHL 0
PUSHL 2
EQUAL
PUSHL 0
PUSHL 3
EQUAL
MUL
MUL
DUP 1
PUSHI 1
EQUAL
JZ l1
PUSHS "Pode ser"
WRITES
JUMP l1
l1:
STOP
```

#### 2 - ler um inteiro N, depois ler N números e escrever o menor deles

```lisp
(do
    (decl
        (n int)
        (num int)
        (min int)
        (i int)
    )

    (let
        (min 0)
        (i 0)
        (n (atoi (read)))
    )

    (while (inf i n)
      (
          (let
            (num (atoi (read)))
          )
          (case (equal i 0)
            (1 ((let
                 (min num)
               ))
            )
          )
        (case (sup min num)
          (1 ((let
                (min num)
              ))
           )
        )
        (let
          (i (add i 1))
        )
      )
    )
    (writei min)
)
```

```txt
START
PUSHN 1
PUSHN 1
PUSHN 1
PUSHN 1
PUSHI 0
STOREL 2
PUSHI 0
STOREL 3
READ
ATOI
STOREL 0
la0:
PUSHL 3
PUSHL 0
INF
JZ la1
READ
ATOI
STOREL 1
PUSHL 3
PUSHI 0
EQUAL
DUP 1
PUSHI 1
EQUAL
JZ l1
PUSHL 1
STOREL 2
JUMP l1
l1:
PUSHL 2
PUSHL 1
SUP
DUP 1
PUSHI 1
EQUAL
JZ l3
PUSHL 1
STOREL 2
JUMP l3
l3:
PUSHL 3
PUSHI 1
ADD
STOREL 3
JUMP la0
la1:
PUSHL 2
WRITEI
STOP
```

#### 3 - ler N (constante do programa) números e calcular e imprimir o seu produtório

```lisp
(do
  (defun readInt 0 1 ((let ($1 (atoi (read))))))
  (decl
    (n int)
    (p int)
    (i int)
    (num int)
  )

  (let
    (p 1)
    (n (call readInt))
  )

  (let (i 0))
  (while (inf i n)
    ((let (num (call readInt)))
    (let (p (mul p num)))
    (let (i (add i 1))))
  )

  (writei p)

)

```

```txt
START
PUSHN 1
PUSHN 1
PUSHN 1
PUSHN 1
PUSHI 1
STOREL 1
PUSHN 1
PUSHA la0
CALL
POP 0
STOREL 0
PUSHI 0
STOREL 2
la1:
PUSHL 2
PUSHL 0
INF
JZ la2
PUSHN 1
PUSHA la0
CALL
POP 0
STOREL 3
PUSHL 1
PUSHL 3
MUL
STOREL 1
PUSHL 2
PUSHI 1
ADD
STOREL 2
JUMP la1
la2:
PUSHL 1
WRITEI
STOP
la0:
READ
ATOI
STOREL -1
RETURN
```

#### 4 - contar e imprimir os números impares de uma sequência de números naturais

```lisp
(do
  (decl (i int) (size int) (num2 array 10))
  (let (i 0) (size 10))

  (while (inf i size) (
        (aset num2 i (atoi (read)))
        (let (i (add i 1)))
    )
  )

  (let (i (sub i 1)))

  (while (supeq i 0) (
        (case (mod (aref num2 i) 2)
            (1 ((writei (aref num2 i))))
        )
        (let (i (sub i 1)))
    )
  )
)
```

```txt
START
PUSHN 1
PUSHN 1
PUSHN 10
PUSHI 0
STOREL 0
PUSHI 10
STOREL 1
la0:
PUSHL 0
PUSHL 1
INF
JZ la1
PUSHGP
PUSHI 2
PADD
PUSHL 0
READ
ATOI
STOREN
PUSHL 0
PUSHI 1
ADD
STOREL 0
JUMP la0
la1:
PUSHL 0
PUSHI 1
SUB
STOREL 0
la2:
PUSHL 0
PUSHI 0
SUPEQ
JZ la3
PUSHGP
PUSHI 2
PADD
PUSHL 0
LOADN
PUSHI 2
MOD
DUP 1
PUSHI 1
EQUAL
JZ l1
PUSHGP
PUSHI 2
PADD
PUSHL 0
LOADN
WRITEI
JUMP l1
l1:
PUSHL 0
PUSHI 1
SUB
STOREL 0
JUMP la2
la3:
STOP
```

#### 5 - ler e armazenar N números num array; imprimir os valores por ordem inversa

```lisp
(do
  (decl (i int) (size int) (num2 array 10))
  (let (i 0) (size 10))
  (defun readInt 0 1 ((let ($1 (atoi (read))))))

  (while (inf i size) (
        (aset num2 i (call readInt))
        (let (i (add i 1)))
    )
  )

  (let (i (sub i 1)))

  (while (supeq i 0) (
        (writei (aref num2 i))
        (let (i (sub i 1)))
    )
  )
)
```

```txt
START
PUSHN 1
PUSHN 1
PUSHN 10
PUSHI 0
STOREL 0
PUSHI 10
STOREL 1
la1:
PUSHL 0
PUSHL 1
INF
JZ la2
PUSHGP
PUSHI 2
PADD
PUSHL 0
PUSHN 1
PUSHA la0
CALL
POP 0
STOREN
PUSHL 0
PUSHI 1
ADD
STOREL 0
JUMP la1
la2:
PUSHL 0
PUSHI 1
SUB
STOREL 0
la3:
PUSHL 0
PUSHI 0
SUPEQ
JZ la4
PUSHGP
PUSHI 2
PADD
PUSHL 0
LOADN
WRITEI
PUSHL 0
PUSHI 1
SUB
STOREL 0
JUMP la3
la4:
STOP
la0:
READ
ATOI
STOREL -1
RETURN
```

#### 6 - invocar e usar num programa seu uma função `potencia()`, que começa por ler do input a base $B$ e o expoente $E$ e retorna o valor $B^E$

```lisp
(do
    (defun pow 2 1 (
        (let (#1 (atoi (read))) (#2 (atoi (read))) ($1 1))
        (while (sup #2 0) (
            (let ($1 (mul $1 #1)) (#2 (sub #2 1)))
        ))
    ))

    (writei (call pow))
)
```

```txt
START
PUSHN 3
PUSHA la0
CALL
POP 2
WRITEI
STOP
la0:
READ
ATOI
STOREL -2
READ
ATOI
STOREL -1
PUSHI 1
STOREL -3
la1:
PUSHL -1
PUSHI 0
SUP
JZ la2
PUSHL -3
PUSHL -2
MUL
STOREL -3
PUSHL -1
PUSHI 1
SUB
STOREL -1
JUMP la1
la2:
RETURN
```

### Primitivas

- `decl ∷ [(WORD,TYPE)]` : Makes the WORDs IDs
- `deprim` : definir função usando código máquina
- `let ∷ [(ID,VALUE)]` : definir algo
- `while ∷ (condition,body) → ()` : executes body if condition = 1
- `case ∷ (v,[(v_i,body_i)]) → ()` : executes body_i if v = v_i

