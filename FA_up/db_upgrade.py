import sqlite3
import sys, os
import FA_tools as fatl
import FA_var as favar
from .v1v2 import db_upgrade_v1v2
from .v2v2_3 import db_upgrade_v2v2_3
from .v2_3v2_6 import db_upgrade_v2_3v2_6
from .v2_6v2_7 import db_upgrade_v2_6v2_7

def db_upgrade_main():
    print('Checking database for upgrade ... ', end='', flush=True)
    db = sqlite3.connect(favar.db_file)
    tables = db.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()
    db.close()
    tables = [t[0] for t in tables]
    print('\b \b'*34, end='', flush=True)
    if any(t not in tables for t in ('SUBMISSIONS','USERS','INFOS')):
        os.remove(favar.db_file)
        return

    while True:
        print('Checking database for upgrade ... ', end='', flush=True)
        db = sqlite3.connect(favar.db_file)
        infos = db.execute('SELECT FIELD, VALUE FROM INFOS').fetchall()
        db.close()

        infos = {i[0]: i[1] for i in infos}
        if 'VERSION' not in infos.keys():
            infos['VERSION'] = '1.0'

        db_upgrade = False
        print('\b \b'*34, end='', flush=True)

        if infos['VERSION'] < '2.0':
            db_upgrade = db_upgrade_v1v2
        elif infos['VERSION'] < '2.3':
            db_upgrade = db_upgrade_v2v2_3
        elif infos['VERSION'] < '2.6':
            db_upgrade = db_upgrade_v2_3v2_6
        elif infos['VERSION'] < '2.7':
            db_upgrade = db_upgrade_v2_6v2_7
        elif infos['VERSION'] > favar.fa_version:
            print('Program is not up to date')
            print(f'FA version: {favar.fa_version}')
            print(f'DB version: {infos["VERSION"]}')
            print('Use a program version equal or higher')
            sys.exit(1)

        if db_upgrade:
            fatl.header('Database version upgrade')
            db_upgrade()
            print()
        else:
            break
