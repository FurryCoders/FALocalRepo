import requests, json, bs4
import os, sys
import sqlite3
import FA_DLSUB as dlsub

section_full = {
    'g' : 'gallery',
    's' : 'scraps',
    'f' : 'favorites',
    'e' : 'extra (partial)',
    'E' : 'extra (full)'
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

    if check_p.find('img', 'loggedin_user_avatar') is None: return False

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

def dl_usr(Session, user, section, DB, sync=False, speed=1):
    url = dl_url(section, user)
    print(f'--> {section_full[section]}')

    page_i = 1
    while True:
        page_r = Session.get(url+str(page_i))
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        if section in ('e', 'E'):
            page_p = page_p.find('section', id="gallery-search-results")
        else:
            page_p = page_p.find('section', id="gallery-gallery")

        if page_p.find('figure') is None:
            if page_i == 1:
                print("--->No submissions to download")
                return 1
            else:
                return 0

        sub_i = 0
        for sub in page_p.findAll('figure'):
            sub_i += 1
            ID = rsub.get('id')[4:]
            print(f'--->{page_i:03d}/{sub_i:02d}) {ID:0>10} - ', end='', flush=True)
            folder = f'__files/{tiers(ID)}/{ID:0>10}'

            if os.path.isfile(folder+'/info.txt'):
                cols = os.get_terminal_size()[0]
                print("%.*s | Repository" % ((cols-34), sub.find_all('a')[1].string))
                if sync: return
                else: continue

            sub_ret = dlsub.dl_sub(Session, ID, folder, DB, True, False, speed)
            if sub_ret: print(" | Downloaded")
            else: print(" | Error 41")

        page_i += 1

def sync(Session, DB, users='', sections=''):

try: Session = make_session()
except FileNotFoundError: exit(1)
usrs = []
for u in sys.argv[1:]:
    usrs.append(u)

fadb = sqlite3.connect('FA.db')
fadb.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
    (ID INT UNIQUE PRIMARY KEY NOT NULL,
    AUTHOR TEXT NOT NULL,
    AUTHORURL TEXT NOT NULL,
    TITLE TEXT,
    UDATE CHAR(10) NOT NULL,
    TAGS TEXT,
    FILE TEXT,
    LOCATION TEXT NOT NULL);''')
fadb.execute('''CREATE TABLE IF NOT EXISTS USERS
    (NAME TEXT UNIQUE PRIMARY KEY NOT NULL,
    FOLDERS CHAR(4) NOT NULL,
    GALLERY TEXT,
    SCRAPS TEXT,
    FAVORITES TEXT,
    EXTRAS TEXT);''')
