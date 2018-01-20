import sqlite3
import os
import re
from FA_dl import session, dl_usr, dl_sub, check_page
from FA_tools import tiers, sigint_check

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
        if s[7] != '0' and not os.path.isfile(loc+f'/{s[7]}'):
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
    print()

    if len(errs_id) or len(errs_vl) or len(errs_fl):
        Session = session()
        print()

        if not Session:
            print('Session error')
            return

        if len(errs_vl):
            print('Fixing field values errors')
            i, l = 0, len(str(len(errs_vl)))
            for sub in errs_vl:
                if sigint_check(): return
                sub = str(sub[0])
                i += 1
                print(f'\r{i:0>{l}}/{len(errs_vl)} - {sub:0>10}', end='', flush=True)
                sub_db = DB.execute(f'SELECT * FROM submissions WHERE id = {int(sub)}').fetchall()[0]
                if sub_db[3] == None and None not in sub_db[0:3]+sub_db[4:]:
                    DB.execute(f'UPDATE submissions SET title = "" WHERE id = {int(sub)}')
                    DB.commit()
                    continue
                if not check_page(Session, 'view/'+sub):
                    print(' - Page Error')
                    continue
                DB.execute(f'DELETE FROM submissions WHERE id = {int(sub)}')
                DB.commit()
                dl_sub(Session, sub, f'FA.files/{tiers(sub)}/{sub:0>10}', DB, True, False, 2)
            print('\r', end=' '*(l+l+1+3+10), flush=True)

        if len(errs_fl):
            print('Fixing missing files')
            i, l = 0, len(str(len(errs_fl)))
            for sub in errs_fl:
                if sigint_check(): return
                sub = str(sub)
                i += 1
                print(f'\r{i:0>{l}}/{len(errs_fl)} - {sub:0>10}', end='', flush=True)
                if not check_page(Session, 'view/'+sub):
                    print(' - Page Error')
                    continue
                if int(sub) in [s[0] for s in errs_vl]:
                    continue
                loc = DB.execute(f'SELECT location FROM submissions WHERE id = {int(sub)}').fetchall()[0][0]
                dl_sub(Session, sub, f'FA.files/{loc}', DB, True, False, 2)
            print('\r', end=' '*(l+l+1+3+10), flush=True)

        print()

    print('Optimizing database ... ', end='', flush=True)
    DB.execute("VACUUM")
    print('Done')
    print('\nAll done')
