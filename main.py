import re

def main3():
    with open('simp.bib','r',encoding = 'utf8') as file:
        string = file.read()
    with open('exemplo-utf8.bib','r', encoding = 'utf8') as file:
        string2 = file.read()
    return get_entries(string2)

def get_entries(string):
    """Creates a dictionary with the following map
    (type of publication,citation-key) → {field:field_value}"""
    d = {}
    field = re.compile(r'(\w+)\s*=\s*(?:{([^}]+)}|"([^"]+)"|(\d+))(?:,|\n})')
    for entry in re.finditer(r'@(\w+){(\w+),((?:.*|\n)*),?\n}',string):
        d[entry.group(1).lower(),entry.group(2)] = dict((x[0].lower(),get_valid_group(x,1,3)) for x in field.findall(entry.group(3)))
    return d


def get_valid_group(t,begin_or_group,end_or_group):
    # This exists because we have 3 groups when matching a field content:
    # The content needs to be enclosed by either curly braces or quotation-marks.
    # Additionally numbers can stand alone.
    for i in range(begin_or_group,end_or_group+1):
        if (v := t[i]):
            return v

def get_author_list(data):
    return sorted(set(invert_names([a
    for s in data.values()
    for a in s.get('author',[])])))

def invert_names(authors):
    res = []
    for name in authors:
            res.append(re.sub(r'([^,]+),\s*([^,]+)',r'\2 \1',name))
    return res

def fix_authors(data):
    for d in data.values():
        if 'author' in d:
            d['author'] = [ s.strip() for s in re.split(r'\band\b',d['author'].replace('\n',' ')) if s.strip()]

def fix_accent(s):
    # https://en.wikibooks.org/wiki/LaTeX/Special_Characters
    r"""
    \`{o}	ò	grave accent
    \'{o}	ó	acute accent
    \^{o}	ô	circumflex
    \"{o}	ö	umlaut, trema or dieresis
    \H{o}	ő	long Hungarian umlaut (double acute)
    \~{o}	õ	tilde
    \c{c}	ç	cedilla
    \k{a}	ą	ogonek
    \l{}	ł	barred l (l with stroke)
    \={o}	ō	macron accent (a bar over the letter)
    \b{o}	o	bar under the letter
    \.{o}	ȯ	dot over the letter
    \d{u}	ụ	dot under the letter
    \r{a}	å	ring over the letter (for å there is also the special command \aa)
    \u{o}	ŏ	breve over the letter
    \v{s}	š	caron/háček ("v") over the letter
    \t{oo}	o͡o	"tie" (inverted u) over the two letters
    \o{}	ø	slashed o (o with stroke)
    {\i}	ı	dotless i (i without tittle)
    """
    pass