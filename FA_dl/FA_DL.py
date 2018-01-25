import requests, cfscrape, json, bs4
import os, sys, time
import re
import sqlite3
from FA_tools import sigint_check, tiers
import FA_db as fadb
from .FA_DLSUB import dl_sub, str_clean

section_full = {
    'g' : 'gallery',
    's' : 'scraps',
    'f' : 'favorites',
    'e' : 'extra (partial)',
    'E' : 'extra (full)'
    }
section_db = {
    'g' : 'GALLERY',
    's' : 'SCRAPS',
    'f' : 'FAVORITES',
    'e' : 'EXTRAS',
    'E' : 'EXTRAS'
    }

def ping(url):
    try:
        requests.get(url, stream=True)
        return True
    except:
        return False

def session_make(cookies_file='FA.cookies'):
    Session = cfscrape.create_scraper()

    try:
        with open(cookies_file) as f: cookies = json.load(f)
    except FileNotFoundError:
        raise

    for cookie in cookies: Session.cookies.set(cookie['name'], cookie['value'])

    return Session

def check_cookies(Session):
    check_r = Session.get('https://www.furaffinity.net/controls/settings/')
    check_p = bs4.BeautifulSoup(check_r.text, 'lxml')

    if check_p.find('a', id='my-username') is None:
        return False
    else:
        return True

def session(Session=None):
    print('Checking connection ... ', end='', flush=True)
    if ping('http://www.furaffinity.net'):
        print('Done')
    else:
        print('Failed')
        return False

    if not Session:
        print('Creating session & adding cookies ... ', end='', flush=True)
        try:
            Session = session_make()
            print('Done')
        except FileNotFoundError:
            print('Failed')
            return False

        print('Checking cookies & bypassing cloudflare ... ', end='', flush=True)
        if check_cookies(Session):
            print('Done')
        else:
            print('Failed')
            return False

    return Session

def check_page(Session, url):
    page_r = Session.get('https://www.furaffinity.net/'+url)
    page_t = bs4.BeautifulSoup(page_r.text, 'lxml').title.string

    if page_t == 'System Error': return False
    elif page_t == 'Account disabled. -- Fur Affinity [dot] net': return False
    elif page_r.status_code == 404: return False

    return True

def dl_url(section, usr):
    url ='https://www.furaffinity.net/'
    if section in ('g', 's', 'f'):
        url += '{}/{}/'.format(section_full[section], usr)
    elif section == 'e':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" ) ! ( @lower {0} )&order-by=date&page='.format(usr)
    elif section == 'E':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" | "{0}" ) ! ( @lower {0} )&order-by=date&page='.format(usr)

    return url

def dl_usr(Session, user, section, DB, sync=False, speed=1, force=0):
    url = dl_url(section, user)
    print(f'-->{section_full[section]}')

    page_i = 1
    while True:
        page_r = Session.get(url+str(page_i))
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        if section in ('e', 'E'):
            page_p = page_p.find('section', id="gallery-search-results")
        elif section == 'f':
            page_p = page_p.find('section', id="gallery-favorites")
        else:
            page_p = page_p.find('section', id="gallery-gallery")

        if page_p == None:
            if section in ('e','E'):
                print("--->No submissions to download")
                return 1
            elif page_i == 1:
                return 4
            else:
                return 0

        if page_p.find('figure') is None:
            if page_i == 1:
                print("--->No submissions to download")
                return 1
            else:
                return 0

        sub_i = 0
        for sub in page_p.findAll('figure'):
            if sigint_check(): return 5

            sub_i += 1
            ID = sub.get('id')[4:]
            print(f'--->{page_i:03d}/{sub_i:02d}) {ID:0>10} - ', end='', flush=True)
            folder = f'FA.files/{tiers(ID)}/{ID:0>10}'

            if fadb.usr_src(DB, user, ID.zfill(10), section_db[section]):
                cols = os.get_terminal_size()[0] - 38
                if cols < 0: cols = 0
                titl = str_clean(sub.find_all('a')[1].string)
                print(f'{titl[0:cols]} | Repository')
                if sync:
                    if force > 0 and page_i <= force: continue
                    if force == -1: continue
                    if sub_i+page_i == 2: return 3
                    else: return 2
                continue

            if sigint_check(): return 5

            s_ret = dl_sub(Session, ID, folder, DB, False, True, speed)
            if s_ret == 0:
                print("\b"*5+" | Downloaded")
                fadb.usr_up(DB, user, ID.zfill(10), section_db[section])
            elif s_ret == 1:
                print("\b"*5+" | File Error")
                fadb.usr_up(DB, user, ID.zfill(10), section_db[section])
            elif s_ret == 2:
                print("\b"*5+" | Repository")
                fadb.usr_up(DB, user, ID.zfill(10), section_db[section])
            elif s_ret == 3:
                print("\b"*5+" | Page Error")

            if sigint_check(): return 5

        page_i += 1

