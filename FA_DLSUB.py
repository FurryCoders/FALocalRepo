import requests
import bs4
import re
import os
import glob
import time
import magic
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
filetypes = {
    'application/msword.vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
    'application/msword' : 'doc',
    'application/vnd.oasis.opendocument.text' : 'odt',
    'text/plain' : 'txt',
    'image/vnd.adobe.photoshop' : 'tif',
    'audio/x-wav' : 'wav',
    'application/x-shockwave-flash' : 'swf',
    'application/x-rar' : 'rar',
    'inode/x-empty': 'inode/x-empty'
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

def get_file(link, folder, speed=1):
    if os.path.isfile(folder+'/submission.temp'):
        os.remove(folder+'/submission.temp')

    try: sub = requests.get(link, stream=True)
    except: return False

    with open(folder+'/submission.temp', 'wb') as f:
        for chunk in sub.iter_content(chunk_size=1024):
            if chunk: f.write(chunk)
            if speed == 1: time.sleep(.01)

    if not os.path.isfile(folder+'/submission.temp'): return False

    mime = magic.from_file(folder+'/submission.temp', mime=True)
    mime = filetypes.get(mime, mime.split('/')[-1])

    if mime == 'inode/x-empty': os.remove(folder+'/submission.temp')
    else: os.rename(folder+'/submission.temp', folder+'/submission.'+mime)

    return os.path.isfile(folder+'/submission.'+mime)

def str_clean(string):
    return re.sub('[()%.:;![\]"&*/\\\]', '', string)

def set_dest(data, rule):
    folder = ''
    for i in range(0,len(rule)):
        if rule[i] == 'a': folder += data[0]
        elif rule[i] == 't': folder += str_clean(data[1])
        elif rule[i] == 'd': folder += data[2]
        elif rule[i] == 'i': folder += data[4].zfill(10)

        if i < len(rule)-1: folder += ' - '

    return folder


def dl_sub(Session, ID, folder, rule, quiet=False, check=False, speed=1):
    if check:
        if len(glob.glob(folder+'* - '+ID.zfill(10)+' - */info.txt')) == 1:
            return 1

    page = get_page(Session, ID)
    data = get_info(page) ; data.append(ID)
    link = get_link(page)
    desc = get_desc(page)

    if quiet:
        cols = os.get_terminal_size()[0]
        print("%.*s" % ((cols-34), data[1]), end='', flush=True)
    else:
        print("->Author: %s" % data[0])
        print("->Title: %s" % data[1])
        print("->Upload date: %s" % data[2])
        print("->Keywords: %s" % data[3])
        print("->ID: %s" % data[4])
        print("->File: %s" % link.split('/')[-1])

    folder += set_dest(data, rule)
    os.makedirs(folder, exist_ok=True)

    subf = get_file(link, folder, speed)

    with open(folder+'/description.html', 'w') as f:
        f.write(desc)

    with open(folder+'/info.txt', 'w') as f:
        f.write("Author: %s\n" % data[0])
        f.write("Title: %s\n" % data[1])
        f.write("Upload date: %s\n" % data[2])
        f.write("Keywords: %s\n" % data[3])
        f.write("ID: %s\n" % data[4])
        f.write("File: %s\n" % link)

    return subf
