import re
import functools

# Pra ganhar mais pontos:
# https://tex.stackexchange.com/questions/109064/is-there-a-difference-between-and-in-bibtex
# author = {{National Aeronautics and Space Administration}},
#

def main3():
    with open("simp.bib", "r", encoding="utf8") as file:
        string = file.read()
    with open("exemplo-utf8.bib", "r", encoding="utf8") as file:
        string2 = file.read()
    # Sem essa substituicao iremos entrar em loop
    return get_entries(re.sub(r'\b}',r' }',string2))


def get_entries(string):
    """Creates a dictionary with the following map
       (type of publication,citation-key) → {field:field_value}"""
    # Pega titulos com chaveta dentro de chaveta, mantendo chavetas.
    # Elas sao removidas mais tarde.
    d = {}
    # oldregex = r'(\w+)\s*=\s*(?:{((?:.|\n)+)}|"(([^"]|\n)+)"|(\d+))(?:,\n|\n})'
    # up to 2 levels of curly brace nesting based on:
    # https://stackoverflow.com/questions/546433/regular-expression-to-match-balanced-parentheses
    # @(\w+){(\w+),((?:[^{}]+|{(?:[^{}]*|{[^{}]*})+})+)
    field = re.compile(r'(\w+)\s*=\s*(?:{((?:[^{}]+|{(?:[^{}]+|{[^{}]*})+})+)}|"([^"]+)"|(\d+))')
    for entry in re.finditer(r"@(\w+){(\w+),((?:[^{}]+|{(?:[^{}]*|{[^{}]*})+})+)", string):
        d[entry.group(1).lower(), entry.group(2)] = {
            x[0].lower(): get_valid_group(x, 1, 3)
            for x in field.findall(entry.group(3))}
    return d

def get_valid_group(t, begin_or_group, end_or_group):
    # This exists because we have 3 groups when matching a field content:
    # The content needs to be enclosed by either curly braces or quotation-marks.
    # Additionally numbers can stand alone.
    for i in range(begin_or_group, end_or_group + 1):
        if v := t[i]:
            return v

def unbrace(expression):
    """Assumes balanced braces.
       Removes braces from expression
       According to https://tex.stackexchange.com/questions/109064/is-there-a-difference-between-and-in-bibtex:

       Braces inside a title are used to
       prevent words in title fields from being converted to lowercase
       if "sentence style" (as is the case with many bibliography styles)
       rather than "title style" typesetting is in effect.

       E.g., you should use curly braces to write
       title = "The Life of {Albert} {Einstein}",

       or, equivalently,

       title = {The life of {Albert} {Einstein}},

       to ensure that the letters "A" and "E" will
       always be typeset in uppercase mode even if "sentence style"
       is in effect."""
    return expression.translate({ord(x):None for x in '{}'})


def get_author_list(data):
    return sorted(set([a for s in data.values() for a in s.get("author", [])]))

def invert_name(author_name):
    '''Inverte nome do tipo: last_name, first_name.
       Por exemplo: da Cruz, Daniela → Daniela da Cruz'''
    return re.sub(r"([^,]+),\s*([^,]+)", r"\2 \1", author_name)

# Expression is in any given language. Latex, html expression
# It's not just a simple string.

def remove_latex_special_chars(latex_expression):
    return re.sub(r'\\({|[^{])\b',r'\1',latex_expression)

def str_to_html_small_caps(expression):
    return html_to_small_caps(html_create_span(expression))

def html_create_span(expression):
    return html_enclose('span',expression)

def html_enclose(tag,string):
    # Funcao mais geral
    return rf'<{tag.upper()}>{string}</{tag.upper()}>'

def html_to_small_caps(html_expression):
    '''Usado para converter expressoes latex \\textsc{expression}'''
    return html_add_attr('style','font-variant:small-caps',html_expression)

def html_to_sans_serif(html_expression):
    return html_add_attr('style','font-family:sans-serif',html_expression)

def html_add_attr(attr,val,html_expression):
    # Funcao mais geral
    return re.sub(r'<(\w+)([^>]*)\s*>(.*)</\1>',rf'<\1\2 {attr.upper()}="{val}">\3</\1>',html_expression)

def question_b_view(data):
    string_ls = [html_enclose('h2','Category Index')]
    for entry_type in set(x[0] for x in data):
        string_ls.append(html_enclose('h3',entry_type))
        for citation_key in [x[1] for x in data if x[0]==entry_type]:
            title = data[entry_type,citation_key].get('title','')
            authors = ', '.join((sorted(data[entry_type,citation_key].get('author',''))))
            string_ls.append(html_enclose('p',f"Key = {citation_key}<br>Title = {fix_title(title)}<br>Autores = {authors}"))
    return '\n'.join(string_ls)

