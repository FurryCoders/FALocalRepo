import requests
import os
import re
import sys
import bs4
import json
import glob
import FA_DLSUB as dlsub

def make_session(cookies_file='FA.cookies'):
    Session = requests.Session()

    try:
        with open(cookies_file) as f: cookies = json.load(f)
    except FileNotFoundError as err:
        raise err

    for cookie in cookies: Session.cookies.set(cookie['name'], cookie['value'])

    return Session

def check_cookies(FA):
    check_r = FA.get('https://www.furaffinity.net/controls/settings/')
    check_p = bs4.BeautifulSoup(check_r.text, 'lxml')

    if check_p.find('img', 'loggedin_user_avatar') is None: return False

def check_page(FA, url):
    page_r = FA.get('https://www.furaffinity.net/'+url)
    page_t = bs4.BeautifulSoup(page_r.text, 'lxml').title.string

    if page_t == 'System Error': return False
    elif page_t == 'Account disabled. -- Fur Affinity [dot] net': return False
    elif page_r.status_code == 404: return False

    return true

def dl_usr_data(section, usr):
    url ='https://www.furaffinity.net/'
    if section == 'g':
        print('-> gallery')
        folder = 'gallery'
        url += '{}/{}/'.format(folder, usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'dit'
    elif section == 's':
        print('-> scraps')
        folder = 'scraps'
        url += '{}/{}/'.format(folder, usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'dit'
    elif section == 'f':
        print('-> favorites')
        folder = 'favorites'
        url += '{}/{}/'.format(folder, usr)
        glob_string = '* - '
        rule = 'ait'
    elif section == 'e':
        print('-> extra (partial)')
        folder = 'extra'
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" ) ! ( @lower {0} )&order-by=date&page='.format(usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'diat'
    elif section == 'E':
        print('-> extra (full)')
        folder = 'Extra'
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" | "{0}" ) ! ( @lower {0} )&order-by=date&page='.format(usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'diat'

    folder = usr+"/"+folder+"/"
    glob_string = usr+'/'+folder+'/'+glob_string

    return [url, glob_string, folder, rule]

def dl_usr(FA, usr, section, sync=False, speed=1):
    url, glob_string, folder, rule = dl_usr_data(section, usr)

    page_i = 1
    while True:
        page_r = FA.get(url+str(page_i))
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        page_p = page_p.find('section', id="gallery-gallery")

        if page_p.find('figure') is None:
            if page_i == 1:
                print("--->No submissions to download")
                return 1
            else: return 0

        sub_i = 0
        for i in page_p.find_all('figure'):
            ID = re.sub('[^0-9]', '', i.get('id'))
            sub_i += 1
            print("--->%03d/%02d) %s - " % (page_i, sub_i, ID.zfill(10)), end='', flush=True)

            if len(glob.glob(glob_string+ID.zfill(10)+' - */info.txt')) == 1:
                cols = int(os.popen('tput cols').read()) - 34
                print("%.*s | Repository" % (cols, i.find_all('a')[1].string))
                if sync: return
                else: continue

            subB = dlsub.dl_sub(FA, ID, folder, rule, quiet=True, speed=speed)
            if subB: print(" | Downloaded")
            else: print(" | Error 41")

        page_i += 1

def dl(FA, users, sections, options=''):
    sync = False ; speed = 1
    for o in options:
        if o == 'Y': sync = True
        if o == 'Q': speed = 2

    for usr in users:
        if not check_page(FA, 'user/'+usr): continue
        print('-> %s' % usr)
        for s in sections:
            dl_usr(FA, usr, s, sync, speed)


try: FA = make_session()
except FileNotFoundError: exit(1)
usrs = []
for u in sys.argv[1:]:
    usrs.append(u)

ords = 'gs'

try: os.mkdir('FA Repo')
except: pass
os.chdir('FA Repo')

dl(FA, usrs, ords, 'Q')
