---
title: tp2
export_on_save:
  html: true
---

## Organização da Máquina

### Pilhas

2 pilhas:

- Pilha de Execução (valores: Inteiros, Reais, Endereços)
- Pilha de Chamadas: contém pares de apontadores $(i,f)$. O endereço $i$ guarda o registo de instrução $pc$ e $f$ o registo $fp$ .

### Auxiliar

- 1x Zona de Código
- Heaps referenciadas por endereços
  - String Heap
  - Structured Block Heap
    - Contem um certo número de valores (do mesmo tipo dos valores que se podem encontrar na pilha).
- 4x registos

### Endereço

- Pode apontar para 4 tipos de informação:
  1. Código
  2. Pilha
  3. Bloco estruturado
  4. String

### Registo

- $sp$ (stack pointer): aponta para o topo corrente da pilha. Ele aponta para a primeira célula livre da pilha.
- $fp$ (frame pointer): aponta para o endereço de base das variáveis locais.
- $gp$ (global pointer): contem o endereço de base das variáveis globais.
- $pc$ (program counter): aponta para a instrução corrente (da zona de código) por executar.

### Instrução

Aceitam 1 ou 2 parâmetros. Estes podem ser:

- constantes inteiras
- constantes reais
- cadeias de caracteres delimitadas por aspas.
  - Estas cadeias de caracteres seguem as mesmas regras de formatação que as cadeias da linguagem C (em particular no que diz respeito aos caracteres especiais como \", \n ou \\ ),
- uma etiqueta simbólica designando uma zona no código.

### Convenção

- Empilhar um valor x significa colocar o valor x na célula P[sp] e incrementar sp de 1.
- Empilhar n vezes um valor x significa iterar n vezes a operação anterior.
- Retirar, ou tirar da pilha n valor consiste em decrementar de n o valor de sp.
- O topo da pilha representa o último valor colocado na pilha, ou seja P[sp − 1], o valor anterior representa o penúltimo valor, o sub-topo colocado na pilha, ou seja P[sp −2].
- Se x designar um endereço na pilha então x[n] designa um endereço situada n células por cima.

### Comparação

O resultado duma operação de comparação é um inteiro que vale 0 ou 1. O inteiro 0 representa o valor booleano f also enquanto o valor 1 representa o valor verdade.

### Operações

- inf: subtopo < topo
- jz label ≡ if not P[sp-1]: pc = label

## Exemplos

### Exemplos 1

```txt
x,y,z : int

x := 1
y := 2
z := x + y

print(x)
print(y)
print(z)
```

```txt
PUSHN 3

PUSHI 1
STOREG 0

PUSHI 2
STOREG 1

PUSHG 0
PUSHG 1
ADD
STOREG 2

PUSHG 0
WRITEI

PUSHG 1
WRITEI

PUSHG 2
WRITEI
```

### 1 - ler 4 números e dizer se podem ser os lados de um quadrado

```lisp
(do
    (decl
        (a b c d int)
    )

    (let
        (a readInt)
        (b readInt)
        (c readInt)
        (d readInt)
    )

    (case (= a b)
        1 (case (= a c)
                1 (case (= a d)
                        1 (print "Pode ser")
                        0 (print "Nao da")
                     )
                0 (print "Nao da")
             )
        0 (print "Nao da")
    )

    (ladosDoQuadrado a b c d)
)
```

```txt
// (decl (a b c d int))
PUSHN 4

// (let (a readInt))
READ
ATOI
STOREG 0

// (let (b readInt))
READ
ATOI
STOREG 1

// (let (c readInt))
READ
ATOI
STOREG 2

// (let (d readInt))
READ
ATOI
STOREG 3

pushg 0
pushg 1
equal

jz e1

pushg 0
pushg 2
equal
jz e3
<case 3>
jump e4

e4:
<>

jump e2

e1:
<nao da>

e2:
<apos case 1>
```

### 2 - ler um inteiro N, depois ler N números e escrever o menor deles

```c
#include <stdio.h>

int main()
{
    int n,num, min, i;
    min = 0;
    i = 0;
    printf("How many numbers you want to read: ");
    scanf("%d",&n);
    while(i<n){
         printf("Insert your number: ");
         scanf("%d",&num);
         if(i == 0) min = num;
         if(min > num) min = num;
         i++;
    }
    printf("Min Value: %d\n",min);
    return 0;
}
```

```lisp
(do
    (decl
        (n num min i int)
    )

    (let
        (min 0)
        (i 0)
        (n readInt)
    )

    (while (< i n)
        (let (num readInt))
        (case (= i 0) (True (let (min num))))
        (case (> min num) (True (let (min num))))
        (let (i (add i 1)))
    )

    (writei min)
)
```

```txt
// int n,num,min,i;
PUSHN 4

START

//min = 0;
PUSHI 0
STOREG 2 // min

//i = 0;
PUSHI 0
STOREG 3 // i

// scanf("%d",&n);
READ
ATOI
STOREG 0 //n

E0:
// i < n
PUSHG 3
PUSHG 0
INF

JZ E1
// scanf("%d",&num);
READ
ATOI
STOREG 1

// if(i == 0) min = num
PUSHG 3
PUSHI 0
EQUAL
JZ E3
PUSHG 1
STOREG 2
E3:
// if (min > num) min = num;
PUSHG 2
PUSHG 1
SUP
JZ E4
PUSHG 1
STOREG 2
E4:

// i++
PUSHG 3
PUSHI 1
ADD
STOREG 3

JUMP E0
E1:

//printf("Min Value: %d\n",min);
PUSHG 2
WRITEI
STOP
```

### 3 - ler N (constante do programa) números e calcular e imprimir o seu produtório

```c
#include <stdio.h>

int main()
{
    int i,n,p,num;
    p = 1;
    printf("How many numbers you want to read: ");
    scanf("%d",&n);
    for(i= 1;i<=n;i++){
     scanf("%d",&num);
     p *= num;
    }
  printf("The result is  %d\n", p);
    return 0;
}
```

for(i=1;i<=n;i++) ≡ i:=1;while(i ≤ n) {…;i++};

```lisp

(do
  (decl
    (n p i num int)
  )

  (let
    (p 1)
    (n readInt)
  )

  (let (i 0))
  (while (<= i n)
    (let (num readInt))
    (let (p (* p num)))
    (let (i (add i 1)))
  )

  (print p)

)

```

```txt
// int i,n,p,num;
pushn 4

// p = 1;
pushi 1
storeg 2

// scanf("%d",&n);
read
atoi
storeg 1

// i = 0;
pushi 1
storeg 0

e0: // start cycle
// i ≤ n
pushg 0
pushg 1
infeq

jz e1 // end cycle if condition is false

// scanf("%d",&num);
read
atoi
storeg 3

// p *= num
pushg 2
pushg 3
mul
storeg 2

// i++
pushg 0
pushi 1
add
storeg 0

// re-cycle
jump e0

e1:
// (print p)
pushg 2
writei
```

### 4 - contar e imprimir os números impares de uma sequência de números naturais

```c
#include <stdio.h>
#include <stdlib.h>

int main() {

    int i, size;

    printf("How many numbers you want to read: ");
    scanf("%d",&size);

    int num2[size];


    for(i = 0; i < size; i++){
        printf("Enter the position element %d: ", i);
        scanf("%d", &num2[i]);
    }

    printf("\n\n");
    for(i = 0; i < size; i++)
        if (num2[i] %2!=0)  printf(" %d ", num2[i]);

    return 0;
}
```

```txt
// int i, size;
pushn 2

// scanf("%d",&size);
read
atoi
storeg 1

// int num2[size];
pushg 1
allocn
```

$$
\DeclareMathOperator{\CASE}{\color{blue}{case}}
\newcommand{\IF}[2]{\operatorname{\color{blue}{if}}\ #1\!:\\\qquad{#2}}
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
\IF{v = v_1}{\EVAL c_1}\\
\ELIF{v = v_2}{\EVAL c_2}\\[.5em]
\qquad\vdots\\[.5em]
\ELIF{v = v_n}{\EVAL c_n}\\
\end{array}
$$

Note que "push" não é um comando.

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
