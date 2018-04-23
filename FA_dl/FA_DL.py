import requests, cfscrape, json, bs4
import os, sys, time
import re
import sqlite3
import PythonRead as readkeys
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

def session_make(cookies_file='FA.cookies.json'):
    Session = cfscrape.create_scraper()

    for name in ('FA.cookies'):
        if os.path.isfile(name) and not os.path.isfile(cookies_file):
            os.rename(name, cookies_file)
            break

    try:
        with open(cookies_file) as f:
            cookies = json.load(f)
    except FileNotFoundError:
        raise
    except:
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
            print('Failed - Missing Cookies File')
            return False
        except:
            print('Failed - Unknown Error')
            return False


        print('Checking cookies & bypassing cloudflare ... ', end='', flush=True)
        if check_cookies(Session):
            print('Done')
        else:
            print('Failed')
            cookies_error()
            return False

    return Session

def check_page(Session, url):
    page_r = Session.get('https://www.furaffinity.net/'+url)
    page_t = bs4.BeautifulSoup(page_r.text, 'lxml').title.string

    if page_t == 'System Error': return False
    elif page_t == 'Account disabled. -- Fur Affinity [dot] net': return False
    elif page_r.status_code == 404: return False

    return page_t


def dl_page(Session, user, section, DB, page_i, page_p, sync=False, speed=1, force=0, quiet=False):
    sub_i = 0
    for sub in page_p.findAll('figure'):
        if sigint_check(): return 5

        sub_i += 1
        ID = sub.get('id')[4:]
        print(f'{user[0:5]: ^5} {page_i:0>3}/{sub_i:0>2} {section} | {ID:0>10} | ', end='', flush=True)
        folder = f'FA.files/{tiers(ID)}/{ID:0>10}'

        if fadb.usr_src(DB, user, ID.zfill(10), section_db[section]):
            cols = os.get_terminal_size()[0] - 44
            if cols < 0: cols = 0
            titl = str_clean(sub.find_all('a')[1].string)
            if quiet and not force:
                print('\r'+' '*30+'\r', end='', flush=True)
            else:
                print(f'{titl[0:cols]} -> Repository')
            if sync:
                if force > 0 and page_i <= force: continue
                if force == -1: continue
                if sub_i+page_i == 2: return 3
                else: return 2
            continue

        if sigint_check(): return 5

        s_ret = dl_sub(Session, ID, folder, DB, False, True, speed)
        if s_ret == 0:
            print("\b"*5+" -> Downloaded")
        elif s_ret == 1:
            print("\b"*5+" -> File Error")
        elif s_ret == 2:
            print("\b"*5+" -> Repository")
        elif s_ret == 3:
            print("\b"*5+" -> Page Error")

        if s_ret != 3:
            fadb.usr_up(DB, user, ID.zfill(10), section_db[section])

        if sigint_check(): return 5

    return 0

def dl_gs(Session, user, section, DB, sync=False, speed=1, force=0, quiet=False):
    url = 'https://www.furaffinity.net/'
    url += f'{section_full[section]}/{user}/'

    page_i = 0
    while True:
        if sigint_check(): return 5

        page_i += 1
        page_r = Session.get(url+str(page_i))
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        page_p = page_p.find('section', id="gallery-gallery")

        if page_p == None:
            if page_i == 1:
                print(f"{user[0:12]: ^12} {section} | Section disabled for user")
                return 4
            else:
                return 0

        if page_p.find('figure') is None:
            if page_i == 1:
                if not quiet:
                    print(f"{user[0:5]: ^5} 001/01 {section} | No submissions to download")
                return 1
            else:
                return 0

        if sigint_check(): return 5

        page_ret = dl_page(Session, user, section, DB, page_i, page_p, sync, speed, force, quiet)

        if page_ret != 0: return page_ret

        if sigint_check(): return 5

