import sqlite3
import os

def missingfiles(DB):
    subs = DB.execute('SELECT id, location, filename FROM submissions ORDER BY id ASC')

    subs = [[si for si in s] for s in subs.fetchall()]
    errs = []

    for s in subs:
        loc = 'FA.files/'+s[1]
        if not os.path.isdir(loc):
            errs.append(s[0])
            continue
        if not os.path.isfile(loc+'/info.txt'):
            errs.append(s[0])
            continue
        if not os.path.isfile(loc+'/description.html'):
            errs.append(s[0])
            continue
        if s[2] != 0 and not os.path.isfile(loc+f'/{s[2]}'):
            errs.append(s[0])
            continue

    return errs
