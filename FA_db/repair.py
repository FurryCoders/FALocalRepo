import sqlite3
import os, glob
import re
import PythonRead as readkeys
import FA_dl as fadl
import FA_db as fadb
import FA_tools as fatl

def sub_check_values(sub):
    if None in sub:
        return False
    elif '' in (sub[1], sub[2], sub[4], sub[5], sub[7], sub[8], sub[9], sub[10], sub[13]):
        return False
    elif sub[12] != '0' and sub[11] == '':
        return False
    elif sub[13] != fatl.tiers(sub[0])+f'/{sub[0]:0>10}':
        return False

    return True

def sub_check_files(sub):
    loc = 'FA.files/'+sub[13]
    if not os.path.isdir(loc):
        return False
    elif not os.path.isfile(loc+'/info.txt'):
        return False
    elif not os.path.isfile(loc+'/description.html'):
        return False
    elif sub[12] != '0' and not os.path.isfile(loc+f'/{sub[12]}'):
        return False

    return True

def sub_find_errors(db):
    subs = db.execute('SELECT * FROM submissions ORDER BY id ASC')
    subs = [[si for si in s] for s in subs.fetchall()]

    errs_id = []
    errs_vl = []
    errs_fl = []

    re_id = re.compile('^(|0+)$')

    for s in subs:
        if fatl.sigint_check(): break

        if re_id.match(str(s[0])):
            errs_id.append(s)
            continue

        if not sub_check_values(s):
            errs_vl.append(s)
            continue

        if not sub_check_files(s):
            errs_fl.append(s)

    return errs_id, errs_vl, errs_fl

def usr_check_folder(usr):
    if len(usr[3]) and 'g' not in usr[2]:
        return False
    elif len(usr[4]) and 's' not in usr[2]:
        return False
    elif len(usr[5]) and 'f' not in usr[2]:
        return False
    elif len(usr[6]) and 'e' not in usr[2] and 'E' not in usr[2]:
        return False

    return True

def usr_check_folder_dl(usr):
    ret = []
    if 'g' in usr[2] and not len(usr[3]):
        if 'g!' not in usr[1]:
            ret.append('g')
    if 's' in usr[2] and not len(usr[4]):
        if 's!' not in usr[1]:
            ret.append('s')
    if 'f' in usr[2] and not len(usr[5]):
        if 'f!' not in usr[1]:
            ret.append('f')
    if ('e' in usr[2] or 'E' in usr[2]) and not len(usr[6]):
        ret.append('e')

    return ret

def usr_find_errors(db):
    usrs = db.execute('SELECT * FROM users ORDER BY user ASC')
    usrs = [[ui for ui in u] for u in usrs.fetchall()]

    errs_empty = []
    errs_repet = []
    errs_names = []
    errs_namef = []
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
        if u[1].lower().replace('_','') != u[0]:
            errs_namef.append(u)
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1

    i = 0
    while i < len(usrs):
        u = usrs[i]
        if not usr_check_folder(u):
            errs_foldr.append(u)
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1

    i = 0
    while i < len(usrs):
        u = usrs[i]
        u_d = usr_check_folder_dl(u)
        if u_d:
            errs_fl_dl.append([u[0], u_d])
            usrs = usrs[0:i] + usrs[i+1:]
            i -= 1
        i += 1


    return errs_empty, errs_repet, errs_names, errs_namef, errs_foldr, errs_fl_dl

def inf_find_errors(db):
    infos = db.execute('SELECT FIELD, VALUE FROM INFOS').fetchall()

    errs_reps = []
    errs_vers = False
    errs_name = False
    errs_nums = False
    errs_timu = False
    errs_timd = False


    for i in range(0, len(infos)):
        for j in range(0, len(infos)):
            if infos[i][0] == infos[j][0] and i != j:
                errs_reps.append(infos[i])
    infos = [i for i in infos if i not in errs_reps]

    infos = {i[0]: i[1] for i in infos}

    if 'VERSION' not in infos or infos['VERSION'] != '2.6':
        errs_vers = True

    if 'dbNAME' not in infos or infos['dbNAME'] != '':
        errs_name = True

    if 'USRN' not in infos or infos['USRN'] != '':
        errs_nums = True
    if 'SUBN' not in infos or infos['SUBN'] != '':
        errs_nums = True

    if 'LASTUP' not in infos or infos['LASTUP'] != '':
        errs_timu = True
    if 'LASTUPT' not in infos or infos['LASTUPT'] != '':
        errs_timu = True

    if 'LASTDL' not in infos or infos['LASTDL'] != '':
        errs_timd = True
    if 'LASTDLT' not in infos or infos['LASTDLT'] != '':
        errs_timd = True

    return errs_reps, errs_vers, errs_name, errs_nums, errs_timu, errs_timd

def index(Session, db):
    print('Indexing new entries ... ', end='', flush=True)
    fadb.mkindex(db)
    print('Done\n')

    return Session

def vacuum(Session, db):
    print('Optimizing database ... ', end='', flush=True)
    db.execute("VACUUM")
    print('Done\n')

    return Session

