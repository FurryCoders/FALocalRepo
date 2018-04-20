import sqlite3
import os, glob
import re
from FA_dl import session, dl_usr, dl_sub, check_page
from FA_db import usr_ins, usr_rm, usr_rep, usr_up
from FA_tools import tiers, sigint_check, sigint_clear

def check_values(sub):
    if None in sub:
        return False
    elif '' in (sub[1], sub[2], sub[4], sub[12]):
        return False
    elif '' in (sub[6], sub[7], sub[8], sub[9]):
        return False
    elif sub[11] != '0' and sub[10] == '':
        return False
    elif sub[12] != tiers(sub[0])+f'/{sub[0]:0>10}':
        return False

    return True

def check_files(sub):
    loc = 'FA.files/'+sub[12]
    if not os.path.isdir(loc):
        return False
    elif not os.path.isfile(loc+'/info.txt'):
        return False
    elif not os.path.isfile(loc+'/description.html'):
        return False
    elif sub[11] != '0' and not os.path.isfile(loc+f'/{sub[11]}'):
        return False

    return True

def find_errors_sub(DB):
    subs = DB.execute('SELECT * FROM submissions ORDER BY id ASC')
    subs = [[si for si in s] for s in subs.fetchall()]

    errs_id = []
    errs_vl = []
    errs_fl = []

    re_id = re.compile('^(|0+)$')

    for s in subs:
        if sigint_check(): break

        if re_id.match(str(s[0])):
            errs_id.append(s)
            continue

        if not check_values(s):
            errs_vl.append(s)
            continue

        if not check_files(s):
            errs_fl.append(s)

    return errs_id, errs_vl, errs_fl

def check_folder(usr):
    if len(usr[2]) and 'g' not in usr[1]:
        return False
    elif len(usr[3]) and 's' not in usr[1]:
        return False
    elif len(usr[4]) and 'f' not in usr[1]:
        return False
    elif len(usr[5]) and 'e' not in usr[1] and 'E' not in usr[1]:
        return False

    return True

def check_folder_dl(usr):
    ret = []
    if 'g' in usr[1] and not len(usr[2]):
        if 'g!' not in usr[1]:
            ret.append('g')
    if 's' in usr[1] and not len(usr[3]):
        if 's!' not in usr[1]:
            ret.append('s')
    if 'f' in usr[1] and not len(usr[4]):
        if 'f!' not in usr[1]:
            ret.append('f')
    if ('e' in usr[1] or 'E' in usr[1]) and not len(usr[5]):
        ret.append('e')

    return ret

def find_errors_usr(DB):
    usrs = DB.execute('SELECT * FROM users ORDER BY name ASC')
    usrs = [[ui for ui in u] for u in usrs.fetchall()]

    errs_empty = []
    errs_repet = []
    errs_names = []
    errs_foldr = []
    errs_fl_dl = []

    i = 0
    while i < len(usrs):
        u = usrs[i]
        if all(ui == '' for ui in u[1:]):
            errs_empty.append(u[0])
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1

    i = 0
    while i < len(usrs):
        u = usrs[i]
        if any(u[0].lower() == usrs[j][0].lower() for j in range(0, len(usrs)) if j != i):
            errs_repet.append(u)
        i += 1
    usrs = [u for u in usrs if u not in errs_repet]

    i = 0
    while i < len(usrs):
        u = usrs[i]
        if u[0].lower() != u[0] or '_' in u[0]:
            errs_names.append(u)
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1

    i = 0
    while i < len(usrs):
        u = usrs[i]
        if not check_folder(u):
            errs_foldr.append(u)
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1

    i = 0
    while i < len(usrs):
        u = usrs[i]
        u_d = check_folder_dl(u)
        if u_d:
            errs_fl_dl.append([u[0], u_d])
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1


    return errs_empty, errs_repet, errs_names, errs_foldr, errs_fl_dl

