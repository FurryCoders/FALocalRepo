import requests
import os
import re
import sys
import bs4
import json
import glob
import FA_DLSUB as dlsub
section_full = {
    'g' : 'gallery',
    's' : 'scraps',
    'f' : 'favorites',
    'e' : 'extra (partial)',
    'E' : 'extra (full)'
    }

def make_session(cookies_file='FA.cookies'):
    Session = requests.Session()

    try:
        with open(cookies_file) as f: cookies = json.load(f)
    except FileNotFoundError as err:
        raise err

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

def dl_url_print(section, usr):
    url ='https://www.furaffinity.net/'
    if section in ('g', 's', 'f'):
        url += '{}/{}/'.format(section_full[section], usr)
    elif section == 'e':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" ) ! ( @lower {0} )&order-by=date&page='.format(usr)
    elif section == 'E':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" | "{0}" ) ! ( @lower {0} )&order-by=date&page='.format(usr)

    return url

def dl_usr(Session, user, section, DB, sync=False):

def sync(Session, DB, users='', sections=''):

try: Session = make_session()
except FileNotFoundError: exit(1)
usrs = []
for u in sys.argv[1:]:
    usrs.append(u)