def str_to_html_math(string):
    return html_add_attr('class','math inline',html_create_span(string))

def compose2(f, g):
    return lambda *a, **kw: f(g(*a, **kw))

def compose(*fs):
    return functools.reduce(compose2, fs)

def fix_title(title):
    # Nao e necessario remover acentos.
    # So o fazemos por consistencia com o nome dos autores.
    # <p><span class="math inline">\(T_2O\)</span></p>
    substitutions = [(r'\\textsc{((?:\\{|[^{])+)}',lambda m: f'{html_to_small_caps(html_create_span(m.group(1)))}'),
                     (r'\\textsf{((?:\\{|[^{])+)}',lambda m: f'{html_to_sans_serif(html_create_span(m.group(1)))}'),
                     (r'(\$(?:.|\\\$)+\$)', lambda m: f'{str_to_html_math(m.group(1))}')]


    replace = lambda x: mult_replace(x,substitutions)

    return   html_create_span(
             unbrace(#Pode dar problema com expressoes matematicas. Para melhorar devemos fazer if not between $.
             replace(
             remove_latex_special_chars(
             remove_accents(
             ' '.join(s.strip() for s in title.split('\n')))))))


def mult_replace(string, replacement_list):
    '''Uses a list of regex substitutions to modify a string'''
    for old, new in replacement_list:
        string = re.sub(old, new, string)
    return string



def fix_repeated_authors(data):
    author_blocks = fix_block_func(block_authors_with_two_common_names_v2(get_author_list(data)))
    author_dict = {author_name:max(s,key=len) for s in author_blocks for author_name in s}
    for d in data.values():
        d['author'] = [author_dict[author] for author in d['author']]

def format_authors(data):
    '''Escolhemos remover acentuações e caracteres especiais
       que as representam em latex (e.g. "\\~") do nome dos autores.'''
    for d in data.values():
        if "author" in d:
            author_lst = [ remove_consecutive_spaces(
                           str.strip(
                           invert_name(
                           unbrace(
                           remove_accents(name)))))
                           for name in re.split(r"\band\b", d["author"].replace("\n", " "))]
            d['author'] = [author for author in author_lst if author]


def remove_consecutive_spaces(name):
    return re.sub(r'\s+',' ',name)

def remove_accents(name):
    return remove_latex_accent(remove_normal_accent(name))

def remove_latex_accent(name):
    return re.sub(r'\\\W','',name)

def remove_normal_accent(name):
    import unicodedata
    # https://en.wikibooks.org/wiki/LaTeX/Special_Characters
    # re.sub(r'\\{?(acento)}?',rf'{fix_accent(\1)}',author_name)
    return ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))

# 2 comuns
# 'Pedro Henriques', - ph
# 'Pedro R. Henriques', - prh
# 'Pedro Rangel Henriques', - prh
# 'P. Henriques', - ph
# 'P. Rangel Henriques', - prh
# 'P.R. Henriques', - prh

# hipotetico -- 'J. Varanda'
# 3 nomes comuns
# 'M. J. Varanda' - mjv
# 'M. Joao Varanda' - mjv
# 'Maria Joao Varanda' - mjv
# 'Maria Joao V. Pereira' - mjvp
# hipotetico -- 'Maria Joao Pereira'

# dois nomes comuns
# 'Ricardo Henriques', - rh
# 'M.R. Henriques', - mrh
# 'Mario Ricardo Henriques', - mrh

# ivo miguel lima - iml
# miguel lima - ml
# ivo lima - il
# ivo miguel pereira - imp

# alguns casos serao impossiveis:
# m. pinto
# m. pinto
# mario pinto
# maria pinto

# 'Matej Crepinsek' - mc
# 'Marcirio Chaves' - mc

# 2 nomes comuns em ordem
# Omitir nome do meio

# Estao como diferentes:
# L.F. Neves
# F.L. Neves

def last_name_first(name):
    '''Recebe um nome normalizado (e.g.
       Pedro Filipe H. Pereira) e deve
       retornar "invertido" (e.g.
       Pereira, P. F. H.'''
    initials =  '. '.join(get_crude_abbrev(name))[:-2]
    last_name = name.split()[-1]
    return f'{last_name}, {initials}'


def get_author_index_dict(data):
    index = {}
    for key, e in data.items():
        if 'author' in e:
            for author in e['author']:
                author_name = last_name_first(author)
                if author_name not in index:
                    index[author_name] = set()
                index[author_name].add(key[1]) #key[1] is the citation-key
    return index

