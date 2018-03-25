import sqlite3
import sys
import time
import readkeys
import FA_db as fadb
import FA_dl as fadl
import FA_tools as fatl
import FA_up as faup

def menu(DB):
    menu = []
    menu.append(f'{len(menu)+1}) Download & Update')
    menu.append(f'{len(menu)+1}) Search')
    menu.append(f'{len(menu)+1}) Repair database')
    menu.append(f'{len(menu)+1}/ESC) Exit')

    Session = None

    while True:
        print('-'*20)
        print('Main Menu')
        print('-'*20)
        print()
        print('\n'.join(menu))
        print()
        print('Choose option: ', end='', flush=True)
        o = ''
        while o not in [str(n) for n in range(1, len(menu)+1)]+['ESC']:
            o = readkeys.getkey()
            if o == '\x03': sys.exit(130)
            elif o == '\x1b': o = 'ESC'
        print(repr(o))
        print()

        if o == '1':
            print('-'*20)
            print('Download & Update')
            print('-'*20)
            print()
            Session = fadl.download_main(Session, DB)
        elif o == '2':
            print('-'*20)
            print('Search')
            print('-'*20)
            print()
            fatl.db_search(DB)
        elif o == '3':
            print('-'*20)
            print('Repair database')
            print('-'*20)
            print()
            Session = fadb.repair(Session, DB)
        elif o in (str(len(menu)), 'ESC'):
            return

        print()
        print('-'*30)
        print()


fatl.sigint_block()

faup.db_upgrade()

DB = sqlite3.connect('FA.db')
fadb.mktable(DB, 'submissions')
fadb.mktable(DB, 'users')
fadb.mktable(DB, 'infos')

menu(DB)
