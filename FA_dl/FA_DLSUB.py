import requests, bs4
import re
import os, sys
import time
import filetype
import codecs
from FA_db import sub_exists, sub_read, sub_ins

months = {
    'January' : '01',
    'February' : '02',
    'March' : '03',
    'April' : '04',
    'May' : '05',
    'June' : '06',
    'July' : '07',
    'August' : '08',
    'September' : '09',
    'October' : '10',
    'November' : '11',
    'December' : '12'
    }

def get_page(Session, ID):
    url = 'https://www.furaffinity.net/view/'+ID
    page = Session.get(url)
    page = bs4.BeautifulSoup(page.text, 'lxml')

    return page

def get_info(page):
    data = []

    author = page.find('div', 'submission-artist-container')
    author = author.find('h2').string
    data.append(author)

    title = page.find('h2', 'submission-title-header')
    title = title.string
    if title == None: title = ''
    data.append(title)

    date_r = page.find('meta', {"name":"twitter:data1"})
    date_r = date_r.get('content').replace(',', '')
    date_r = date_r.split(' ')
    date = [date_r[2], '', date_r[1].rjust(2, '0')]
    date[1] = months.get(date_r[0])
    data.append("-".join(date))

    keyw = []
    for k in page.find_all('span', 'tags'): keyw.append(k.string)
    keyw = keyw[0:int(len(keyw)/2)]
    keyw.sort(key = str.lower)
    data.append(" ".join(keyw))

    extras = [str(e) for e in page.find('div', 'sidebar-section-no-bottom').find_all('div')]
    extras = [e.rstrip('</div>') for e in extras]
    extras = [re.sub('.*> ', '', e).replace('&gt;', '>') for e in extras]
    # [category, species, gender]

    data += extras

    rating = page.find('meta', {"name":"twitter:data2"})
    rating = rating.get('content').lower()
    data.append(rating)

    return data

def get_link(page):
    link = page.find('a', 'button download-logged-in')
    link = "https:" + link.get('href')

    return link

def get_desc(page):
    desc = page.find('div', 'submission-description-container')
    desc = str(desc)
    desc = desc.split('</div>', 1)[-1]
    desc = desc.rsplit('</div>', 1)[0]
    desc = desc.strip()

    return desc

def get_file(link, folder, quiet=False, speed=1):
    if os.path.isfile(folder+'/submission.temp'):
        os.remove(folder+'/submission.temp')

    if not quiet: print('[Sizing Sub]', end='', flush=True)

    try:
        sub = requests.get(link, stream=True)
    except:
        if not quiet: print(('\b'*11)+'File Error', end='', flush=True)
        return False

    if not quiet: print('\b'+'\b \b'*10, end='', flush=True)

    size = requests.head(link)
    size = size.headers
    if "Content-Length" in size.keys():
        size = size["Content-Length"]
        size = int(size)
    else:
        if not quiet: print('Size Error', end='', flush=True)
        size = 0

    with open(folder+'/submission.temp', 'wb') as f:
        chunks = 0
        bar = 1
        for chunk in sub.iter_content(chunk_size=1024):
            if not quiet and size and (chunks*1024) >= bar*(size/10.0):
                print('=', end='', flush=True)
                bar += 1
            if chunk:
                f.write(chunk)
                chunks += 1
            if speed == 1:
                time.sleep(.01)
        if not quiet and size: print('='*(10-bar+1), end='', flush=True)

    if not quiet: print(('\b \b'*10)+'Saving Sub', end='', flush=True)

    if not os.path.isfile(folder+'/submission.temp'): return False

    ext = filetype.guess_extension(folder+'/submission.temp')
    if ext == None:
        ext = link.split('.')[-1]
        if ext == link.split('/')[-1]: ext = None
    elif ext == 'zip':
        ext = link.split('.')[-1]
        if ext == link.split('/')[-1]: ext = None
    if os.path.isfile(folder+'/submission.'+str(ext)):
        os.remove(folder+'/submission.'+str(ext))
    os.rename(folder+'/submission.temp', folder+'/submission.'+str(ext))

    if ext:
        return 'submission.'+str(ext)
    else:
        return False

def str_clean(string):
    if string == None or string == '':
        return ''
    return re.sub('[^\x00-\x7F]', '', string)


def dl_sub(Session, ID, folder, db, quiet=False, check=False, speed=1):
    if check and sub_exists(db, ID):
        if not quiet:
            if sys.platform in ('win32', 'cygwin'):
                cols = os.get_terminal_size()[0] - 44
            else:
                cols = os.get_terminal_size()[0] - 43
            if cols < 0: cols = 0
            title = str_clean(sub_read(db, ID, "title"))[0:cols]
            print('[Repository]'+(' '+title)*bool(title))
        return 2

    if not quiet: print('[Get Infos ]', end='', flush=True)

    page = get_page(Session, ID)
    if page == None:
        print('\b'*11+'Page Error')
        return 3
    data = get_info(page)
    link = get_link(page)
    desc = get_desc(page)

    if not quiet:
        if sys.platform in ('win32', 'cygwin'):
            cols = os.get_terminal_size()[0] - 44
        else:
            cols = os.get_terminal_size()[0] - 43
        if cols < 0: cols = 0
        title = str_clean(data[1])[0:cols]
        print((' '+title+('\b'*(len(title)+bool(cols-len(title)))))*bool(title), end='\b'*12, flush=True)
        if sys.platform in ('win32', 'cygwin') and cols and cols == len(title):
            print('\b', end='', flush=True)

    os.makedirs(folder, exist_ok=True)

    subf = get_file(link, folder, quiet, speed)

    if not quiet: print(('\b'*10)+'Saving DB ', end='', flush=True)

    with codecs.open(folder+'/description.html', encoding='utf-8', mode='w') as f:
        f.write(desc)

    with open(folder+'/info.txt', 'w') as f:
        f.write(f'Author: {data[0]}\n')
        f.write(f'Title: {data[1]}\n')
        f.write(f'Upload date: {data[2]}\n')
        f.write(f'Keywords: {data[3]}\n')
        f.write(f'ID: {ID}\n')
        f.write(f'File: {link}\n')

    sub_info = (
        ID,                                 # ID
        data[0],                            # authorurl
        data[0].lower().replace('_', ''),   # author
        data[1],                            # title
        data[2],                            # udate
        desc,                               # description
        data[3],                            # tags
        data[4],                            # category
        data[5],                            # species
        data[6],                            # gender
        data[7],                            # rating
        link,                               # filelink
        subf,                               # filename
        folder.split('/',1)[-1],            # location
        1,                                  # server
    )
    sub_ins(db, sub_info)

    if subf == False:
        if not quiet: print(('\b'*10)+'File Error')
        return 1
    else:
        if not quiet: print(('\b'*10)+'Downloaded')
        return 0
