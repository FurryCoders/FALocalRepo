import sqlite3
import re
import time, os, sys
import readkeys

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, fields):
    if all(len(f) == 0 for f in fields):
        print('At least one field must be searched')
        return False

    user = fields[0]
    titl = fields[1]
    tags = fields[2]
    catg = fields[3]
    spec = fields[4]
    gend = fields[5]
    rate = fields[6]

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

    terms = ('(?:.)*'+user+'(?:.)*', '(?:.)*'+titl+'(?:.)*', tags_r,\
    '(?:.)*'+catg+'(?:.)*', '(?:.)*'+spec+'(?:.)*', '(?:.)*'+gend+'(?:.)*', '(?:.)*'+rate+'(?:.)*')
    t1 = time.time()
    results = DB.execute('''SELECT author, udate, title, id FROM submissions
        WHERE authorurl REGEXP ? AND
        title REGEXP ? AND
        tags REGEXP ? AND
        category REGEXP ? AND
        species REGEXP ? AND
        gender REGEXP ? AND
        rating REGEXP ?
        ORDER BY authorurl ASC, id DESC''', terms)
    t2 = time.time()

    cols = os.get_terminal_size()[0] - 35
    if cols < 0: cols = 0
    print('{: ^10} | {: ^8} {: ^10} | {}'.format('AUTHOR', 'DATE', 'ID', 'TITLE'[0:cols]))
    print(('-'*35)+'-------'[0:cols])
    for r in results:
        print(f'{r[0][0:10]: <10} | {r[1][2:]} {r[3]:0>10} | {r[2][0:cols]}')

    print(f'\n{len(results.fetchall())} results found in {t2-t1:.3f} seconds')

    return True

def main(DB):
    while True:
        fields = []
        # Author
        # Title
        # Tags
        # Category
        # Species
        # Gender
        # Rating
        try:
            fields += [readkeys.input('Author: ')]
            fields += [readkeys.input('Title: ')]
            fields += [readkeys.input('Tags: ')]
            fields += [readkeys.input('Category: ')]
            fields += [readkeys.input('Species: ')]
            fields += [readkeys.input('Gender: ')]
            fields += [readkeys.input('Rating: ')]
        except:
            return

        print()

        if not search(DB, fields):
            print()
            continue
        else:
            break
