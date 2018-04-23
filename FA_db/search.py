import sqlite3
import re
import time, os, sys
import PythonRead as readkeys
from FA_tools import sigint_block, sigint_ublock, sigint_check, sigint_clear

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, fields):
    DB.create_function("REGEXP", 2, regexp)
    if fields['user']:
        subs = DB.execute(f'SELECT gallery, scraps, favorites, extras FROM users WHERE name = "{fields["user"]}"')
        subs = subs.fetchall()
        subs = [s for s in subs[0]]
        if fields['sect']:
            subs_t = subs
            subs = []
            if 'g' in fields['sect']:
                subs.append(subs_t[0])
            if 's' in fields['sect']:
                subs.append(subs_t[1])
            if 'f' in fields['sect']:
                subs.append(subs_t[2])
            if 'e' in fields['sect']:
                subs.append(subs_t[3])
    else:
        subs = DB.execute(f'SELECT * FROM submissions')

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
