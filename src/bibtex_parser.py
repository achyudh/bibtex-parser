from os.path import dirname, join as pjoin
import sys
import sqlite3
from ply import lex
from ply import yacc
from ply.lex import TOKEN
import sqlite3


db_connect = sqlite3.connect('bibtex.db')
db_cursor = db_connect.cursor()
# db_cursor.execute('DROP TABLE REF_TABLE')


db_cursor.execute('''CREATE TABLE REF_TABLE(address TEXT, author TEXT, bibkey TEXT PRIMARY KEY, bibtype TEXT, booktitle TEXT, chapter TEXT,
                    edition TEXT, journal TEXT, numb TEXT, pages text, publisher text, school text, title text, volume text, year text)''')

db_cursor.execute('PRAGMA table_info([REF_TABLE])')
print("Table Description:", db_cursor.fetchall())
print("\nTokens:")
tokens=(
"AT",
"NEWLINE",
"COMMENT",
"WHITESPACE",
"JUNK",
"NUMBER",
"NAME",
"LBRACE",
"RBRACE",
"LPAREN",
"RPAREN",
"EQUALS",
"HASH",
"COMMA",
"QUOTE",
"STRING",
)

t_AT= r'\@'
t_NEWLINE=r'\n'
t_COMMENT=r'\%~[\n]*\n'
t_WHITESPACE= r'[ \r\t]+'
t_JUNK=r'~[\@\n\ \r\t]+'
t_NUMBER =r'[0-9]+'
t_NAME =r'[A-Za-z0-9\!\$\&\*\+\-\.\/\:\;\<\>\?\[\]\^\_\'\| ]+'
t_LBRACE =r'\{'
t_RBRACE =r'\}'
t_LPAREN=r'\('
t_RPAREN=r'\)'
t_EQUALS =r'='
t_HASH =r'\#'
t_COMMA =r','
t_QUOTE =r'\"'
t_STRING =r'{[^{}]}'
t_ignore=' \t\n\v\r'

def t_error(t):
    print("Illegal character ’%s’" % t.value[0])
    t.lexer.skip(1)

def p_bibfile(p):
    '''bibfile : entries'''
    p[0] = p[1]
    # print(p[1])

def p_entries(p):
    '''entries : entry entries
               | entry'''
    if len(p) > 2:
        p[0] = p[2].append(p[1])
    else:
        p[0] = [p[1]]

def p_entry(p):
    'entry : AT NAME LBRACE key COMMA fields RBRACE'
    temp_fields = {**p[6], 'type':p[2]}
    temp_dict = {'bibkey': "NULL", 'bibtype': "NULL", 'address': "NULL", 'author': "NULL",
            'booktitle': "NULL", 'chapter': "NULL", 'edition': "NULL", 'journal': "NULL",
            'num': "NULL", 'pages': "NULL", 'publisher': "NULL", 'school': "NULL",
            'title': "NULL", 'volume': "NULL", 'year': "NULL"}
    for key, value in temp_fields.items():
        temp_dict[key] = value
    temp_dict['bibkey'] = p[4]
    temp_dict['bibtype'] = temp_dict['type']
    p[0]={p[4]:temp_dict}
    # print(temp_dict)
    # print(temp_dict['bibtype'], temp_dict['bibkey'])
    db_cursor.execute('INSERT INTO REF_TABLE values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',[x[1] for x in sorted(temp_dict.items(),key=lambda x:x[0]) if x[0] != 'type'])
    db_connect.commit()

def p_fields(p):
    '''fields : field COMMA fields
              | field'''
    if len(p)>2:
        p[0] = {**p[1], **p[3]}
    else:
        p[0] = p[1]

def p_field(p):
    'field : NAME EQUALS LBRACE value RBRACE'
    p[0] = {p[1].strip():p[4].strip()}

def p_value(p):
    '''value : STRING
             | NUMBER
             | NAME'''
    p[0] = p[1]

def p_key(p):
    '''key : NAME
           | NUMBER'''
    p[0] = p[1]


lexer = lex.lex()
data = """
@book{ourbook,
author = {joe smith and john Kurt},
title = {Our Little Book},
year = {1997}}
@article{key1,
author = {Sarkar Santonu},
title = {John Smith}}
"""

lexer.input(data)
for token_iter in lexer:
    print(token_iter)
parser = yacc.yacc()
parser.parse(data)
print("\nTable after Insertion:")
db_cursor.execute('SELECT * FROM REF_TABLE')
print(db_cursor.fetchall())
db_cursor.execute('DROP TABLE REF_TABLE')
db_connect.close()
