import requests
import os
import re
import sys
import bs4
import json
import glob
from FA_DLSUB import download_submission


def check_usr(FA, usr):
    user_r = FA.get('https://www.furaffinity.net/user/'+usr) 
    user_t = bs4.BeautifulSoup(user_r.text, 'lxml').title.string

    if user_t == 'System Error': return False
    elif user_t == 'Account disabled. -- Fur Affinity [dot] net': return False
    elif user_r.status_code == 404: return False

    return True

"""class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)"""

def set_data(folder, usr):
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

    return [url, glob_string, rule]

def dl_usr(FA, usr, folder, sync=False):
    url, glob_string, rule = set_data(folder, usr)

    page_i = 1
    while True:
        page_r = FA.get(url+str(page_i))
        page_r = page_r.text
        page = bs4.BeautifulSoup(page_r, 'lxml')
        page = page.find('section', id="gallery-gallery")

        if page.find('figure') is None:
            if page_i == 1: return 1
            else: return 0

        sub_i = 0
        for i in page.find_all('figure'):
            ID = re.sub('^[0-9]', '', i.get('id'))
            sub_i += 1
            print("%03d/%02d) %s - " % (page_i, sub_i, ID.zfill(10)), end='', flush=True)

            if len(glob.glob(usr+'/'+folder.lower()+'/'+glob_string+ID.zfill(10)+' - */info.txt')) == 1:
                cols = int(os.popen('tput cols').read()) - 34
                print("%.*s | Repository" % (cols, i.find_all('a')[1].string))
                if sync: return
                else: continue

            subB = download_submission(FA, ID, usr+"/"+folder.lower()+"/", rule, True)
            if subB: print(" | Downloaded")
            else: print(" | Error 41")

        page_i += 1


#sys.stdout = Unbuffered(sys.stdout)

FA = requests.Session()
with open('FA-cookies-JS.txt') as f: cookies = json.load(f)
for cookie in cookies: FA.cookies.set(cookie['name'], cookie['value'])

for usr in sys.argv[1:]:
    if check_usr(FA, usr): dl_usr(FA, usr, 'gallery')
