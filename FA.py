import sqlite3
import re
import FA_DL as fadl
import FA_DB as fadb

users = input('Insert username: ')
users = re.sub('( ){2,}', ' ', users.strip())
users = re.sub('([^a-zA-Z0-9\-. ])', '', users.strip())
users = users.split(' ')

sections = input('Insert sections: ')
sections = [s for s in sections if s in ('g','s','f','e','E')]

speed = 1 ; update = False ; sync = False
for o in input('Insert options: '):
    if o == 'Q': speed = 2
    elif o == 'S': speed = 0
    elif o == 'U': update = True
    elif o == 'Y': sync = True

if not update and (len(users) == 0 or len(sections) == 0): exit(1)

print()

try:
    try: Session = fadl.make_session()
    except FileNotFoundError: exit(1)
    if not fadl.check_cookies(Session): exit(2)

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
        fadl.update(Session, DB, users, sections)
    else:
        print('Download', end='')
        for u in users:
            print(f'\n->{u}', end='', flush=True)
            if not fadl.check_page(Session, f'user/{u}'):
                print(' - Failed')
                continue
            else:
                print()
            fadb.db_ins_usr(DB, u)
            for s in sections:
                if fadl.dl_usr(Session, u, s, DB, sync, speed):
                    if s == 'e':
                        fadb.db_usr_rep(DB, u, 'E', 'e', 'FOLDERS')
                    elif s == 'E':
                        fadb.db_usr_rep(DB, u, 'e', 'E', 'FOLDERS')
                    else:
                        fadb.db_usr_up(DB, u, s, 'FOLDERS')
except KeyboardInterrupt:
    exit()
