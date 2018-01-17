import sqlite3
import re
import time, os, sys

if not os.path.isfile('FA.db'): sys.exit(1)

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def db_search(DB, terms):
    return DB.execute('''SELECT author, udate, title, id FROM submissions
        WHERE authorurl LIKE ? AND
        title LIKE ? AND
        tags REGEXP ?
        ORDER BY authorurl ASC, id ASC''', terms)

DB = sqlite3.connect('FA.db')
DB.create_function("REGEXP", 2, regexp)

argv = sys.argv[1:]

if len(argv) == 3:
    author = argv[0]
    title = argv[1]
    tags_r = argv[2]
    cols = False
else:
    author = input('Author: ').strip()
    title = input('Title: ').strip()
    tags_r = input('Tags: ').strip()
    cols = True

if author == '' and title == '' and tags_r == '': sys.exit(2)

print()

tags_r = re.sub('( )+', ' ', tags_r)
tags_r = tags_r.split(' ')
tags_n = [t.replace('!', '', 1) for t in tags_r if re.search('^!', t)]
tags_y = [t for t in tags_r if t not in tags_n]
tags_r = [re.sub('^!', '', t) for t in tags_r]
tags_r.sort(key=str.lower)
tags = []
for t in tags_r:
    if t in tags_n:
        tags.append(f'(?!((?:.)*{t}))(?:.)*')
    elif t in tags_y:
        tags.append(f'(?:.)*{t}')
tags = ''.join(tags)+'(?:.)*'

terms = ('%'+author+'%', '%'+title+'%', tags)
t1 = time.time()
results = db_search(DB, terms)
t2 = time.time()

print('{: ^10} | {: ^10} {: ^10} | {}'.format('AUTHOR', 'DATE', 'ID', 'TITLE'))
print('-'*44)
i = 0
for r in results:
    i += 1
    if cols:
        cols = os.get_terminal_size()[0] - 37
        print(f'{r[0][0:10]: <10} | {r[1]} {r[3]:0>10} | {r[2][0:cols]}')
    else:
        print(f'{r[0][0:10]: <10} | {r[1]} {r[3]:0>10} | {r[2]}')

print(f'\n{i} results found in {t2-t1:.3f} seconds')
