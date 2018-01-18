import sqlite3
import re
import sys
import FA_db as fadb
import FA_dl as fadl

if sys.platform not in ('win32', 'cygwin'):
    import signal
    signal_flag = True
else:
    signal_flag = False

def session():
    print('Checking connection ... ', end='', flush=True)
    if fadl.ping('http://www.furaffinity.net'):
        print('Done')
    else:
        print('Failed')
        sys.exit(2)

    print('Creating session & adding cookies ... ', end='', flush=True)
    try:
        Session = fadl.session_make()
        print('Done')
    except FileNotFoundError:
        print('Failed')
        sys.exit(3)

    print('Checking cookies & bypassing cloudflare ... ', end='', flush=True)
    if fadl.check_cookies(Session):
        print('Done')
    else:
        print('Failed')
        sys.exit(4)
    return Session

try:
    users = input('Insert username: ')
    users = users.lower()
    users = re.sub('([^a-zA-Z0-9\-., ])', '', users)
    users = re.sub('( )+', ',', users.strip())
    users = users.split(',')
    users = [u for u in users if u != '']

    sections = input('Insert sections: ')
    sections = re.sub('[^gsfeE]', '', sections)

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
    print('\033[2D  \033[2D', flush=True)
    sys.exit(0)

print()

try:
    Session = session()
    print()

    DB = sqlite3.connect('FA.db')
    fadb.mktable(DB, 'submissions')
    fadb.mktable(DB, 'users')
    fadb.mktable(DB, 'infos')

    if signal_flag:
        signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT})

    if update:
        print('Update')
        fadl.update(Session, DB, users, sections, speed, force)
        if signal_flag:
            if signal.SIGINT in signal.sigpending():  sys.exit(130)
    else:
        print('Download', end='')
        for u in users:
            print(f'\n->{u}', end='', flush=True)
            sections_u = sections
            if not fadl.check_page(Session, f'user/{u}'):
                print(' - Failed', end='')
                sections_u = re.sub('[^eE]', '', sections_u)
            print()
            if len(sections_u) == 0: continue
            fadb.ins_usr(DB, u)
            for s in sections_u:
                d = fadl.dl_usr(Session, u, s, DB, sync, speed, force)
                if d in (0,1,2,3,5):
                    if s == 'e':
                        fadb.usr_rep(DB, u, 'E', 'e', 'FOLDERS')
                    elif s == 'E':
                        fadb.usr_rep(DB, u, 'e', 'E', 'FOLDERS')
                    else:
                        fadb.usr_up(DB, u, s, 'FOLDERS')
                elif d == 4:
                    fadb.usr_rep(DB, u, s, s+'!', 'FOLDERS')
                if d == 5: sys.exit(130)

    if signal_flag:
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT})
except KeyboardInterrupt:
    print('\033[2D  \033[2D', flush=True)
    sys.exit(0)
