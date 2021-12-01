#!/usr/bin/python

import regex as re

HTML_PROLOGUE = '''<!DOCTYPE  html>
    <HTML lang="en">
        <HEAD>
            <meta charset="utf-8">
            <TITLE>Categories in BibTeX</TITLE>

            <script type="text/x-mathjax-config"> MathJax.Hub.Config({"extensions":["tex2jax.js"],"jax":["input/TeX","output/HTML-CSS"],"messageStyle":"none","tex2jax":{"processEnvironments":false,"processEscapes":true,"inlineMath":[["$","$"]],"displayMath":[]},"TeX":{"extensions":["AMSmath.js","AMSsymbols.js","noErrors.js","noUndefined.js"]},"HTML-CSS":{"availableFonts":["TeX"]}}); </script>

            <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js"></script>
        </HEAD>'''

HTML_EPILOGUE = '</HTML>'

BIB_EXAMPLE_FILENAME = "exemplo-utf8.bib"

OUTPUT_FILENAME = 'output.html'

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

def get_bib_str(filename):
    with open(filename,'r') as file:
        return file.read()

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

def html_enclose(tag,string):
    return rf'<{tag.upper()}>{string}</{tag.upper()}>'

def html_create_span(expression):
    return html_enclose('span',expression)

def html_add_attr(attr,val,html_expression):
    return re.sub(r'<(\w+)([^>]*)\s*>(.*)</\1>',rf'<\1\2 {attr.upper()}="{val}">\3</\1>',html_expression)

def mult_replace(string, replacement_list):
    for old, new in replacement_list:
        string = re.sub(old, new, string)
    return string

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

def remove_consecutive_spaces(name):
    return re.sub(r'\s+',' ',name)

def invert_name(author_name):
    return re.sub(r"([^,]+),\s*([^,]+)", r"\2 \1", author_name)

def remove_accents(name):
    return remove_latex_accent(remove_normal_accent(name))

def remove_latex_accent(name):
    return re.sub(r'\\\W','',name)

def remove_normal_accent(name):
    import unicodedata
    return ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))

def fix_repeated_authors(data):
    author_blocks = fix_block_func(block_authors_with_two_common_names_v2(get_author_list(data)))
    author_dict = {author_name:max(s,key=len) for s in author_blocks for author_name in s}
    for d in data.values():
        d['author'] = [author_dict[author] for author in d['author']]

def get_author_list(data):
    return sorted(set([a for s in data.values() for a in s.get("author", [])]))

def block_authors_with_two_common_names_v2(authors):
    res = set()
    for author in authors:
        fs = set()
        for author2 in authors:
            a1 = set(re.findall(r'\w\w+',author))
            a2 = set(re.findall(r'\w\w+',author2))

            if len(a1.intersection(a2)) > 1:
                fs.add(author2)

            elif len(a1) == 1 and len(a1.intersection(a2)) == 1 and is_a_first_last_match(author,author2):
                fs.add(author2)
        res.add(frozenset(fs))
    return res

def get_crude_abbrev(name):
    return ''.join(c for c in name if c.isupper())

def is_a_first_last_match(author1,author2):
    a1 = get_crude_abbrev(author1)
    a2 = get_crude_abbrev(author2)
    return a1[0] == a2[0] and a1[-1] == a2[-1]

def fix_block_func(data):
    res = set()
    for q in data:
        for s2 in data:
            if q.intersection(s2) != set():
                q = q.union(s2)
        res.add(frozenset(q))
    return res

def get_pub_type_counts(data):
    pub_types_occur = [x[0] for x in data.keys()]
    pub_types = set(pub_types_occur)
    return [(pub_type, pub_types_occur.count(pub_type)) for pub_type in pub_types]

def get_html_pub_type_counts(data):
    string_ls = [html_enclose('h2','Number of Occurrences of Publication Types')]
    pub_counts = sorted(get_pub_type_counts(data),key=lambda x: x[1],reverse=True)
    time = lambda v: 's' if v > 1 else ''
    for pub_type, count in pub_counts:
        string_ls.append(html_enclose('p',f'Type {pub_type} appears {count} time{time(count)}'))
    return ''.join(string_ls)


def get_author_pub_graph(author,data):
    pub_partners = []
    for entry in data.values():
        if 'author' in entry and author in entry['author']:
            for partner in entry['author']:
                if partner != author:
                    pub_partners.append(partner)
    return [(author_name,pub_partners.count(author_name))
            for author_name in set(pub_partners)]

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

def get_html_dot_svg(author,data):
    import os
    DOT_INPUT_FILENAME = 'dot_input'
    with open(DOT_INPUT_FILENAME,'w') as file:
        file.write(get_dot_graph(author,data))
    os.system(f'dot -T svg -O {DOT_INPUT_FILENAME}')
    with open(DOT_INPUT_FILENAME + '.svg','r') as file:
        return re.search(r'<svg(?:.|\n)+</svg>',file.read()).group()

def get_html_common_pub_author(author,data):
    string_ls = [html_enclose('h2','Author Graph')]
    string_ls.append(get_html_dot_svg(author,data))
    return ''.join(string_ls)

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

def double_quote_latex(expression):
    return re.sub(r"``(.*[^\\])''",r'"\1"',expression)

def single_quote_latex (expression):
    return re.sub(r"[^`]`([^`].*[^'])'[^`]",r"'\1'",expression)

def remove_latex_special_chars(latex_expression):
    return re.sub(r'\\({|[^{])\b',r'\1',latex_expression)

def html_to_small_caps(html_expression):
    return html_add_attr('style','font-variant:small-caps',html_expression)

def str_to_html_small_caps(expression):
    return html_to_small_caps(html_create_span(expression))

def html_to_sans_serif(html_expression):
    return html_add_attr('style','font-family:sans-serif',html_expression)

def str_to_html_math(string):
    return html_add_attr('class','math inline',html_create_span(string))

def get_html_pub_type_index(data):
    string_ls = [html_enclose('h2','Publication Type Index')]
    for entry_type in sorted(set(x[0] for x in data)):
        string_ls.append(html_enclose('h3',entry_type))
        for citation_key in [x[1] for x in data if x[0]==entry_type]:
            title = data[entry_type,citation_key].get('title','')
            authors = ', '.join((sorted(data[entry_type,citation_key].get('author',''))))
            string_ls.append(html_enclose('p',f"Key = {citation_key}<br>Title = {fix_title(title)}<br>Autores = {authors}"))
    return '\n'.join(string_ls)

def last_name_first(name):
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
                index[author_name].add(key[1])
    return index

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
