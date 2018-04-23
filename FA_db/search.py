import sqlite3
import re
import time, os, sys
import PythonRead as readkeys
from FA_tools import sigint_block, sigint_ublock, sigint_check, sigint_clear

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, fields):
    DB.create_function("REGEXP", 2, regexp)

def main(DB):
    while True:
        fields = {}

        try:
            sigint_ublock()
            fields['user'] = readkeys.input('User: ').strip()
            if fields['user'] != '':
                fields['sect'] = readkeys.input('Section: ').strip()
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
