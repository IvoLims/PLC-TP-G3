# Relatório

Para realizar as modificações em um ficheiro chamamos `solve(author_name,INPUT_FILENAME=BIB_EXAMPLE_FILENAME)`, passando o nome do autor que queremos conforme (R5).

```python, echo = False
#!/usr/bin/python
```

## Módulo não é `re`

Usamos o módulo `regex` que é um _superset_ de `re` mais poderoso. Seu uso será justificado.

```python
import regex as re
```

## Algumas constantes

```python
HTML_PROLOGUE = '''<!DOCTYPE  html>
    <HTML lang="en">
        <HEAD>
            <meta charset="utf-8">
            <TITLE>Categories in BibTeX</TITLE>

            <script type="text/x-mathjax-config"> MathJax.Hub.Config({"extensions":["tex2jax.js"],"jax":["input/TeX","output/HTML-CSS"],"messageStyle":"none","tex2jax":{"processEnvironments":false,"processEscapes":true,"inlineMath":[["$","$"]],"displayMath":[]},"TeX":{"extensions":["AMSmath.js","AMSsymbols.js","noErrors.js","noUndefined.js"]},"HTML-CSS":{"availableFonts":["TeX"]}}); </script>

            <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js"></script>
        </HEAD>'''
```

Famos ter que fechar a tag HTML que começamos em `HTML_PROLOGUE`
```python
HTML_EPILOGUE = '</HTML>'
```

O ficheiro dado como argumento de entrada é o ficheiro `exemplo-utf8.bib`.

```python
BIB_EXAMPLE_FILENAME = "exemplo-utf8.bib"
```

Decidimos chamar o output como `output.html`.

```python
OUTPUT_FILENAME = 'output.html'
```

Aqui incluimos javascript para renderizar fórmulas matemáticas.

## Função principal

Em `solve` temos a váriavel `htlm_str_ls` que é uma lista de strings que iremos concatenar. Usamos uma lista ao invés de ir concatenando uma váriavel string porque em python strings são imutáveis, cada concatenação requer que todos os caracteres sejam copiados. Por outro lado, appends numa lista são $\cal{O}(1)$ e no final concatenamos só uma vez as strings na lista para formar o código html.

Em `bib_str` salvamos o texto inteiro que está em `INPUT_FILENAME`. `get_bib_str()` é utilizada para abrir o ficheiro.g

```python
def solve(author_name,INPUT_FILENAME=BIB_EXAMPLE_FILENAME):
    html_str_ls = [HTML_PROLOGUE]
    bib_str = get_bib_str(INPUT_FILENAME)

    entries = get_entries(bib_str)
    format_authors(entries)
    fix_repeated_authors(entries)

    html_str_ls.append(html_enclose('body',f'{get_html_pub_type_counts(entries)}{get_html_common_pub_author(author_name,entries)}{get_html_pub_type_index(entries)}{get_html_author_index(entries)}'))

    html_str_ls.append(HTML_EPILOGUE)
    with open(OUTPUT_FILENAME,'w') as file:
        file.write('\n'.join(html_str_ls))
```

```python
def get_bib_str(filename):
    with open(filename,'r') as file:
        return file.read()
```

## Apanhando as entradas

Nesse procedimento, criamos um dicionário onde cada chave é um par (tipo de publicação, nome do autor) e o valor é um dicionário em que cada chave é um campo da entrada bibtex e o valor é o valor do campo.

É aqui que se justifica o useo do módulo `regex`. Note a expressão regular:

<<>>=
between_cbrace_ex = r'(?:(?<rec>{(?<value>[^{}]+|(?P>rec))*+}))'
@

Nela usamos um padrão recursivo não suportado pelo módulo `re`. O padrão é usado para capturar o que está entre chavetas que podem estar aninhadas arbitrariamente.

Usamos `RELEVANT_FIELDS` para definir quais campos iremos usar.

