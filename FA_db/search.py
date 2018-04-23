import sqlite3
import re
import time, os, sys
import PythonRead as readkeys
from FA_tools import sigint_block, sigint_ublock, sigint_check, sigint_clear

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, fields):
    DB.create_function("REGEXP", 2, regexp)

    for k in list(fields.keys())[2:]:
        fields[k] = f'%{fields[k]}%'
    fields['tags'] = re.sub('( )+', '%', fields['tags'])

    subs = DB.execute('''SELECT * FROM submissions
        WHERE title LIKE ? AND
        tags LIKE ? AND
        category LIKE ? AND
        species LIKE ? AND
        gender LIKE ? AND
        rating LIKE ?
        ORDER BY authorurl ASC, id DESC''', tuple(fields.values())[2:]).fetchall()
    subs = {s[0]: s[1:] for s in subs}

    if fields['user']:
        subs_u = DB.execute(f'SELECT gallery, scraps, favorites, extras FROM users WHERE name = "{fields["user"]}"')
        subs_u = subs_u.fetchall()
        if not len(subs_u):
            subs_u = ['']
        subs_u = [[int(si) for si in s.split(',') if si != ''] for s in subs_u[0]]
        if fields['sect']:
            subs_t = []
            if 'g' in fields['sect']:
                subs_t += subs_u[0]
            if 's' in fields['sect']:
                subs_t += subs_u[1]
            if 'f' in fields['sect']:
                subs_t += subs_u[2]
            if 'e' in fields['sect']:
                subs_t += subs_u[3]
        else:
            subs_t = subs_u[0] + subs_u[1] + subs_u[2] + subs_u[3]
        subs_u = list(set(subs_t))
        subs = [subs.get(s) for s in subs_u]
        subs = [s for s in subs if s != None]

def main(DB):
    while True:
        fields = {}

        try:
            sigint_ublock()
            fields['user'] = readkeys.input('User: ').strip()
            if fields['user'] != '':
                fields['sect'] = readkeys.input('Section: ').strip().lower()
                fields['sect'] = re.sub('[^gsfe]','', fields['sect'])
            else:
                fields['sect'] = ''
            fields['titl'] = readkeys.input('Title: ')
            fields['tags'] = readkeys.input('Tags: ')
            fields['catg'] = readkeys.input('Category: ')
            fields['spec'] = readkeys.input('Species: ')
            fields['gend'] = readkeys.input('Gender: ').lower()
            fields['ratg'] = readkeys.input('Rating: ').lower()
        except:
            return
        finally:
            sigint_clear()

        if all(v == '' for v in fields.values()):
            print('At least one field needs to be used')
            print()
            continue

        break

    search(DB, fields)
    print()
    print('Press any key to continue ', end='', flush=True)
    readkeys.getkey()
    print('\b \b'*26, end='')