def repair_subs(Session, db):
    print('Analyzing submissions database for errors ... ', end='', flush=True)
    errs_id, errs_vl, errs_fl = sub_find_errors(db)
    print('Done')
    print(f'Found {len(errs_id)} id error{"s"*bool(len(errs_id) != 1)}')
    print(f'Found {len(errs_vl)} field values error{"s"*bool(len(errs_vl) != 1)}')
    print(f'Found {len(errs_fl)} files error{"s"*bool(len(errs_fl) != 1)}')

    fatl.sigint_clear()

    while any(len(errs) for errs in (errs_id, errs_vl, errs_fl)):
        print()

        Session = fadl.session(Session)

        if not Session:
            print('Session error')
            errs_id = errs_vl = errs_fl = ''

        if len(errs_id):
            print()
            print('ID errors')
            for err in errs_id:
                print(err[0:4])

        if len(errs_vl):
            print()
            print('Fixing field values errors', end='')
            i, l, L = 0, len(str(len(errs_vl))), len(errs_vl)
            errs_fl_mv = 0
            for sub in errs_vl:
                if fatl.sigint_check(): break
                ID = sub[0]
                i += 1
                print(f'\n{i:0>{l}}/{L} - {ID:0>10}', end='', flush=True)
                if sub[3] == None: sub[3] = ''
                if sub[5] == None: sub[5] = ''
                if sub[6] == None: sub[6] = ''
                if sub_check_values(sub):
                    db.execute(f'UPDATE submissions SET title = "{sub[3]}" WHERE id = {ID}')
                    db.execute(f'UPDATE submissions SET description = "{sub[5]}" WHERE id = {ID}')
                    db.execute(f'UPDATE submissions SET tags = "{sub[6]}" WHERE id = {ID}')
                    db.commit()
                    if not sub_check_files(sub) and sub[14]:
                        errs_fl.append(sub)
                        errs_fl_mv += 1
                    continue
                if not sub[14]:
                    print(' - Page Error', end='', flush=True)
                    continue
                if not fadl.check_page(Session, 'view/'+str(ID)):
                    print(' - Page Error', end='', flush=True)
                    db.execute(f'UPDATE submissions SET server = 0 WHERE id = {ID}')
                    db.commit()
                    continue
                if sub[13] == fatl.tiers(ID)+f'{ID:0>10}':
                    for f in glob.glob(f'FA.files/{sub[13]}/*'):
                        os.remove(f)
                db.execute(f'DELETE FROM submissions WHERE id = {ID}')
                db.commit()
                fadl.dl_sub(Session, str(ID), f'FA.files/{fatl.tiers(ID)}/{ID:0>10}', db, True, False, 2)
            print()
            if errs_fl_mv:
                print(f'{errs_fl_mv} new submission{"s"*bool(len(errs_fl_mv) != 1)} with files missing')

        if len(errs_fl):
            print()
            print('Fixing missing files', end='')
            i, l, L = 0, len(str(len(errs_fl))), len(errs_fl)
            for sub in errs_fl:
                if fatl.sigint_check(): break
                ID = sub[0]
                i += 1
                print(f'\n{i:0>{l}}/{L} - {ID:0>10} {sub[13]}', end='', flush=True)
                if not sub[14]:
                    print(' - Page Error', end='', flush=True)
                    continue
                if not fadl.check_page(Session, 'view/'+str(ID)):
                    print(' - Page Error', end='', flush=True)
                    db.execute(f'UPDATE submissions SET server = 0 WHERE id = {ID}')
                    db.commit()
                    continue
                for f in glob.glob(f'FA.files/{sub[13]}/*'):
                    os.remove(f)
                db.execute(f'DELETE FROM submissions WHERE id = {ID}')
                db.commit()
                fadl.dl_sub(Session, str(ID), f'FA.files/{sub[13]}', db, True, False, 2)

        break

    print()
    index()
    vacuum()

    return Session

