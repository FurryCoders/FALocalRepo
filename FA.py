import sqlite3
import sys
import PythonRead as readkeys
import FA_db as fadb
import FA_dl as fadl
import FA_tools as fatl
import FA_up as faup

def header(s, end='\n', l=20):
    print('-'*l)
    print(s)
    print('-'*l)
    print(end=end)

def menu(DB):
    menu = {}
    menu[str(len(menu)+1)] = ['Download & Update', fadl.download_main]
    menu[str(len(menu)+1)] = ['Search', fadb.db_search]
    menu[str(len(menu)+1)] = ['Repair database', fadb.repair]
    menu[str(len(menu)+1)] = ['Exit', (lambda x,y: sys.exit(0))]

    Session = None

    while True:
        fatl.sigint_clear()

        header('Menu')

        print('\n'.join([f'{i}) {menu[i][0]}' for i in menu]))
        print('\nChoose option: ', end='', flush=True)
        k = '0'
        while k not in menu:
            k = readkeys.getkey()
            k = k.replace('\x03', str(len(menu)))
            k = k.replace('\x1b', str(len(menu)))
        print(k+'\n')

        header(menu[k][0])
        Session = menu[k][1](Session, DB)

        print(-'*30'+'\n')

fatl.sigint_block()

faup.db_upgrade()

DB = sqlite3.connect('FA.db')
fadb.mktable(DB, 'submissions')
fadb.mktable(DB, 'users')
fadb.mktable(DB, 'infos')

menu(DB)
