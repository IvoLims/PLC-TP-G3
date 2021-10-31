import re
import prog
#\s*(\w+)\s*=\s*{([^}]+)}
# @(\w+)\s*{\s*(\w+),\n?\s*((\w+)\s*=\s*{([^}]+)}\s*)+\n?}
# @(\w+)\s*{\s*(\w+),((\s*(\w+)\s*=\s*{([^}]+)}\s*,\s*)+)|((\s*(\w+)\s*=\s*"([^"]+)"\s*,\s*)+)|((\s*(\w+)\s*=\s*(\d+)\s*,\s*)+)
def main():
    # Funcao do Ivo, nao e esboco
    file = open("exemplo-utf8.bib", "r")
    read = True
    dic = {}
    string_ls = ['<!DOCTYPE  HTML PUBLIC>\n<HTML>\n   <HEAD>\n      <TITLE>Categories in BibTeX</TITLE>\n   </HEAD>\n   <BODY>']
    while read:
      linhaFicheiro = file.readline()
      ncat = re.match(r'^@(.*){',linhaFicheiro)
      if ncat != None:
        cat_title = ncat.group(1).title()
        dic[cat_title] = dic.get(cat_title,0) + 1
      if not linhaFicheiro:
        read = False
    file.close()

    time = lambda v: 's' if v > 1 else ''


    for k, v in dic.items():
      string_ls.append(f'      <P>The category {k} appears {v} time{time(v)}.</P>')
    string_ls.append(f'   </BODY>\n{prog.test_data_view()}</HTML>')

    with open('output.html','w') as file:
        file.write('\n'.join(string_ls))

def getMatch():
    #@(\w+)\s*{(\s*(\w+)\s*,\s*(((\w+)\s*=\s*({([^}]*)}|"([^"]*)"|(\d+))),\s*)+)}
    return re.compile(r'@(\w+)\s*{(\w+),(?:\s*(\w+)\s*=\s*(?:{([^}]*)}|"([^"]*)"|(\d*))\s*,)(?:\s*(\w+)\s*=\s*(?:{([^}]*)}|"([^"]*)"|(\d*))\s*,)?')

def getStr():
    with open('exemplo-utf8.bib', 'r') as file:
        string = file.read()
    # return string.replace(r'}\n}',r'},\n}')
    with open('simp.bib', 'r') as file:
        string2 = file.read()
    return string

myMatch = getMatch()
string = getStr()

#@\w+{\w+,\s*(((\w+)=(?:{([^}]+)}|"([^"]+)"|(\d+))),\s*)*

#@(\w+)\s*{(\w+),(?:\s*(\w+)\s*=\s*(?:{([^}]*)}|"([^"]*)"|(\d*))\s*,)
# just repeat (?:\s*(\w+)\s*=\s*(?:{([^}]*)}|"([^"]*)"|(\d*))\s*,) with ? at the end
# finish it all of with \n}

# regex to match entry and citation-key
init_entry_regex = r'@(\w+)\s*{(\w+),'
# regex to match fields in entry
basic_field_regex = r'(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,\s*)?'
basic_field_regex_optional_comma = r'(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,?\s*)?'
# there are 24 possible fields
full_field_regex = basic_field_regex + (basic_field_regex + r'?')*22
end_entry_regex  = basic_field_regex_optional_comma + r'}'

full_regex = init_entry_regex + full_field_regex + end_entry_regex


# '@(\w+)\s*{(\w+),
# (?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)
# (?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?
# (?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?
# ...
# (?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,?\s*)?}

def main2():
    tt = r'@(\w+)\s*{(\w+),(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,?\s*)?}'

    rp = r'(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)?'

    qq = r'@(\w+)\s*{(\w+),'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,)?'\
           + r'(?:\s*(\w+)\s*=\s*(?:{(.*|\n)}|"([^"]*)"|(\d*))\s*,?\s*)?}'

    qq1 = r'@(\w+)\s*{(\w+),(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,)'\
        + rp*26 + r'(?:\s*(\w+)\s*=\s*(?:{(.*)}|"([^"]*)"|(\d*))\s*,?\s*)?}'

    for m in re.finditer(qq,getStr()):
        for i in range(1,87,2):
            if m.group(i) is not None:
                print(f'{m.group(i)} = {m.group(i+1)}')
        print('\n')

def getFullRegex():
    return full_field_regex