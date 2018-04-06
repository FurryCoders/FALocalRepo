import sqlite3
import sys, os
import bs4
import re
from math import log10
from FA_db import sub_up
from FA_dl import session
from FA_tools import tiers, sigint_check
from readkeys import getkey

def dl_values(Session, ID):
    url = f'https://www.furaffinity.net/view/{ID}'
    page = Session.get(url)
    page = bs4.BeautifulSoup(page.text, 'lxml')

    if page == None or page.find('meta', {"property":"og:title"}) == None:
        return False

    data = []

    extras = [str(e) for e in page.find('div', 'sidebar-section-no-bottom').find_all('div')]
    extras = [e.rstrip('</div>') for e in extras]
    extras = [re.sub('.*> ', '', e).replace('&gt;', '>') for e in extras]
    # [category, species, gender]

    rating = page.find('meta', {"name":"twitter:data2"})
    rating = rating.get('content').lower()

    data += extras
    data.append(rating)

    return data

def temp_new():
    print('Creating temporary database ... ', end='', flush=True)
    if os.path.isfile('FA.v1v2.db'): os.remove('FA.v1v2.db')
    db_new = sqlite3.connect('FA.v1v2.db')
    print('Done')

    db_old = sqlite3.connect('FA.db')
    db_old.execute("ATTACH DATABASE 'FA.v1v2.db' AS db_new")

    print('Copying INFOS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.INFOS AS SELECT * FROM main.INFOS")
    db_new.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("VERSION", "2.0")')
    db_old.commit()
    db_new.commit()
    print('Done')

    print('Copying USERS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.USERS AS SELECT * FROM main.USERS")
    db_old.commit()
    print('Done')

    print('Finding all submissions ... ', end='', flush=True)
    subs_old = db_old.execute("SELECT * FROM submissions ORDER BY id ASC")
    subs_old = [[si for si in s] for s in subs_old.fetchall()]
    db_old.close()
    print('Done')

    db_new = sqlite3.connect('FA.v1v2.db')

    db_new.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
        (ID INT UNIQUE PRIMARY KEY NOT NULL,
        AUTHOR TEXT NOT NULL,
        AUTHORURL TEXT NOT NULL,
        TITLE TEXT,
        UDATE CHAR(10) NOT NULL,
        TAGS TEXT,
        CATEGORY TEXT,
        SPECIES TEXT,
        GENDER TEXT,
        RATING TEXT,
        FILELINK TEXT,
        FILENAME TEXT,
        LOCATION TEXT NOT NULL,
        SERVER INT);''')

    print('Editing submissions data to add new values ... ', end='', flush=True)
    subs_new = [s[0:6] + ['NULL']*4 + s[6:9] + [1] for s in subs_old]
    print('Done')

    N = len(subs_new)
    Nl = int(log10(N)+1)
    Ni = 0
    print('Adding submissions to new database ... ', end='', flush=True)
    for s in subs_new:
        Ni += 1
        print(f'{Ni:0>{Nl}}/{N}', end='', flush=True)
        try:
            db_new.execute(f'''INSERT INTO SUBMISSIONS
            (ID,AUTHOR,AUTHORURL,TITLE,UDATE,TAGS,CATEGORY,SPECIES,GENDER,RATING,FILELINK,FILENAME,LOCATION, SERVER)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', s)
        except sqlite3.IntegrityError:
            pass
        print('\b \b'+'\b \b'*(Nl*2), end='', flush=True)
    db_new.commit()
    print('Done')

    db_new.close()
    return subs_new

def temp_import():
    print('Opening temporary database ... ', end='', flush=True)
    db_new = sqlite3.connect('FA.v1v2.db')
    print('Done')

    print('Checking temporary database ... ', end='', flush=True)
    infos = bool(db_new.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "INFOS")'))
    users = bool(db_new.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "USERS")'))
    subs = bool(db_new.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "SUBMISSIONS")'))
    if not(infos == users == subs == True):
        print('Tables error')
        return False

    cols = db_new.execute('PRAGMA table_info(submissions)')
    cols = [col[1] for col in cols.fetchall()]
    if cols != ['ID','AUTHOR','AUTHORURL','TITLE','UDATE','TAGS','CATEGORY','SPECIES','GENDER','RATING','FILELINK','FILENAME','LOCATION','SERVER']:
        print('Columns error')
        return False

    subs_new = db_new.execute('SELECT * FROM submissions')
    subs_new = subs_new = [[si for si in s] for s in subs_new.fetchall()]
    db_old = sqlite3.connect('FA.db')
    subs_old = db_old.execute('SELECT * FROM submissions')
    subs_old = subs_old = [[si for si in s] for s in subs_old.fetchall()]
    if len(subs_new) != len(subs_old):
        print('Submissions error')
        return False

    print('Done')

    db_old.close()
    db_new.close()
    return subs_new

def db_upgrade_v1v2():
    print('The database needs to be upgraded to version 2.0')
    print('This procedure is required to continue using the program')
    print('The current database will be saved in a backup file named FA.v1.db')
    print('This procedure can take a long time, do you want to continue? ', end='', flush=True)
    c = ''
    while c not in ('y','n'):
        c = getkey().lower()
        if c in ('\x03', '\x04'):
            print('n')
            sys.exit(130)
    print(c)
    if c == 'n': sys.exit(0)

    print()

    if os.path.isfile('FA.v1v2.db'):
        subs_new = temp_import()
        if not subs_new:
            subs_new = temp_new()
    else:
        subs_new = temp_new()
    db_new = sqlite3.connect('FA.v1v2.db')

    print()
    Session = session()
    if not Session:
        print('Impossible to connect to the forum, update interrupted')
        print('Please check cookies and status of FA website')
        print('Cleaning up temporary files ... ', end='', flush=True)
        db_new.close()
        os.remove('FA.v1v2.db')
        print('Done')
        print('Closing program')
        sys.exit(0)
    print()

    N = len(subs_new)
    Nl = int(log10(N)+1)
    Ni = 0
    missing = 0
    fields = ['CATEGORY','SPECIES','GENDER','RATING']
    print('Getting new values from FA ... ', end='', flush=True)
    for s in subs_new:
        Ni += 1
        print(f'{Ni:0>{Nl}}/{N}', end='', flush=True)
        if s[6] != 'NULL':
            print('\b \b'+'\b \b'*(Nl*2), end='', flush=True)
            continue
        try:
            values = dl_values(Session, s[0])
        except:
            print(' Error encountered')
            print('The connection with the forum has encountered an unknown error')
            with open('FA.v1v2.error.txt', 'w') as f:
                err = sys.exc_info()
                for e in err:
                    f.write(repr(e)+'\n')
            print('Informations on the error have been written to FA.v1v2.error.txt')
            print('Update interrupted, it may be resumed later')
            if missing > 0:
                print(f'Found {missing} submission/s no longer present on the website')
            print('Closing program')
            sys.exit(0)
        if not values:
            values = ['All > All', 'Unspecified / Any', 'Any', 'general']
            sub_up(db_new, s[0], values+[0], fields+['SERVER'])
            missing += 1
        else:
            sub_up(db_new, s[0], values, fields)
        if sigint_check():
            print(' Interrupt')
            print('Update interrupted, it may be resumed later')
            if missing > 0:
                print(f'Found {missing} submission/s no longer present on the website')
            print('Closing program')
            sys.exit(0)
        print('\b \b'+'\b \b'*(Nl*2), end='', flush=True)
    print('Done')

    if missing > 0:
        print(f'Found {missing} submission/s no longer present on the website')

    db_new.close()

    print()
    print('Backing up old database and renaming new one ... ', end='', flush=True)
    os.rename('FA.db', 'FA.v1.db')
    os.rename('FA.v1v2.db', 'FA.db')
    print('Done')