def dl_e(Session, user, section, DB, sync=False, speed=1, force=0, quiet=False):
    url = 'https://www.furaffinity.net/'
    if section == 'e':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" ) ! ( @lower {0} )&order-by=date'.format(user)
    elif section == 'E':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" | "{0}" ) ! ( @lower {0} )&order-by=date'.format(user)

    page_i = 0
    while True:
        if sigint_check(): return 5

        page_i += 1
        page_r = Session.get(f'{url}&page={page_i}')
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        page_p = page_p.find('section', id="gallery-search-results")

        if page_p == None:
            if page_i == 1:
                return 1
            else:
                return 0

        if page_p.find('figure') is None:
            if page_i == 1:
                if not quiet:
                    print(f"{user[0:5]: ^5} 001/01 {section} | No submissions to download")
                return 1
            else:
                return 0

        if sigint_check(): return 5

        page_ret = dl_page(Session, user, section, DB, page_i, page_p, sync, speed, force, quiet)

        if page_ret != 0: return page_ret

        if sigint_check(): return 5

def dl_f(Session, user, section, DB, sync=False, speed=1, force=0, quiet=False):
    url = f'https://www.furaffinity.net/favorites/{user}'

    page_i = 0
    url_i = ''
    while True:
        if sigint_check(): return 5

        page_i += 1
        page_r = Session.get(url+url_i)
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        page_next = page_p.find('a', {"class": "button mobile-button right"})
        page_p = page_p.find('section', id="gallery-favorites")

        if page_p == None:
            if page_i == 1:
                print(f"{user[0:12]: ^12} {section} | Section disabled for user")
                return 4
            else:
                return 0

        if page_p.find('figure') is None:
            if page_i == 1:
                if not quiet:
                    print(f"{user[0:5]: ^5} 001/01 {section} | No submissions to download")
                return 1
            else:
                return 0

        if sigint_check(): return 5

        page_ret = dl_page(Session, user, section, DB, page_i, page_p, sync, speed, force, quiet)

        if page_ret != 0: return page_ret

        if sigint_check(): return 5

        if page_next:
            page_next = page_next['href']
            page_next = page_next.split(user)[-1]
            page_i += 1
        else:
            return 0

def dl_usr(Session, user, section, DB, sync=False, speed=1, force=0, quiet=False):
    print(f'{user[0:12]: ^12} {section}\r', end='', flush=True)
    if section in ('g', 's'):
        dl_ret = dl_gs(Session, user, section, DB, sync, speed, force, quiet)
    elif section in ('e', 'E'):
        dl_ret = dl_e(Session, user, section, DB, sync, speed, force, quiet)
    elif section in ('f'):
        dl_ret = dl_f(Session, user, section, DB, sync, speed, force, quiet)

    if dl_ret not in (1, 4):
        if section == 'e':
            fadb.usr_rep(DB, user, 'E', 'e', 'FOLDERS')
        elif section == 'E':
            fadb.usr_rep(DB, user, 'e', 'E', 'FOLDERS')
        else:
            fadb.usr_up(DB, user, section, 'FOLDERS')

    return dl_ret


def update(Session, DB, users=[], sections=[], speed=2, force=0):
    if sigint_check(): return

    print('Update')
    print('USR PAGE SECT. |     ID     | TITLE -> RESULT')
    print('-'*47)

    users_db = DB.execute("SELECT name, folders FROM users ORDER BY name ASC")
    t = int(time.time())
    fadb.info_up(DB, 'LASTUP', t)
    fadb.info_up(DB, 'LASTUPT', 0)
    flag_download = False

    for u in users_db:
        if sigint_check(): break
        flag_download_u = False

        if users and u[0] not in users:
            continue

        for s in u[1].split(','):
            dl_ret = 0
            if sigint_check():
                dl_ret = 5
                break
            if len(sections) and s not in sections:
                continue
            if s[-1] == '!' and s[0] not in sections:
                continue

            print(f'{u[0][0:12]: ^12} {s}\r', end='', flush=True)

            dl_ret = dl_usr(Session, u[0], s, DB, True, speed, force, quiet=True)
            if dl_ret == 3:
                print('\b \b'*os.get_terminal_size()[0], end='', flush=True)
            if dl_ret in (0,2,4):
                flag_download_u = True
            if dl_ret == 4:
                print(f'{section_full[s]} DISABLED')
                fadb.usr_rep(DB, u[0], s, s+'!', 'FOLDERS')
            if dl_ret == 5 or sigint_check():
                dl_ret = 5
                break

        if sigint_check(): break
        if dl_ret == 5:
            break

        if flag_download_u:
            flag_download = True

    if not flag_download:
        print("No new submissions were downloaded")

    t = int(time.time()) - t
    fadb.info_up(DB, 'LASTUPT', t)

