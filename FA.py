import sqlite3
import sys
import PythonRead as readkeys
import FA_db as fadb
import FA_dl as fadl
import FA_tools as fatl
import FA_up as faup

def menu(DB):
    menu = (
        ('Download & Update', fadl.download_main),
        ('Search', fadb.db_search),
        ('Repair database', fadb.repair),
        ('Exit', (lambda *x: sys.exit(0)))
    )
    menu = {str(k): mk for k, mk in enumerate(menu, 1)}

    menu_l = [f'{i}) {menu[i][0]}' for i in menu]

    Session = None

    while True:
        fatl.sigint_clear()

        fatl.header('Menu')

        print('\n'.join(menu_l))
        print('\nChoose option: ', end='', flush=True)
        k = '0'
        while k not in menu:
            k = readkeys.getkey()
            k = k.replace('\x03', str(len(menu)))
            k = k.replace('\x04', str(len(menu)))
            k = k.replace('\x1b', str(len(menu)))
        print(k+'\n')

        Session = menu[k][1](Session, DB)

        print('-'*30+'\n')

fatl.sigint_block()

faup.db_upgrade()

DB = sqlite3.connect('FA.db')
fadb.mktable(DB, 'submissions')
fadb.mktable(DB, 'users')
fadb.mktable(DB, 'infos')

menu(DB)