def update(Session, DB, users=[], sections=[], speed=2, force=0):
    users_db = DB.execute("SELECT name, folders FROM users ORDER BY name ASC")
    download = False
    for u in users_db:
        if len(users) != 0 and u[0] not in users: continue
        download_u = False
        print(f'->{u[0]}')
        for s in u[1].split(','):
            if len(sections) != 0 and s not in sections: continue
            if s[-1] == '!': continue
            d = dl_usr(Session, u[0], s, DB, True, speed, force)
            if d in (0,2):
                if force not in (1,2): print('\033[1A\033[2K', end='', flush=True)
                download_u = True
            elif d in (1,3):
                    if force not in (1,2): print('\033[1A\033[2K\033[1A\033[2K', end='', flush=True)
            elif d == 4:
                print('\033[1A\033[2K', end='', flush=True)
                print(f'-->{section_full[s]} DISABLED')
                fadb.usr_rep(DB, u[0], s, s+'!', 'FOLDERS')
                download_u = True
            if d == 5: return
            if sigint_check(): return
        if not download_u:
            if force not in (1,2): print('\033[1A\033[2K', end='', flush=True)
        else: download = True
    if not download: print("Nothing new to download")


def download(Session, DB):
    while True:
        users = input('Insert username: ')
        users = users.lower()
        users = re.sub('([^a-zA-Z0-9\-., ])', '', users)
        users = re.sub('( )+', ',', users.strip())
        users = users.split(',')
        users = [u for u in users if u != '']

        sections = input('Insert sections: ')
        sections = re.sub('[^gsfeE]', '', sections)

        speed = 1 ; upd = False
        sync = False ; force = 0
        options = input('Insert options: ')
        if 'quick' in options: speed = 2
        if 'slow' in options: speed = 0
        if 'update' in options: upd = True
        if 'sync' in options: sync = True
        if 'all' in options: force = -1
        if re.search('force[0-9]+', options):
            force = re.search('force[0-9]+', options).group(0).lstrip('force')
            force = int(force)
        if force != 0: speed = 1

        if upd or (len(users) > 0 and len(sections) > 0):
            break
        else:
            print()

    print()
    Session = session(Session)
    print()

    if not Session:
        print('Session error')
        return None

    if upd:
        print('Update')
        t = int(time.time())
        fadb.info_up(DB, 'LASTUP', t)
        fadb.info_up(DB, 'LASTUPT', 0)
        update(Session, DB, users, sections, speed, force)
        t = int(time.time()) - t
        fadb.info_up(DB, 'LASTUPT', t)
        fadb.info_up(DB, 'SUBN', fadb.table_n(DB, 'SUBMISSIONS'))
        if sigint_check(): return Session
    else:
        print('Download', end='')
        t = int(time.time())
        fadb.info_up(DB, 'LASTDL', t)
        fadb.info_up(DB, 'LASTDLT', 0)
        for u in users:
            print(f'\n->{u}', end='', flush=True)
            sections_u = sections
            if not check_page(Session, f'user/{u}'):
                print(' - Failed', end='')
                sections_u = re.sub('[^eE]', '', sections_u)
            print()
            if len(sections_u) == 0: continue
            fadb.ins_usr(DB, u)
            for s in sections_u:
                d = dl_usr(Session, u, s, DB, sync, speed, force)
                if d in (0,1,2,3,5):
                    if s == 'e':
                        fadb.usr_rep(DB, u, 'E', 'e', 'FOLDERS')
                    elif s == 'E':
                        fadb.usr_rep(DB, u, 'e', 'E', 'FOLDERS')
                    else:
                        fadb.usr_up(DB, u, s, 'FOLDERS')
                elif d == 4:
                    fadb.usr_rep(DB, u, s, s+'!', 'FOLDERS')
                fadb.info_up(DB, 'USRN', fadb.table_n(DB, 'USERS'))
                fadb.info_up(DB, 'SUBN', fadb.table_n(DB, 'SUBMISSIONS'))
                if d == 5: return Session
        t = int(time.time()) - t
        fadb.info_up(DB, 'LASTDLT', t)

    return Session