def repair(Session, DB):
    print('Analyzing submissions database for errors ... ', end='', flush=True)
    errs_id, errs_vl, errs_fl = find_errors_sub(DB)
    print('Done')
    print(f'Found {len(errs_id)} id error{"s"*bool(len(errs_id) != 1)}')
    print(f'Found {len(errs_vl)} field values error{"s"*bool(len(errs_vl) != 1)}')
    print(f'Found {len(errs_fl)} files error{"s"*bool(len(errs_fl) != 1)}')
    print()

    sigint_clear()

    print('Analyzing users database for errors ... ', end='', flush=True)
    errs_empty, errs_repet, errs_names, errs_foldr, errs_fl_dl = find_errors_usr(DB)
    print('Done')
    print(f'Found {len(errs_empty)} empty user{"s"*bool(len(errs_id) != 1)}')
    print(f'Found {len(errs_repet)} repeated user{"s"*bool(len(errs_vl) != 1)}')
    print(f'Found {len(errs_names)} capitalized username{"s"*bool(len(errs_fl) != 1)}')
    print(f'Found {len(errs_foldr)} empty folder{"s"*bool(len(errs_fl) != 1)}')
    print(f'Found {len(errs_fl_dl)} empty folder download{"s"*bool(len(errs_fl) != 1)}')
    print()

    sigint_clear()

    if any(len(errs) for errs in (errs_id, errs_vl, errs_fl)):
        Session = session()
        print()

        if not Session:
            print('Session error')
            errs_id = errs_vl = errs_fl = ''

        if len(errs_id):
            print('ID errors')
            for err in errs_id:
                print(err[0:4])

        if len(errs_vl):
            print('Fixing field values errors', end='')
            i, l, L = 0, len(str(len(errs_vl))), len(errs_vl)
            errs_fl_mv = 0
            for sub in errs_vl:
                if sigint_check(): return Session
                ID = sub[0]
                i += 1
                print(f'\n{i:0>{l}}/{L} - {ID:0>10}', end='', flush=True)
                if sub[3] == None: sub[3] = ''
                if sub[5] == None: sub[5] = ''
                if check_values(sub):
                    DB.execute(f'UPDATE submissions SET title = "{sub[3]}" WHERE id = {ID}')
                    DB.execute(f'UPDATE submissions SET tags = "{sub[5]}" WHERE id = {ID}')
                    DB.commit()
                    if not check_files(sub) and sub[13]:
                        errs_fl.append(sub)
                        errs_fl_mv += 1
                    continue
                if not sub[13]:
                    print(' - Page Error', end='', flush=True)
                    continue
                if not check_page(Session, 'view/'+str(ID)):
                    print(' - Page Error', end='', flush=True)
                    DB.execute(f'UPDATE submissions SET server = 0 WHERE id = {ID}')
                    DB.commit()
                    continue
                if sub[12] == tiers(ID)+f'{ID:0>10}':
                    for f in glob.glob(f'FA.files/{sub[12]}/*'):
                        os.remove(f)
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
                if sigint_check(): return Session
                ID = sub[0]
                i += 1
                print(f'\n{i:0>{l}}/{L} - {ID:0>10} {sub[12]}', end='', flush=True)
                if not sub[13]:
                    print(' - Page Error', end='', flush=True)
                    continue
                if not check_page(Session, 'view/'+str(ID)):
                    print(' - Page Error', end='', flush=True)
                    DB.execute(f'UPDATE submissions SET server = 0 WHERE id = {ID}')
                    DB.commit()
                    continue
                for f in glob.glob(f'FA.files/{sub[12]}/*'):
                    os.remove(f)
                DB.execute(f'DELETE FROM submissions WHERE id = {ID}')
                DB.commit()
                dl_sub(Session, str(ID), f'FA.files/{sub[12]}', DB, True, False, 2)
            print()

        print()

    if any(len(errs) for errs in (errs_empty, errs_repet, errs_names, errs_foldr, errs_fl_dl)):
        print()

        if len(errs_empty):
            print('Empty users')
            for u in errs_empty:
                print(f' {u}')
                usr_rm(DB, u, True)
        print()

        if len(errs_repet):
            print('Repeated users')
            while len(errs_repet):
                u = errs_repet[0]
                print(f' {u[0]}')
                u_new = [u[0].lower(),'','','','','']
                u_rep = [ur for ur in errs_repet if ur[0].lower() == u[0].lower()]
                errs_repet = [ur for ur in errs_repet if ur[0].lower() != u[0].lower()]
                for i in range(1, 6):
                    u_new_i = []
                    for u in u_rep:
                        for ui in u[i].split(','):
                            if ui not in u_new_i and ui != '':
                                u_new_i.append(ui)
                    u_new_i.sort()
                    u_new[i] = ",".join(u_new_i)
                for u in u_rep:
                    usr_rm(DB, u[0])
                usr_ins(DB, u[0])
                usr_up(DB, u[0], u_new[1], 'FOLDERS')
                usr_up(DB, u[0], u_new[2], 'GALLERY')
                usr_up(DB, u[0], u_new[3], 'SCRAPS')
                usr_up(DB, u[0], u_new[4], 'FAVORITES')
                usr_up(DB, u[0], u_new[5], 'EXTRAS')
                if not check_folder(u_new):
                    errs_foldr.append(u_new)
                else:
                    u_d = check_folder_dl(u)
                    if len(u_d):
                        errs_fl_dl.append([u[0], u_d])
            print()

        if len(errs_names):
            print('Capitalized usernames')
            for u in errs_names:
                print(f' {u[0]}')
                usr_rep(DB, u[0], u[0], u[0].lower().replace('_',''), 'NAME')
                if not check_folder(u):
                    errs_foldr.append(u)
            print()

        if len(errs_foldr):
            print('Empty folders')
            for u in errs_foldr:
                print(f' {u[0]}')
                if len(u[2]):
                    usr_up(DB, u[0], 'g', 'FOLDERS')
                if len(u[3]):
                    usr_up(DB, u[0], 's', 'FOLDERS')
                if len(u[4]):
                    usr_up(DB, u[0], 'f', 'FOLDERS')
                if len(u[5]) and 'e' not in u[1] and 'E' not in u[1]:
                    usr_up(DB, u[0], 'e', 'FOLDERS')
                u_d = check_folder_dl(u)
                if len(u_d):
                    errs_fl_dl.append([u[0], u_d])
            print()

        if len(errs_fl_dl):
            print('Missing submissions')
            Session = session()
            if not Session:
                print('Session error')
                errs_fl_dl = []
            else:
                print('-'*47)
            for u in errs_fl_dl:
                for f in u[1]:
                    dl_usr(Session, u[0], f, DB, False, 2, 0, False)
            print()

    print('Optimizing database ... ', end='', flush=True)
    DB.execute("VACUUM")
    print('Done')
    print('\nAll done')

    return Session
