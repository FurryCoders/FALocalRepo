import sqlite3
import re
import sys
import FA_DL as fadl
import FA_DB as fadb

try:
    users = input('Insert username: ')
    users = re.sub('([^a-zA-Z0-9\-., ])', '', users)
    users = re.sub('( )+', ',', users.strip())
    users = users.split(',')
    users = [u for u in users if u != '']

    sections = input('Insert sections: ')
    sections = [s for s in sections if s in ('g','s','f','e','E')]

    speed = 1 ; update = False
    sync = False ; force = 0
    for o in input('Insert options: '):
        if o == 'Q': speed = 2
        elif o == 'S': speed = 0
        elif o == 'U': update = True
        elif o == 'Y': sync = True
        elif o == 'F': force = 1
        elif o == 'A': force = 2
    if force != 0: speed = 1

    if not update and (len(users) == 0 or len(sections) == 0): sys.exit(1)
except KeyboardInterrupt:
    print('\033[2D  \033[2D', end='', flush=True)
    sys.exit(0)

print()

try:
    try: Session = fadl.make_session()
    except FileNotFoundError: sys.exit(1)
    if not fadl.check_cookies(Session): sys.exit(2)

    DB = sqlite3.connect('FA.db')
    DB.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
        (ID INT UNIQUE PRIMARY KEY NOT NULL,
        AUTHOR TEXT NOT NULL,
        AUTHORURL TEXT NOT NULL,
        TITLE TEXT,
        UDATE CHAR(10) NOT NULL,
        TAGS TEXT,
        FILELINK TEXT,
        FILENAME TEXT,
        LOCATION TEXT NOT NULL);''')
    DB.execute('''CREATE TABLE IF NOT EXISTS USERS
        (NAME TEXT UNIQUE PRIMARY KEY NOT NULL,
        FOLDERS CHAR(4) NOT NULL,
        GALLERY TEXT,
        SCRAPS TEXT,
        FAVORITES TEXT,
        EXTRAS TEXT);''')

    if update:
        print('Update')
        fadl.update(Session, DB, users, sections, force)
    else:
        print('Download', end='')
        for u in users:
            print(f'\n->{u}', end='', flush=True)
            if not fadl.check_page(Session, f'user/{u}'):
                print(' - Failed')
                continue
            else:
                print()
            fadb.ins_usr(DB, u)
            for s in sections:
                d = fadl.dl_usr(Session, u, s, DB, sync, speed, force)
                if d in (0,1,2,3):
                    if s == 'e':
                        fadb.usr_rep(DB, u, 'E', 'e', 'FOLDERS')
                    elif s == 'E':
                        fadb.usr_rep(DB, u, 'e', 'E', 'FOLDERS')
                    else:
                        fadb.usr_up(DB, u, s, 'FOLDERS')
                elif d == 4:
                    fadb.usr_rep(DB, u, s, s+'!', 'FOLDERS')
except KeyboardInterrupt:
    print('\033[2D  \033[2D', end='', flush=True)
    sys.exit(0)
