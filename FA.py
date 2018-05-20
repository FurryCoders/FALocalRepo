print('Readying program ... ', end='', flush=True)
import sqlite3
import sys, os
import PythonRead as readkeys
import FA_db as fadb
import FA_dl as fadl
import FA_tools as fatl
import FA_up as faup
import FA_var as favar

def menu(db):
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

        Session = menu[k][1](Session, db)

        print('-'*30+'\n')

fatl.sigint_block()

print('\b \b'*21, end='', flush=True)

if os.path.isfile(favar.db_file):
    faup.db_upgrade()

if os.path.isfile(favar.db_file):
    db = sqlite3.connect(favar.db_file)
else:
    db = sqlite3.connect(favar.db_file)
    fadb.mktable(db, 'submissions')
    fadb.mktable(db, 'users')
    fadb.mktable(db, 'infos')

menu(db)
