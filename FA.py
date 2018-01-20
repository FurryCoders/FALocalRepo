import sqlite3
import re
import sys
import time
import readkeys
import FA_db as fadb
import FA_dl as fadl
import FA_tools as fatl

def download(DB):
    while True:
        users = input('Insert username: ')
        users = users.lower()
        users = re.sub('([^a-zA-Z0-9\-., ])', '', users)
        users = re.sub('( )+', ',', users.strip())
        users = users.split(',')
        users = [u for u in users if u != '']

        sections = input('Insert sections: ')
        sections = re.sub('[^gsfeE]', '', sections)

        speed = 1 ; update = False
        sync = False ; force = 0
        for o in input('Insert options: '):
            if o == 'Q': speed = 2
            elif o == 'S': speed = 0
            elif o == 'U': update = True
            elif o == 'Y': sync = True
            elif o == 'F': force = 1
            elif o == 'A': force = 2
        if force != 0: speed = 1

        if update or (len(users) > 0 and len(sections) > 0):
            break
        else:
            print()

    print()
    Session = fadl.session()
    print()

    if not Session:
        return

    if update:
        print('Update')
        t = int(time.time())
        fadb.info_up(DB, 'LASTUP', t)
        fadb.info_up(DB, 'LASTUPT', 0)
        fadl.update(Session, DB, users, sections, speed, force)
        t = int(time.time()) - t
        fadb.info_up(DB, 'LASTUPT', t)
        fadb.info_up(DB, 'SUBN', fadb.table_n(DB, 'SUBMISSIONS'))
        if fatl.sigint_check(): sys.exit(130)
    else:
        print('Download', end='')
        t = int(time.time())
        fadb.info_up(DB, 'LASTDL', t)
        fadb.info_up(DB, 'LASTDLT', 0)
        for u in users:
            print(f'\n->{u}', end='', flush=True)
            sections_u = sections
            if not fadl.check_page(Session, f'user/{u}'):
                print(' - Failed', end='')
                sections_u = re.sub('[^eE]', '', sections_u)
            print()
            if len(sections_u) == 0: continue
            fadb.ins_usr(DB, u)
            for s in sections_u:
                d = fadl.dl_usr(Session, u, s, DB, sync, speed, force)
                if d in (0,1,2,3,5):
                    if s == 'e':
                        fadb.usr_rep(DB, u, 'E', 'e', 'FOLDERS')
                    elif s == 'E':
                        fadb.usr_rep(DB, u, 'e', 'E', 'FOLDERS')
                    else:
                        fadb.usr_up(DB, u, s, 'FOLDERS')
                elif d == 4:
                    fadb.usr_rep(DB, u, s, s+'!', 'FOLDERS')
                fadb.info_up(DB, 'USRN', fadb.table_n(DB, 'USERS'))
                fadb.info_up(DB, 'SUBN', fadb.table_n(DB, 'SUBMISSIONS'))
                if d == 5: sys.exit(130)
        t = int(time.time()) - t
        fadb.info_up(DB, 'LASTDLT', t)

def menu(DB):
    menu = []
    menu.append(f'{len(menu)+1}) Download & Update')
    menu.append(f'{len(menu)+1}) Search')
    menu.append(f'{len(menu)+1}/ESC) Exit')

    while True:
        print('-'*20)
        print('Main Menu')
        print('-'*20)
        print()
        print('\n'.join(menu))
        print()
        print('Choose option: ', end='', flush=True)
        o = ''
        while o not in [str(n) for n in range(1, len(menu)+1)]+['\x1b']:
            o = readkeys.getkey()
            if o == '\x03': sys.exit(130)
        print(repr(o))
        print()

        if o == '1':
            print('-'*20)
            print('Download & Update')
            print('-'*20)
            print()
            download(DB)
        elif o == '2':
            print('-'*20)
            print('Search')
            print('-'*20)
            print()
            fatl.db_search(DB)
        elif o in (str(len(menu)), '\x1b'):
            return

        print()
        print('-'*30)
        print()


fatl.sigint_block()

DB = sqlite3.connect('FA.db')
fadb.mktable(DB, 'submissions')
fadb.mktable(DB, 'users')
fadb.mktable(DB, 'infos')

menu(DB)

fatl.sigint_ublock()
