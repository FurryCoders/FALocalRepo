import sqlite3
import os, glob
import re
from FA_dl import session, dl_usr, dl_sub, check_page
from FA_tools import tiers, sigint_check

def check_values(sub):
    if None in sub:
        return False
    elif '' in (sub[1], sub[2], sub[4], sub[8]):
        return False
    elif sub[7] != '0' and sub[6] == '':
        return False
    elif sub[8] != tiers(sub[0])+f'/{sub[0]:0>10}':
        return False

    return True

def check_files(sub):
    loc = 'FA.files/'+sub[8]
    if not os.path.isdir(loc):
        return False
    elif not os.path.isfile(loc+'/info.txt'):
        return False
    elif not os.path.isfile(loc+'/description.html'):
        return False
    elif sub[7] != '0' and not os.path.isfile(loc+f'/{sub[7]}'):
        return False

    return True

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

        if not check_values(s):
            errs_vl.append(s)
            continue

        if not check_files(s):
            errs_fl.append(s)

    return errs_id, errs_vl, errs_fl

def dberrors(DB):
    print('Analyzing database for errors ... ', end='', flush=True)
    errs_id, errs_vl, errs_fl = find_errors(DB)
    print('Done')

    print(f'Found {len(errs_id)} id error{"s"*bool(len(errs_id) != 1)}')
    print(f'Found {len(errs_vl)} field values error{"s"*bool(len(errs_vl) != 1)}')
    print(f'Found {len(errs_fl)} files error{"s"*bool(len(errs_fl) != 1)}')
    print()

    if len(errs_id) or len(errs_vl) or len(errs_fl):
        Session = session()
        print()

        if not Session:
            print('Session error')
            return

        if len(errs_vl):
            print('Fixing field values errors', end='')
            i, l, L = 0, len(str(len(errs_vl))), len(errs_vl)
            errs_fl_mv = 0
            for sub in errs_vl:
                if sigint_check(): return
                ID = sub[0]
                i += 1
                print(f'\n{i:0>{l}}/{L} - {ID:0>10}', end='', flush=True)
                if sub[3] == None: sub[3] = ''
                if sub[5] == None: sub[5] = ''
                if check_values(sub):
                    DB.execute(f'UPDATE submissions SET title = "{sub[3]}" WHERE id = {ID}')
                    DB.execute(f'UPDATE submissions SET tags = "{sub[5]}" WHERE id = {ID}')
                    DB.commit()
                    if not check_files(sub):
                        errs_fl.append(sub)
                        errs_fl_mv += 1
                    continue
                if not check_page(Session, 'view/'+str(ID)):
                    print(' - Page Error', end='', flush=True)
                    continue
                DB.execute(f'DELETE FROM submissions WHERE id = {ID}')
                DB.commit()
                dl_sub(Session, str(ID), f'FA.files/{tiers(ID)}/{ID:0>10}', DB, True, False, 2)
            print()
            if errs_fl_mv:
                print(f'{errs_fl_mv} new submission{"s"*bool(len(errs_fl_mv) != 1)} with files missing')

        if len(errs_fl):
            print('Fixing missing files', end='')
            i, l, L = 0, len(str(len(errs_fl))), len(errs_fl)
            for sub in errs_fl:
                if sigint_check(): return
                ID = sub[0]
                i += 1
                print(f'\n{i:0>{l}}/{L} - {ID:0>10} {sub[8]}', end='', flush=True)
                if not check_page(Session, 'view/'+str(ID)):
                    print(' - Page Error', end='', flush=True)
                    continue
                sub_f = glob.glob(f'FA.files/{sub[8]}/*')
                for f in sub_f:
                    os.remove(f)
                DB.execute(f'DELETE FROM submissions WHERE id = {ID}')
                DB.commit()
                dl_sub(Session, str(ID), f'FA.files/{sub[8]}', DB, True, False, 2)
            print()

        print()

    print('Optimizing database ... ', end='', flush=True)
    DB.execute("VACUUM")
    print('Done')
    print('\nAll done')
