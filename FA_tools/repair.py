import sqlite3
import os
import re
from .tools import tiers

def dberrors(DB):
    subs = DB.execute('SELECT * FROM submissions ORDER BY id ASC')

    subs = [[si for si in s] for s in subs.fetchall()]
    errs_vl = []
    errs_id = []
    errs_fl = []
    re_id = re.compile('^(|0+)$')

    for s in subs:
        if re_id.match(str(s[0])):
            errs_id.append(s)
            continue

        err = [s[0]]
        if None in s:
            err.append('n')
        if '' in (s[1], s[2], s[4], s[6], s[8]):
            err.append('e')
        if s[8] != tiers(s[0])+f'/{s[0]:0>10}':
            err.append('l')
        if len(err) > 1:
            errs_vl.append(err)

        loc = 'FA.files/'+s[8]
        if not os.path.isdir(loc):
            errs_fl.append(s[0])
            continue
        if not os.path.isfile(loc+'/info.txt'):
            errs_fl.append(s[0])
            continue
        if not os.path.isfile(loc+'/description.html'):
            err_fls.append(s[0])
            continue
        if s[7] != 0 and not os.path.isfile(loc+f'/{s[7]}'):
            errs_fl.append(s[0])
            continue

    return errs_id, errs_vl, errs_fl
