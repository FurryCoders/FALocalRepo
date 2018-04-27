import sqlite3
import sys, os
from math import log10
import PythonRead as readkeys
from FA_db import usr_rep
from FA_dl import session, check_page
from FA_tools import sigint_check

def temp_new():
    print('Creating temporary database ... ', end='', flush=True)
    if os.path.isfile('FA.v2v2_3.db'): os.remove('FA.v2v2_3.db')
    db_new = sqlite3.connect('FA.v2v2_3.db')
    print('Done')

    db_old = sqlite3.connect('FA.db')
    db_old.execute("ATTACH DATABASE 'FA.v2v2_3.db' AS db_new")

    print('Copying INFOS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.INFOS AS SELECT * FROM main.INFOS")
    db_new.execute(f"UPDATE infos SET value = '2.3' WHERE field = 'VERSION'")
    db_old.commit()
    db_new.commit()
    print('Done')

    print('Copying SUBMISSIONS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.SUBMISSIONS AS SELECT * FROM main.SUBMISSIONS")
    db_old.commit()
    print('Done')

    print('Grabbing USERS data .. ', end='', flush=True)
    usrs_old = db_old.execute("SELECT * FROM users ORDER BY name ASC")
    usrs_old = [[ui for ui in u] for u in usrs_old.fetchall()]
    db_old.close()
    print('Done')

    print('Editing USERS data to add new values ... ', end='', flush=True)
    usrs_new = [u[0:1] + ['NULL'] + u[1:] for u in usrs_old]
    print('Done')

    print('Creating new USERS table ... ', end='', flush=True)
    db_new.execute('''CREATE TABLE IF NOT EXISTS USERS
        (NAME TEXT UNIQUE PRIMARY KEY NOT NULL,
        NAMEFULL TEXT NOT NULL,
        FOLDERS TEXT NOT NULL,
        GALLERY TEXT,
        SCRAPS TEXT,
        FAVORITES TEXT,
        EXTRAS TEXT);''')
    db_new.commit()
    print('Done')

    N = len(usrs_new)
    Nl = int(log10(N)+1)
    Ni = 0
    print('Adding USERS to new database ... ', end='', flush=True)
    for u in usrs_new:
        Ni += 1
        print(f'{Ni:0>{Nl}}/{N}', end='', flush=True)
        exists = db_new.execute(f'SELECT EXISTS(SELECT name FROM users WHERE name = "{u[0]}" LIMIT 1);')
        if exists.fetchall()[0][0]:
            return
        try:
            db_new.execute(f'''INSERT INTO USERS
                (NAME,NAMEFULL,FOLDERS,GALLERY,SCRAPS,FAVORITES,EXTRAS)
                VALUES (?,?,?,?,?,?,?)''', u)
        except sqlite3.IntegrityError:
            pass
        except:
            raise
        print('\b \b'+'\b \b'*(Nl*2), end='', flush=True)
    db_new.commit()
    print('Done')

    db_new.close()
    return usrs_new

def temp_import():
    print('Opening temporary database ... ', end='', flush=True)
    db_new = sqlite3.connect('FA.v2v2_3.db')
    print('Done')

    print('Checking temporary database ... ', end='', flush=True)
    infos = bool(db_new.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "INFOS")'))
    users = bool(db_new.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "USERS")'))
    subs = bool(db_new.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "SUBMISSIONS")'))
    if not(infos == users == subs == True):
        print('Tables error')
        return False

    cols = db_new.execute('PRAGMA table_info(users)')
    cols = [col[1] for col in cols.fetchall()]
    if cols != ['NAME','NAMEFULL','FOLDERS','GALLERY','SCRAPS','FAVORITES','EXTRAS']:
        print('Columns error')
        return False

    db_old = sqlite3.connect('FA.db')
    usrs_old = db_old.execute("SELECT * FROM users ORDER BY name ASC").fetchall()
    usrs_new = db_new.execute("SELECT * FROM users ORDER BY name ASC").fetchall()
    if len(usrs_old) != len(usrs_new):
        print('Users error')
        return False

    print('Done')

    db_old.close()
    db_new.close()
    return usrs_new

def db_upgrade_v2v2_3():
    print('The database needs to be upgraded to version 2.3')
    print('This procedure is required to continue using the program')
    print('The current database will be saved in a backup file named FA.v2.db')
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

    if os.path.isfile('FA.v2v2_3.db'):
        usrs_new = temp_import()
        if not usrs_new:
            usrs_new = temp_new()
    else:
        usrs_new = temp_new()
    db_new = sqlite3.connect('FA.v2v2_3.db')

    print()
    Session = session()
    if not Session:
        print('Impossible to connect to the forum')
        print('Please check cookies and status of FA website')
        print('The program will try to update the database manually')
        print('If all necessary data cannot be found in the database the update will be interrupted')
    print()

    N = len(usrs_new)
    Nl = int(log10(N)+1)
    Ni = 0
    missing = []
    missing_db = 0
    print('Getting usernames ... ', end='', flush=True)
    for u in usrs_new:
        Ni += 1
        print(f'{Ni:0>{Nl}}/{N}', end='', flush=True)
        if u[1] != 'NULL':
            print('\b \b'+'\b \b'*(Nl*2), end='', flush=True)
            continue
        u_db = db_new.execute(f'SELECT author FROM submissions WHERE authorurl = "{u[0]}"').fetchall()
        if len(u_db):
            u_db = u_db[0][0]
            usr_rep(db_new, u[0], 'NULL', u_db, 'NAMEFULL')
        elif Session:
            try:
                u_fa = check_page(Session, 'user/'+u[0])
            except:
                print(' Error encountered')
                print('The connection with the forum has encountered an unknown error')
                with open('FA.v2v2_3.error.txt', 'w') as f:
                    err = sys.exc_info()
                    for e in err:
                        f.write(repr(e)+'\n')
                print('Informations on the error have been written to FA.v2v2_3.error.txt')
                print('Update interrupted, it may be resumed later')
                if len(missing) > 0:
                    print(f'Found {len(missing)} user/s no longer present on the website')
                if missing_db > 0:
                    print(f'Found {missing_db} user/s not present in the database')
                print('Closing program')
                sys.exit(0)
            if u_fa:
                u_fa = u_fa.lstrip('Userpage of ').rstrip(' -- Fur Affinity [dot] net').strip()
            else:
                u_fa = u[0]
                missing.append(u[0])
            usr_rep(db_new, u[0], 'NULL', u_fa, 'NAMEFULL')
        else:
            missing_db += 1
        if sigint_check():
            print(' Interrupt')
            print('Update interrupted, it may be resumed later')
            if len(missing) > 0:
                print(f'Found {len(missing)} user/s no longer present on the website')
            if missing_db > 0:
                print(f'Found {missing_db} user/s not present in the database')
            print('Closing program')
            sys.exit(0)
        print('\b \b'+'\b \b'*(Nl*2), end='', flush=True)
    print('Done')

    db_new.close()

    if len(missing) > 0:
        print(f'Found {len(missing)} user/s no longer present on the website:')
        print(' '+'\n '.join(missing))
    if missing_db > 0:
        print(f'Found {missing_db} user/s not present in the database')

    print()

    if missing_db > 0:
        print(f"{missing_db} user/s couldn't be updated")
        print('Update may be resumed later')
        print('Closing program')
        sys.exit(0)

    print('Backing up old database and renaming new one ... ', end='', flush=True)
    os.rename('FA.db', 'FA.v2.db')
    os.rename('FA.v2v2_3.db', 'FA.db')
    print('Done')
