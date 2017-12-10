import requests, json, bs4
import os, sys, signal
import sqlite3
import FA_DLSUB as dlsub
import FA_DB as fadb

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

def tiers(ID, t1=10000000, t2=1000000, t3=1000):
    ID = int(ID)
    tier1 = ID//t1
    tier2 = (ID-(t1*tier1))//t2
    tier3 = ((ID-(t1*tier1))-(t2*tier2))//t3

    return f'{tier1}/{tier2}/{tier3:03d}'

def make_session(cookies_file='FA.cookies'):
    Session = requests.Session()

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
            if page_i == 1: return 4
            else: return 0

        if page_p.find('figure') is None:
            if page_i == 1:
                print("--->No submissions to download")
                return 1
            else:
                return 0

        sub_i = 0
        for sub in page_p.findAll('figure'):
            sub_i += 1
            ID = sub.get('id')[4:]
            print(f'--->{page_i:03d}/{sub_i:02d}) {ID:0>10} - ', end='', flush=True)
            folder = f'FA.files/{tiers(ID)}/{ID:0>10}'

            if fadb.usr_src(DB, user, ID.zfill(10), section_db[section]):
                cols = os.get_terminal_size()[0]
                titl = dlsub.str_clean(sub.find_all('a')[1].string)
                print(f'{titl[0:cols-38]} | Repository')
                if force == 1 and page_i <= 2: continue
                if force == 2: continue
                if sync and sub_i > 1: return 2
                elif sync and sub_i+page_i == 2: return 3
                else: continue

            s_ret = dlsub.dl_sub(Session, ID, folder, DB, True, True, speed)
            if s_ret == 0:
                print(" | Downloaded")
                fadb.usr_up(DB, user, ID.zfill(10), section_db[section])
            elif s_ret == 1:
                print(" | File Error")
                fadb.usr_up(DB, user, ID.zfill(10), section_db[section])
            elif s_ret == 2:
                print(" | Repository")
                fadb.usr_up(DB, user, ID.zfill(10), section_db[section])
            elif s_ret == 3:
                print(" | Page Error")
            if signal.SIGINT in signal.sigpending(): return 0

        page_i += 1

def update(Session, DB, users=[], sections=[], force=0, speed=2):
    users_db = DB.execute("SELECT name, folders FROM users ORDER BY name ASC")
    download = False
    for u in users_db:
        if len(users) != 0 and u[0] not in users: continue
        download_u = False
        print(f'->{u[0]}')
        for s in u[1].split(','):
            if len(sections) != 0 and s not in sections: continue
            if s[-1] == '!': continue
            try:
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
            except KeyboardInterrupt:
                return
        if not download_u:
            if force not in (1,2): print('\033[1A\033[2K', end='', flush=True)
        else: download = True
    if not download: print("Nothing new to download")