def get_html_author_index(data):
    index = sorted(get_author_index_dict(data).items())
    alphabet_order = sorted(set(c[0][0] for c in index))
    string_ls = [html_enclose('h2','Author Index')]
    i = 0
    for author,citation_keys in index:
        if author[0] != alphabet_order[i]:
            i += 1
            string_ls.append(html_enclose('h3',alphabet_order[i]))
        citation_keys_str = ', '.join(citation_keys)
        string_ls.append(html_enclose('p',f'{author}, {citation_keys_str}'))
    return ''.join(string_ls)


def test_get_html_author_index():
    return get_html_author_index(data)

def get_crude_abbrev(name):
    '''Transforma um nome de autor nas primeiras letras
       de cada um de seus nomes.

       Por exemplo: Ricardo Henriques → RH'''
    return ''.join(c for c in name if c.isupper())

def transform(authors):
    '''Retorna das abreviacoes dos autores.'''
    d = {}
    for author in authors:
        crude_abbrev = get_crude_abbrev(author)
        if crude_abbrev not in d:
            d[crude_abbrev] = set()
        d[crude_abbrev].add(author)
    return d

def is_a_first_last_match(author1,author2):
    '''returns true if first letter of first name
       and first letter of last name of author 1
       matches first letter of first name
       and firfst letter of last name of author 2
       respectively'''
    a1 = get_crude_abbrev(author1)
    a2 = get_crude_abbrev(author2)
    return a1[0] == a2[0] and a1[-1] == a2[-1]

def block_authors_with_two_common_names(authors):
    # Resquicios historico, essa funcao nao e usada.
    # Mas e util para enteder o comportamento de block_authors_with_two_common_names_v2
    # quando fomos otimiza-la.
    res = set()
    for author in authors:
        fs = set()
        for author2 in authors:
            if len(set(re.findall(r'\w\w+',author)).intersection(re.findall(r'\w\w+',author2))) > 1:
                fs.add(author2)
        # Names which have only on non-abbreviated word
        if not fs:
            print(author)
        res.add(frozenset(fs))
    return res

def block_authors_with_two_common_names_v2(authors):
    '''Objetivo: Criar "blocos" com nomes dos autores,
       quem estiver no mesmo "bloco", é a mesma pessoa.'''
    res = set()
    for author in authors:
        fs = set()
        for author2 in authors:
            a1 = set(re.findall(r'\w\w+',author))
            a2 = set(re.findall(r'\w\w+',author2))
            if len(a1.intersection(a2)) > 1:
                fs.add(author2)
            # Caso especial: so tem um nome que nao esta abreviado (e.g. P. Henriques)
            # Suponha que autor 1 é esse caso especial.
            # Nesse caso, se o segundo autor tiver esse nome, vamos dizer que são a mesma pessoa
            # segundo as condicoes definidas em is_a_first_last_match(), checar comentario.
            elif len(a1) == 1 and len(a1.intersection(a2)) == 1 and is_a_first_last_match(author,author2):
                fs.add(author2)
        # Usamos frozenset porque queremos colocar um conjunto em res.
        # Queremos que res seja um conjunto, ao inves de uma lista,
        # porque da outra forma iriamos terminar com "blocos" de autores repetidos.
        # Ou seja, fazer res ser um conjunto de conjuntos (frozenset)
        # foi a maneira rapida que encontrei de evitar "blocos" de autores duplicados.
        # Eu enfatizo "blocos" ao inves de conjunto, porque talvez tenha outra estrutura
        # que conseguia crie esses blocos como listas de forma funcional.
        res.add(frozenset(fs))
    return res

def fix_block_func(data):
    '''Objetivo: Criar transitividade nos autores.
       Sem essa funcao, temos blocos {A,B} e {B,C}
       Depois dessa funcao, vamos ter {A,B,C}'''
    res = set()
    for s1 in data:
        q = s1.copy()
        for s2 in data:
            if s1.intersection(s2) != set():
                q = q.union(s2)
        # Evitar "blocos" de autores repetidos.
        # Para mais detalhes, ver comentario em frozenset
        # em block_authors_with_two_common_names_v2()
        res.add(frozenset(q))
    return res


def test_data_view():
    data = main3();format_authors(data); authors = get_author_list(data);authors_abbrev = sorted([transform(name) for name in authors],key=len,reverse=True)
    fix_repeated_authors(data)
    return question_b_view(data)

data = main3()
format_authors(data)
fix_repeated_authors(data)
authors = get_author_list(data)

aut = fix_block_func(block_authors_with_two_common_names_v2(authors))
block_authors_with_two_common_names(authors)