def repair_usrs(Session, db):
    print('Analyzing users database for errors ... ', end='', flush=True)
    errs_empty, errs_repet, errs_names, errs_namef, errs_foldr, errs_fl_dl = usr_find_errors(db)
    print('Done')
    print(f'Found {len(errs_empty)} empty user{"s"*bool(len(errs_empty) != 1)}')
    print(f'Found {len(errs_repet)} repeated user{"s"*bool(len(errs_repet) != 1)}')
    print(f'Found {len(errs_names)} capitalized username{"s"*bool(len(errs_names) != 1)}')
    print(f'Found {len(errs_foldr)} empty folder{"s"*bool(len(errs_foldr) != 1)}')
    print(f'Found {len(errs_fl_dl)} empty folder download{"s"*bool(len(errs_fl_dl) != 1)}')

    fatl.sigint_clear()

    while any(len(errs) for errs in (errs_empty, errs_repet, errs_names, errs_names, errs_foldr, errs_fl_dl)):
        if len(errs_empty):
            print()
            print('Empty users')
            for u in errs_empty:
                print(f' {u}')
                fadb.usr_rm(db, u, True)

        if len(errs_repet):
            print()
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
                    fadb.usr_rm(db, u[0])
                fadb.usr_ins(db, u[0])
                fadb.usr_up(db, u[0], u_new[1], 'FOLDERS')
                fadb.usr_up(db, u[0], u_new[2], 'GALLERY')
                fadb.usr_up(db, u[0], u_new[3], 'SCRAPS')
                fadb.usr_up(db, u[0], u_new[4], 'FAVORITES')
                fadb.usr_up(db, u[0], u_new[5], 'EXTRAS')
                if not usr_check_folder(u_new):
                    errs_foldr.append(u_new)
                else:
                    u_d = usr_check_folder_dl(u)
                    if len(u_d):
                        errs_fl_dl.append([u[0], u_d])

        if len(errs_names):
            print()
            print('Capitalized usernames')
            for u in errs_names:
                print(f' {u[0]}')
                fadb.usr_rep(db, u[0], u[0], u[0].lower().replace('_',''), 'USER')
                u_d = usr_check_folder_dl(u)
                if u[1].lower().replace('_','') != u[0]:
                    errs_namef.append(u)
                elif not usr_check_folder(u):
                    errs_foldr.append(u)
                elif len(u_d):
                    errs_fl_dl.append([u[0], u_d])

        if len(errs_namef):
            print()
            print('Incorrect full usernames')
            Session = fadl.session(Session)
            if not Session:
                print('Session error, will attempt manual repair')
            print('-'*47)
            for u in errs_namef:
                print(f' {u[0]} ', end='', flush=True)
                u_db = db.execute(f'SELECT author FROM submissions WHERE authorurl = "{u[0]}"').fetchall()
                if len(u_db):
                    u_db = u_db[0][0]
                    print(f'- db: {u_db}')
                    fadb.usr_rep(db, u[0], u[1], u_db, 'USERFULL')
                elif Session:
                    u_fa = fadl.check_page(Session, 'user/'+u[0])
                    if u_fa:
                        u_fa = u_fa.lstrip('Userpage of ').rstrip(' -- Fur Affinity [dot] net').strip()
                    else:
                        u_fa = u[0]
                    print(f'- FA: {u_fa}')
                    fadb.usr_rep(db, u[0], u[1], u_fa, 'USERFULL')
                u_d = usr_check_folder_dl(u)
                if not usr_check_folder(u):
                    errs_foldr.append(u)
                elif len(u_d):
                    errs_fl_dl.append([u[0], u_d])

        if len(errs_foldr):
            print()
            print('Empty folders')
            for u in errs_foldr:
                print(f' {u[0]}')
                if len(u[3]):
                    fadb.usr_up(db, u[0], 'g', 'FOLDERS')
                if len(u[4]):
                    fadb.usr_up(db, u[0], 's', 'FOLDERS')
                if len(u[5]):
                    fadb.usr_up(db, u[0], 'f', 'FOLDERS')
                if len(u[6]) and 'e' not in u[2] and 'E' not in u[2]:
                    fadb.usr_up(db, u[0], 'e', 'FOLDERS')
                u_d = usr_check_folder_dl(u)
                if len(u_d):
                    errs_fl_dl.append([u[0], u_d])

        if len(errs_fl_dl):
            print()
            print('Missing submissions')
            Session = fadl.session(Session)
            if not Session:
                print('Session error')
                errs_fl_dl = []
            else:
                print('-'*47)
            for u in errs_fl_dl:
                for f in u[1]:
                    fadl.dl_usr(Session, u[0], f, db, False, 2, 0, False)

        break

    print()
    index()
    vacuum()

    return Session

def reapir_info(Session, db):
    print('Analyzing infos database for errors ... ', end='', flush=True)
    print('Done')

def repair_all(Session, db):
    repair_subs(Session, db)
    fatl.sigint_clear()

    repair_usrs(Session, db)
    fatl.sigint_clear()

    return Session

def repair(Session, db):
    menu = (
        ('Submissions', repair_subs),
        ('Users', repair_usrs),
        ('All', repair_all),
        ('Index', index),
        ('Optimize', vacuum),
        ('Return to menu', (lambda *x: x[0]))
    )
    menu = {str(k): mk for k, mk in enumerate(menu, 1)}
    menu_l = [f'{i}) {menu[i][0]}' for i in menu]

    while True:
        fatl.sigint_clear()

        fatl.header('Repair database')

        print('\n'.join(menu_l))
        print('\nChoose option: ', end='', flush=True)
        k = '0'
        while k not in menu:
            k = readkeys.getkey()
            k = k.replace('\x03', str(len(menu)))
            k = k.replace('\x04', str(len(menu)))
            k = k.replace('\x1b', str(len(menu)))
        print(k+'\n')

        if k == str(len(menu)):
            break
        Session = menu[k][1](Session, db)
        fatl.sigint_clear()

        print('-'*30+'\n')

    return Session
