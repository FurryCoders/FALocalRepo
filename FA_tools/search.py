import sqlite3
import re
import time, os, sys

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, user, titl, tags):
    if user == '' and titl == '' and tags == '':
        print('At least one field must be searched')
        return False

    DB.create_function("REGEXP", 2, regexp)

    tags_a = re.sub('( )+', ' ', tags.strip())
    tags_a = tags_a.split(' ')
    tags_n = [t[1:] for t in tags_a if t.startswith('!')]
    tags_y = [t for t in tags_a if not t.startswith('!') and t not in tags_n]
    tags_a = tags_n + tags_y
    tags_a.sort(key=str.lower)
    tags_r = ''
    for t in tags_a:
        if t in tags_n:
            tags_r += f'(?!((?:.)*{t}))(?:.)*'
        elif t in tags_y:
            tags_r += f'(?:.)*{t}'

    terms = ('%'+user+'%', '%'+titl+'%', tags_r)
    t1 = time.time()
    results = DB.execute('''SELECT author, udate, title, id FROM submissions
        WHERE authorurl LIKE ? AND
        title LIKE ? AND
        tags REGEXP ?
        ORDER BY authorurl ASC, id ASC''', terms)
    t2 = time.time()

    print('{: ^10} | {: ^10} {: ^10} | {}'.format('AUTHOR', 'DATE', 'ID', 'TITLE'))
    print('-'*44)
    i = 0
    for r in results:
        i += 1
        cols = os.get_terminal_size()[0] - 37
        print(f'{r[0][0:10]: <10} | {r[1]} {r[3]:0>10} | {r[2][0:cols]}')

    print(f'\n{i} results found in {t2-t1:.3f} seconds')

def main(DB):
    while True:
        user = input('Author: ')
        titl = input('Title: ')
        tags = input('Tags: ')

        if not search(DB, user, titl, tags):
            print()
            continue
        else:
            break
