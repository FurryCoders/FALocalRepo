import sqlite3
import sys, os
import FA_tools as fatl
import FA_var as favar
from .v1v2 import db_upgrade_v1v2
from .v2v2_3 import db_upgrade_v2v2_3
from .v2_3v2_6 import db_upgrade_v2_3v2_6
from .v2_6v2_7 import db_upgrade_v2_6v2_7

def db_upgrade_main():
    fatl.log.normal('DB UPGRADE -> start')
    print('Checking database file ... ', end='', flush=True)

    db = sqlite3.connect(favar.db_file)
    tables = db.execute('''SELECT name FROM sqlite_master
        WHERE type = "table" AND
            (
            name = "SUBMISSIONS" OR
            name = "USERS" OR
            name = "INFOS"
            )''').fetchall()
    db.close()

    print('\b \b'*27, end='', flush=True)

    if len(tables) != 3:
        os.remove(favar.db_file)
        return

    while True:
        print('Checking database for upgrade ... ', end='', flush=True)
        db = sqlite3.connect(favar.db_file)
        db_version = db.execute('SELECT value FROM infos WHERE field = "VERSION"').fetchall()
        db.close()

        if len(db_version) == 0:
            db_version = '1.0'
        else:
            db_version = db_version[0][0]

        db_upgrade = False
        print('\b \b'*34, end='', flush=True)

        if db_version < '2.0':
            db_upgrade = db_upgrade_v1v2
        elif db_version < '2.3':
            db_upgrade = db_upgrade_v2v2_3
        elif db_version < '2.6':
            db_upgrade = db_upgrade_v2_3v2_6
        elif db_version < '2.7':
            db_upgrade = db_upgrade_v2_6v2_7
        elif db_version > favar.fa_version:
            print('Program is not up to date')
            print(f'FA version: {favar.fa_version}')
            print(f'DB version: {infos["VERSION"]}')
            print('Use a program version equal or higher')
            fatl.log.normal(f'DB UPGRADE -> version error FA:{favar.fa_version} DB:{infos["VERSION"]}')
            fatl.log.normal('PROGRAM END')
            sys.exit(1)

        if db_upgrade:
            fatl.log.normal('DB UPGRADE -> '+db_upgrade.__name__)
            fatl.header('Database version upgrade')
            db_upgrade()
            print()
        else:
            break

    fatl.log.normal('DB UPGRADE -> end')
