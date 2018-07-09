print('Readying program ... ', end='', flush=True)
import sqlite3
import sys, os
import traceback
import PythonRead as readkeys
import FA_db as fadb
import FA_dl as fadl
import FA_tools as fatl
import FA_up as faup
import FA_var as favar

def menu():
    menu = (
        ('Download & Update', fadl.download_main),
        ('Search', fadb.db_search),
        ('Repair database', fadb.repair),
        ('Exit', sys.exit)
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

        fatl.log.normal('MAIN MENU -> '+menu[k][0])
        menu[k][1]()

        print('-'*30+'\n')

try:
    fatl.log.log_trim()
    fatl.log.log_start()
    fatl.log.normal('PROGRAM START')

    fatl.sigint_block()

    print('\b \b'*21, end='', flush=True)

    if os.path.isfile(favar.variables.db_file):
        faup.db_upgrade()

    if os.path.isfile(favar.variables.db_file):
        fatl.log.normal('DB -> connect')
        favar.variables.db = sqlite3.connect(favar.variables.db_file)
    else:
        fatl.log.normal('DB -> connect')
        favar.variables.db = sqlite3.connect(favar.variables.db_file)
        print('Creating database & tables ... ', end='', flush=True)
        fatl.log.normal('DB -> create')
        fadb.mktable('submissions')
        fadb.mktable('users')
        fadb.mktable('infos')
        print('\b \b'*31, end='', flush=True)

    menu()
except SystemExit:
    fatl.log.normal('PROGRAM END')
    raise
except:
    err = traceback.format_exception(*sys.exc_info())
    err = ['ERROR EXIT -> '+e.strip().replace('\n', ' =') for e in err]
    fatl.log.warning(err)
    fatl.log.warning('PROGRAM END')
    if '--raise' in sys.argv[1:]:
        raise
    else:
        print('\nAn unknown error occurred:')
        print('See FA.log for details')
        sys.exit(1)
