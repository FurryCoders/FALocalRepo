import requests
import os
import re
import sys
import bs4
import json
import glob
from FA_DLSUB import download_submission

def make_session(cookies_file='FA.cookies'):
    Session = requests.Session()

    try:
        with open(cookies_file) as f: cookies = json.load(f)
        for cookie in cookies: Session.cookies.set(cookie['name'], cookie['value'])
        return Session
    except:
        raise Exception('No FA.cookies file')

def check_cookies(Session):
    check_r = Session.get('https://www.furaffinity.net/controls/settings/')
    check_p = bs4.BeautifulSoup(check_r.text, 'lxml')

    if check_p.find('img', 'loggedin_user_avatar') is None: return False

def check_usr(FA, usr):
    usr_r = FA.get('https://www.furaffinity.net/user/'+usr)
    usr_t = bs4.BeautifulSoup(usr_r.text, 'lxml').title.string

    if usr_t == 'System Error': return False
    elif usr_t == 'Account disabled. -- Fur Affinity [dot] net': return False
    elif usr_r.status_code == 404: return False

    return True

def check_id(FA, ID):
    id_r = FA.get('https://www.furaffinity.net/view/'+ID)
    id_t = bs4.BeautifulSoup(id_r.text, 'lxml').title.string

    if id_t == 'System Error': return False
    elif id_t == 'Account disabled. -- Fur Affinity [dot] net': return False
    elif id_r.status_code == 404: return False

def dl_usr_data(folder, usr):
    url ='https://www.furaffinity.net/'
    if folder == 'gallery':
        url += '{}/{}/'.format(folder, usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'dit'
    elif folder == 'scraps':
        url += '{}/{}/'.format(folder, usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'dit'
    elif folder == 'favorites':
        url += '{}/{}/'.format(folder, usr)
        glob_string = '* - '
        rule = 'ait'
    elif folder == 'extra':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" ) ! ( @lower {0} )&order-by=date&page='.format(usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'diat'
    elif folder == 'Extra':
        url += 'search/?q=( ":icon{0}:" | ":{0}icon:" | "{0}" ) ! ( @lower {0} )&order-by=date&page='.format(usr)
        glob_string = '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] - '
        rule = 'diat'

    glob_string = usr+'/'+folder.lower()+'/'+glob_string

    return [url, glob_string, rule]

def dl_usr(FA, usr, folder, sync=False):
    url, glob_string, rule = dl_usr_data(folder, usr)

    page_i = 1
    while True:
        page_r = FA.get(url+str(page_i))
        page_p = bs4.BeautifulSoup(page_r.text, 'lxml')
        page_p = page_p.find('section', id="gallery-gallery")

        if page_p.find('figure') is None:
            if page_i == 1: return 1
            else: return 0

        sub_i = 0
        for i in page_p.find_all('figure'):
            ID = re.sub('[^0-9]', '', i.get('id'))
            sub_i += 1
            print("%03d/%02d) %s - " % (page_i, sub_i, ID.zfill(10)), end='', flush=True)

            if len(glob.glob(glob_string+ID.zfill(10)+' - */info.txt')) == 1:
                cols = int(os.popen('tput cols').read()) - 34
                print("%.*s | Repository" % (cols, i.find_all('a')[1].string))
                if sync: return
                else: continue

            subB = download_submission(FA, ID, usr+"/"+folder.lower()+"/", rule, quiet=True)
            if subB: print(" | Downloaded")
            else: print(" | Error 41")

        page_i += 1

try: os.mkdir('FA Repo')
except: pass
os.chdir('FA Repo')
