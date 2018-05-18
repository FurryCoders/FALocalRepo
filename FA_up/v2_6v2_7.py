import sqlite3
import sys, os
import PythonRead as readkeys
from FA_db import mkindex

def temp_new():
    print('Creating temporary database ... ', end='', flush=True)
    if os.path.isfile('FA.v2_6v2_7.db'): os.remove('FA.v2_6v2_7.db')
    db_new = sqlite3.connect('FA.v2_6v2_7.db')
    print('Done')

    db_old = sqlite3.connect('FA.db')
    db_old.execute("ATTACH DATABASE 'FA.v2_6v2_7.db' AS db_new")

    print('Copying INFOS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.INFOS AS SELECT * FROM main.INFOS")
    db_old.commit()
    print('Done')

    print('Copying USERS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.USERS AS SELECT * FROM main.USERS")
    db_old.commit()
    print('Done')

    print('Copying SUBMISSIONS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.SUBMISSIONS AS SELECT * FROM main.SUBMISSIONS")
    db_old.commit()
    print('Done')

    db_old.close()
    print('Adding new INFOS entry ... ', end='', flush=True)
    db_new.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("INDEX", 0)')
    db_new.commit()
    print('Done')

    return db_new

def db_upgrade_v2_6v2_7():
    print('The database needs to be upgraded to version 2.7')
    print('This procedure is required to continue using the program')
    print('The current database will be saved in a backup file named FA.v2_6.db')
    print('WARNING: This update cannot be interrupted and resumed')
    print('This procedure can take a long time, do you want to continue? ', end='', flush=True)
    c = ''
    while c not in ('y','n'):
        c = readkeys.getkey().lower()
        if c in ('\x03', '\x04'):
            print('n')
            sys.exit(130)
    print(c)
    if c == 'n':
        sys.exit(0)

    print()

    db_new = temp_new()

    print('Indexing entries ... ', end='', flush=True)
    mkindex(db_new)
    print('Done')

    print('Updating VERSION to 2.7 ... ', end='', flush=True)
    db_new.execute(f"UPDATE infos SET value = '2.7' WHERE field = 'VERSION'")
    db_new.commit()
    db_new.close()
    print('Done')

    print()

    print('Backing up old database and renaming new one ... ', end='', flush=True)
    os.rename('FA.db', 'FA.v2_6.db')
    os.rename('FA.v2_6v2_7.db', 'FA.db')
    print('Done')