```python
def get_entries(string):
    d = {}

    RELEVANT_FIELDS = {'author','title'}
    SPECIAL_TYPES = {'comment','string','preamble'}

    between_cbrace_ex = r'(?:(?<rec>{(?<value>[^{}]+|(?P>rec))*+}))'

    field_match = re.compile(rf'(?<name>\w+)\s*=\s*({between_cbrace_ex}|"(?<value>[^"]+)"|(?<value>\d+))')
    entry_match = re.compile(rf'@(?<type>\w+)(?<value>{between_cbrace_ex})')
    key_match = re.compile(r'([^{},~#%\\]+),')

    for entry in entry_match.finditer(string):
        entry_type = entry['type'].lower()
        if entry_type not in SPECIAL_TYPES:
            key = key_match.search(entry['value'])[1]
            d[entry_type, key] = {
                field['name'].lower(): field['value']
                for field in field_match.finditer(entry['value']) if field['name'].lower() in RELEVANT_FIELDS}
    return d
```

## Procedimentos usados ao longo do programa

### Relacionado a expressões $La\TeX$

Assumimos que as chavetas estão balanceadas. Iremos remover as caveteas baseados na informação achada [aqui](https://tex.stackexchange.com/questions/109064/is-there-a-difference-between-and-in-bibtex:)

Chavetas dentro de títulos são usadas para previnir que palavras sejam convertidas para em letras minúsculas (se "sentence style" é usado ao invés de "title style").

Por exemplo, devemos usar chavetas para escrever

`title = "The Life of {Albert} {Einstein}"`

ou, de forma equivalente,

`title = {The life of {Albert} {Einstein}}`

para garantir que as letras 'A' e 'E' sejam sempre formatadas em letras maiúsculas mesmo que "sentence style" esteja sendo usado.

Suspeitamos que talvez pudessemos usar:

<<>>=
r'[^\\]\$.*[^\\]\$'
@

para identificar que não estamos dando _escape_ no _dollar sign_. Mas já tinhamos esse procedimento feito e dicimos por não alterá-lo.

```python
def unbrace(expression):
    string_ls = []
    is_between_dollar_sign = False
    is_previous_backslash = False
    for c in expression:
        if c == '$' and not is_previous_backslash:
            if is_between_dollar_sign:
                is_between_dollar_sign = False
            else:
                is_between_dollar_sign = True
        if c == '\\':
            is_previous_backslash = True
        else:
            is_previous_backslash = False
        if c in '{}' and not is_between_dollar_sign:
            continue
        string_ls.append(c)
    return ''.join(string_ls)
```

### Relacionados a _HTML_

É muito comum em _HTML_ o uso de _tags_ para marcar uma expressão. Então criamos um procedimento que facilita colocar cercar uma expressão pela _tag_ desejada.

```python
def html_enclose(tag,string):
    return rf'<{tag.upper()}>{string}</{tag.upper()}>'
```

Nesse sentido, _spans_ são muito úteis em _HTML_, logo criamos:

```python
def html_create_span(expression):
    return html_enclose('span',expression)
```

As vezes queremos adicionar um atributo numa _tag_, nesse caso podemos usar (há um pequeno problema com esse procedimento, mas para nosso uso não foi relevante).

```python
def html_add_attr(attr,val,html_expression):
    return re.sub(r'<(\w+)([^>]*)\s*>(.*)</\1>',rf'<\1\2 {attr.upper()}="{val}">\3</\1>',html_expression)
```

### Relacionados a _Regex_

As vezes queremos fazer várias substituições num texto, logo criamos:

```python
def mult_replace(string, replacement_list):
    for old, new in replacement_list:
        string = re.sub(old, new, string)
    return string
```

## Tratamento do nome dos autores

Escolhemos remover acentuações e caracteres especiais que as representam em $La\TeX$ (e.g. `\~`) do nome dos autores.

É importante notar que ainda ocorrem alguns problemas de acentuações uma vez que não removemos acentuações do tipo `\~{}`.

```python
def format_authors(data):
    for d in data.values():
        if "author" in d:
            author_lst = [ remove_consecutive_spaces(
                           str.strip(
                           invert_name(
                           unbrace(
                           remove_accents(name)))))
                           for name in re.split(r"\band\b", d["author"].replace("\n", " "))]
            d['author'] = [author for author in author_lst if author]
```

### Procedimentos auxiliares

```python
def remove_consecutive_spaces(name):
    return re.sub(r'\s+',' ',name)
```

Para inverte nomes do tipo: last_name, first_name. Por exemplo: "da Cruz, Daniela" → "Daniela da Cruz"

```python
def invert_name(author_name):
    return re.sub(r"([^,]+),\s*([^,]+)", r"\2 \1", author_name)
```

```python
def remove_accents(name):
    return remove_latex_accent(remove_normal_accent(name))
```

Para remoção de acentos $La\TeX$ consultamos a [wiki](https://en.wikibooks.org/wiki/LaTeX/Special_Characters).

Pensamos em possivelmente usar algo como:

<<>>=
re.sub(r'\\{?(acento)}?',rf'{fix_accent(\1)}',author_name)
@

para manter acentuações, mas devido a restrições de tempo não achamos prudente embarcar nesta ideia.

```python
def remove_latex_accent(name):
    return re.sub(r'\\\W','',name)
```

Aqui removemos palavras com acentuações normais, isso é, palavras como "á", "é", "í", etc (não $La\TeX$).

```python
def remove_normal_accent(name):
    import unicodedata
    return ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
```

Também usamos a já referenciada `unbrace()`.

## Tratando autores repetidos na estrutura

No nosso dicionário, teremos autores repetidos (pois podem estar escritos de formas diferentes, omitindo alguns sobrenomes ou até mesmo primeiros nomes).

```python
def fix_repeated_authors(data):
    author_blocks = fix_block_func(block_authors_with_two_common_names_v2(get_author_list(data)))
    author_dict = {author_name:max(s,key=len) for s in author_blocks for author_name in s}
    for d in data.values():
        d['author'] = [author_dict[author] for author in d['author']]
```

Para lidar com isso, realizamos três procedimentos:

1. Obtemos uma lista dos autores ordenada alfabéticamente.
2. Criamos conjuntos onde seus elementos representam um mesmo autor. Ou seja, se temos três nomes: $A$, $B$ e $C$ e temos os conjuntos $\{A,B\}$ e $\{B,C\}$, então os nomes $A,B,C$ referem o mesmo autor.
3. Juntamos esses blocos para que cada bloco seja um único autor. Ou seja, determinamos uma "transitividade" nos blocos, usando o exemplo anterior, se temos $\{A,B\}$ e $\{B,C\}$, devemos obter $\{A,B,C\}$.

### Procedimento 1

```python
def get_author_list(data):
    return sorted(set([a for s in data.values() for a in s.get("author", [])]))
```

### Procedimento 2

```python, evaluate = False
def block_authors_with_two_common_names_v2(authors):
    res = set()
    for author in authors:
        fs = set()
        for author2 in authors:
            a1 = set(re.findall(r'\w\w+',author))
            a2 = set(re.findall(r'\w\w+',author2))
```

Se os autores tem mais de duas componentes do nome em comum, então podemos considerar eles como um mesmo autor.

```python, evaluate = False
            if len(a1.intersection(a2)) > 1:
                fs.add(author2)
```

Caso especial: Suponha que existe um autor que só tem uma componente do nome não abreviada (e.g. P. Henriques). Suponha que outro autor (e.g. P.R. Henriques) também só tem uma componente do nome não abreviada e essa componente é igual a do primeiro autor. Então ainda temos que fortalecer a condição para que sejam considerados iguais. Para isso, usamos `is_a_first_last_match()` garantido que pelo menos a abreciação da primeira componente dos nomes sejam iguais.

```python, evaluate = False
            elif len(a1) == 1 and len(a1.intersection(a2)) == 1 and is_a_first_last_match(author,author2):
                fs.add(author2)
        res.add(frozenset(fs))
    return res
```

Pra implementar `is_a_first_last_match()` usamos `get_crude_abbrev` para obter uma string com o primeiro caractere de cada componente do nome de um autor (e.g. "Ricardo Henriques → RH").

```python
def get_crude_abbrev(name):
    return ''.join(c for c in name if c.isupper())
```

Aqui iremos verificar se os primeiros caracteres da primeira componente e última componente do nome de um autor $a_1$ são iguais, respectivamente, aos primeiros e últimos caracteres da primeira e última componente do nome de um autor $a_2$.

```python
def is_a_first_last_match(author1,author2):
    a1 = get_crude_abbrev(author1)
    a2 = get_crude_abbrev(author2)
    return a1[0] == a2[0] and a1[-1] == a2[-1]
```

### Procedimento 3

Objetivo: Criar a "transitividade" nos blocos dos autores referenciada no ínicio.


```python
def fix_block_func(data):
    res = set()
    for q in data:
        for s2 in data:
            if q.intersection(s2) != set():
                q = q.union(s2)
        res.add(frozenset(q))
    return res
```

## Contagem dos tipos de publicações

Conforme $\text{(R1)}$, devemos contar quantas publicações de cada tipo existem.

```python
def get_pub_type_counts(data):
    pub_types_occur = [x[0] for x in data.keys()]
    pub_types = set(pub_types_occur)
    return [(pub_type, pub_types_occur.count(pub_type)) for pub_type in pub_types]
```

Conforme $\text{(R2)}$ queremos incorporar a contagem de publicações de cada tipo no documento HTML que iremos produzir.

```python
def get_html_pub_type_counts(data):
    string_ls = [html_enclose('h2','Number of Occurrences of Publication Types')]
    pub_counts = sorted(get_pub_type_counts(data),key=lambda x: x[1],reverse=True)
    time = lambda v: 's' if v > 1 else ''
    for pub_type, count in pub_counts:
        string_ls.append(html_enclose('p',f'Type {pub_type} appears {count} time{time(count)}'))
    return ''.join(string_ls)
```


## Criação do grafo

Conforme (R5) queremos constuir um grafo que represente a co-autoria entre os autores.

```python

def get_author_pub_graph(author,data):
    pub_partners = []
    for entry in data.values():
        if 'author' in entry and author in entry['author']:
            for partner in entry['author']:
                if partner != author:
                    pub_partners.append(partner)
    return [(author_name,pub_partners.count(author_name))
            for author_name in set(pub_partners)]
```

Conforme (R6) iremos recorrer a linguagem _Dot_ para renderizar o grafo.

```python
def get_dot_graph(author,data):
    import textwrap
    g = sorted(get_author_pub_graph(author,data),key = lambda x: x[1])
    string_ls = ['graph{']
    string_ls2 = []
    for partner_author,no_joint_pub in g[-3:]:
        string_ls2.append(f'"{author}" -- "{partner_author}" [label="{no_joint_pub}"]')
    string_ls.append(textwrap.indent('\n'.join(string_ls2),'  '))
    string_ls.append('}')
    return '\n'.join(string_ls)
```

Como ideia nossa para ir além do que foi pedido, decidimos incorporar o grafo no documento HTML que iremos produzir.

Utilizamos `re.search()` porque o arquivo gerado contém um preâmbulo _XML_ como _doctype_. Só queremos o _SVG_.

```python
def get_html_dot_svg(author,data):
    import os
    DOT_INPUT_FILENAME = 'dot_input'
    with open(DOT_INPUT_FILENAME,'w') as file:
        file.write(get_dot_graph(author,data))
    os.system(f'dot -T svg -O {DOT_INPUT_FILENAME}')
    with open(DOT_INPUT_FILENAME + '.svg','r') as file:
        return re.search(r'<svg(?:.|\n)+</svg>',file.read()).group()
```

Finalmente,

```python
def get_html_common_pub_author(author,data):
    string_ls = [html_enclose('h2','Author Graph')]
    string_ls.append(get_html_dot_svg(author,data))
    return ''.join(string_ls)
```

## Filtrar (chave,autore,título)

### Títulos

Pelo (R3.3), devemos incluir títulos. Para isso devemos aplicar um tratamento para uma formatação mais elegante (como manter expressões $La\TeX$).

Note que formatmos _small caps_ como pode ser notado em entradas que contém "Camila". Também formatoms _sans serif_ e algumas expressões matemáticas.

```python
def fix_title(title):
    substitutions = [(r'\\textsc{((?:\\{|[^{])+)}',lambda m: f'{html_to_small_caps(html_create_span(m.group(1)))}'),
                     (r'\\textsf{((?:\\{|[^{])+)}',lambda m: f'{html_to_sans_serif(html_create_span(m.group(1)))}'),
                     (r'(\$(?:.|\\\$)+\$)', lambda m: f'{str_to_html_math(m.group(1))}')]


    replace = lambda x: mult_replace(x,substitutions)

    return   html_create_span(
             single_quote_latex(
             double_quote_latex(
             unbrace(
             replace(
             remove_latex_special_chars(
             ' '.join(s.strip() for s in title.split('\n'))))))))
```

#### Tratamento de caracteres $La\TeX$

```python
def double_quote_latex(expression):
    return re.sub(r"``(.*[^\\])''",r'"\1"',expression)
```

```python
def single_quote_latex (expression):
    return re.sub(r"[^`]`([^`].*[^'])'[^`]",r"'\1'",expression)
```

```python
def remove_latex_special_chars(latex_expression):
    return re.sub(r'\\({|[^{])\b',r'\1',latex_expression)
```

### Formatações especiais

#### Small caps


Usado para converter expressoes latex `\textsc{expression}`

```python
def html_to_small_caps(html_expression):
    return html_add_attr('style','font-variant:small-caps',html_expression)
```

Para incluir no _HTML_:

```python
def str_to_html_small_caps(expression):
    return html_to_small_caps(html_create_span(expression))

```

#### Sans serif

```python
def html_to_sans_serif(html_expression):
    return html_add_attr('style','font-family:sans-serif',html_expression)
```

#### Matemática

```python
def str_to_html_math(string):
    return html_add_attr('class','math inline',html_create_span(string))
```

### Incorporar no docmuento _HTML_

Conforme (R3.4):

```python
def get_html_pub_type_index(data):
    string_ls = [html_enclose('h2','Publication Type Index')]
    for entry_type in sorted(set(x[0] for x in data)):
        string_ls.append(html_enclose('h3',entry_type))
        for citation_key in [x[1] for x in data if x[0]==entry_type]:
            title = data[entry_type,citation_key].get('title','')
            authors = ', '.join((sorted(data[entry_type,citation_key].get('author',''))))
            string_ls.append(html_enclose('p',f"Key = {citation_key}<br>Title = {fix_title(title)}<br>Autores = {authors}"))
    return '\n'.join(string_ls)
```

## Índice de autores

Conforme (R4) iremos criar um índice de autores.

Primeiro queremos formatar os nomes para que tenham o apelido aparecendo primeiro, como é comum nos índices de autores. Com esse propósito, criamos o procedimento:

Esse procedimento recebe um nome normalizado (e.g. Pedro Filipe H. Pereira) e deve retornar "invertido" (e.g. Pereira, P. F. H.).

```python
def last_name_first(name):
    initials =  '. '.join(get_crude_abbrev(name))[:-2]
    last_name = name.split()[-1]
    return f'{last_name}, {initials}'
```

Utilizamos `last_name_first()` na construção de um dicionário que irá conter como chaves o nome do autor já formatado e como valor todas as chaves de citações de suas publicações.

```python
def get_author_index_dict(data):
    index = {}
    for key, e in data.items():
        if 'author' in e:
            for author in e['author']:
                author_name = last_name_first(author)
                if author_name not in index:
                    index[author_name] = set()
                index[author_name].add(key[1])
    return index
```

Decidimos incorporar o índice no documento HTML que iremos produzir.

```python
def get_html_author_index(data):
    index = sorted(get_author_index_dict(data).items())
    alphabet_order = sorted(set(c[0][0] for c in index))
    string_ls = [html_enclose('h2','Author Index')]
    i = 0
    string_ls.append(html_enclose('h3',alphabet_order[i]))
    for author,citation_keys in index:
        if author[0] != alphabet_order[i]:
            i += 1
            string_ls.append(html_enclose('h3',alphabet_order[i]))
        citation_keys_str = ', '.join(citation_keys)
        string_ls.append(html_enclose('p',f'{author}, {citation_keys_str}'))
    return ''.join(string_ls)
```

## Chamar pela linha de comando

Isso serve para podermos chamar pela linha de comando.

```python, evaluate = False
if __name__ == '__main__':
    import sys
    import os.path
    filename = sys.argv[1] if len(sys.argv) > 1 else BIB_EXAMPLE_FILENAME
    assert os.path.isfile(filename)
    if len(sys.argv) < 3:
        author_name = 'Daniela da Cruz'
    else:
        author_name = sys.argv[2]
    solve(author_name,filename)

```