def download(Session, DB, users, sections, sync, speed, force):
    if sigint_check(): return

    usr_sec = [[u, "".join(sections)] for u in users]
    print('Checking users:')
    i = -1
    while True:
        if sigint_check(): return
        i += 1
        if i == len(usr_sec): break
        print(f'  {usr_sec[i][0]} ... ', end='', flush=True)

        page_check = check_page(Session, f'user/{usr_sec[i][0]}')
        if page_check:
            print('Found')
            usr_full = page_check.lstrip('Userpage of ').rstrip(' -- Fur Affinity [dot] net').strip()
        else:
            print('Not found')
            usr_sec[i][1] = re.sub('[^eE]', '', usr_sec[i][1])
            usr_full = usr_sec[i][0]

        if len(usr_sec[i][1]) == 0:
            usr_sec = usr_sec[0:i] + usr_sec[i+1:]
            i -= 1
            continue

        fadb.usr_ins(DB, usr_sec[i][0], usr_full)

    if sigint_check(): return

    print()

    if len(usr_sec) == 0:
        print('Nothing to download')
        return
    print('Download')
    print('USR PAGE SECT. |     ID     | TITLE -> RESULT')

    t = int(time.time())
    fadb.info_up(DB, 'LASTDL', t)
    fadb.info_up(DB, 'LASTDLT', 0)

    for usr in usr_sec:
        print('-'*47)
        for i in range(0, len(usr[1])):
            sec = usr[1][i]
            dl_ret = dl_usr(Session, usr[0], sec, DB, sync, speed, force)
            if dl_ret in (0,1,2,3,5):
                if sec == 'e':
                    fadb.usr_rep(DB, usr[0], 'E', 'e', 'FOLDERS')
                elif sec == 'E':
                    fadb.usr_rep(DB, usr[0], 'e', 'E', 'FOLDERS')
                else:
                    fadb.usr_up(DB, usr[0], sec, 'FOLDERS')
            elif dl_ret == 4:
                fadb.usr_rep(DB, usr[0], sec, sec+'!', 'FOLDERS')
            if dl_ret == 5:
                break
            if i < len(usr[1])-1:
                print('-'*29)
        if fadb.usr_isempty(DB, usr[0]):
            fadb.usr_rm(DB, usr[0])
            print(f'{usr[0][0:14]: ^14} | No downloads, user deleted')
        if dl_ret == 5:
            break

    t = int(time.time()) - t
    fadb.info_up(DB, 'LASTDLT', t)

def download_main(Session, DB):
    while True:
        try:
            users = readkeys.input('Insert username: ').lower()
            sections = readkeys.input('Insert sections: ')
            options = readkeys.input('Insert options: ').lower()
        except:
            return

        users = re.sub('([^a-zA-Z0-9\-., ])', '', users)
        users = re.sub('( )+', ',', users.strip())
        users = sorted(users.split(','))
        users = list(set([u for u in users if u != '']))

        sections = re.sub('[^gsfeE]', '', sections)
        sections = list(set(sections))
        sections = [s for s in ('g','s','f','e','E') if s in sections]

        speed = 1 ; upd = False
        sync = False ; force = 0
        quit = False
        if 'quick' in options: speed = 2
        if 'slow' in options: speed = 0
        if 'update' in options: upd = True
        if 'sync' in options: sync = True
        if 'all' in options: force = -1
        if re.search('force[0-9]+', options):
            force = re.search('force[0-9]+', options).group(0)
            force = re.sub('[^0-9]', '', force)
            force = int(force)
        if 'quit' in options: quit = True
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

    if sigint_check(): return Session

    if upd:
        update(Session, DB, users, sections, speed, force)
    else:
        download(Session, DB, users, sections, sync, speed, force)
    fadb.info_up(DB, 'USRN', fadb.table_n(DB, 'USERS'))
    fadb.info_up(DB, 'SUBN', fadb.table_n(DB, 'SUBMISSIONS'))

    if quit: sys.exit(0)
    return Session
