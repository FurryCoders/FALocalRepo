import sqlite3
import os
import re
from FA_dl import session, dl_usr, dl_sub, check_page
from FA_tools import tiers

def find_errors(DB):
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

def dberrors(DB):
    print('Analyzing database for errors ... ', end='', flush=True)
    errs_id, errs_vl, errs_fl = find_errors(DB)
    print('Done')

    print(f'There are {len(errs_id)} id errors')
    print(f'There are {len(errs_vl)} field value errors')
    print(f'There are {len(errs_fl)} files errors')

    if len(errs_id) or len(errs_vl) or len(errs_fl):
        print()
        Session = session()
        print()

        if not Session:
            print('Session error')
            return

        if len(errs_vl):
            print('Fixing field values errors')
            i, l = 0, len(str(len(errs_vl)))
            for sub in errs_vl:
                sub = str(sub[0])
                i += 1
                print(f'{i:0>{l}}/{len(errs_vl)} - {sub:0>10}\r', end='', flush=True)
                if not check_page(Session, 'view/'+sub): continue
                DB.execute(f'DELETE FROM submissions WHERE id = {sub[0]}')
                DB.commit()
                dl_sub(Session, sub, f'FA.files/{tiers(sub[0])}/{sub[0]:0>10}', DB, True, False, 2)
            print(' '*(l+l+1+3+10), end='\r', flush=True)

        if len(errs_fl):
            print('Fixing missing files')
            i, l = 0, len(str(len(errs_fl)))
            for sub in errs_fl:
                i += 1
                print(f'{i:0>{l}}/{len(errs_fl)} - {sub:0>10}\r', end='', flush=True)
                if not check_page(Session, 'view/'+sub): continue
                if int(sub) in [s[0] for s in errs_vl]: continue
                dl_sub(Session, str(sub), f'FA.files/{tiers(sub[0])}/{sub[0]:0>10}', DB, True, False, 2)
            print(' '*(l+l+1+3+10), end='\r', flush=True)

    print('Optimizing database ... ', end='', flush=True)
    DB.commit()
    DB.execute("VACUUM")
    print('Done')
    print('\nAll done')
