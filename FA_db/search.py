import sqlite3
import re
import time
import os
import bs4
import PythonRead as readkeys
import FA_tools as fatl
from FA_dl import session

# def regexp(pattern, input):
#     return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search_web(Session, fields):
    Session = session(Session)
    if not Session:
        print("Couldn't establish connection, search aborted")
        return
    print()

    for k in fields:
        fields[k] = fields[k].strip()

    search_string = ''
    if fields['user']:
        search_string += f"@lower {fields['user']} "
    if fields['titl']:
        search_string += f"@title {fields['titl']} "
    if fields['tags']:
        search_string += f"@keywords {fields['tags']} "
    search_string = search_string.strip()

    search_url = f'https://www.furaffinity.net/search/?q={search_string}&order-by=date&order-direction=asc'
    page_i = 1
    re_id = re.compile('[^0-9]')
    str_cl = re.compile('[^\x00-\x7F]')
    n = 0

    print(f'{page_i:03d}', end='', flush=True)

    page = Session.get(f'{search_url}&page={page_i}')
    page = bs4.BeautifulSoup(page.text, 'lxml')
    page = page.find('section', id="gallery-search-results")

    while page and page.find('figure'):
        results = page.findAll('figure')

        for r in results:
            ratg = r.get('class')[0].lstrip('r-')
            if fields['ratg'] and fields['ratg'].lower() != ratg:
                continue
            s_id = re_id.sub('', r.get('id')).zfill(10)
            user = r.findAll('a')[2].string
            titl = r.findAll('a')[1].string

            n += 1

            print(f'\r{user[0:18]: <18} | {s_id}', end='', flush=True)
            if os.get_terminal_size()[0] > 33:
                print(f' | {str_cl.sub("",titl[0:os.get_terminal_size()[0]-33])}', end='')
            print()

        page_i += 1
        print(f'\r{page_i:03d}', end='', flush=True)

        page = Session.get(f'{search_url}&page={page_i}')
        page = bs4.BeautifulSoup(page.text, 'lxml')
        page = page.find('section', id="gallery-search-results")

    print('\r   \r', end='', flush=True)
    print('\n'*bool(n) + f'{n} results found')

def search(Session, DB, fields):
    # DB.create_function("REGEXP", 2, regexp)
    fields_o = {k: v for k,v in fields.items()}

    fields['user'] = fields['user'].strip()
    fields['sect'] = re.sub('[^gsfe]','', fields['sect'].lower())
    fields['titl'] = '%'+fields['titl']+'%'
    fields['tags'] = re.sub('( )+', ' ', fields['tags'].upper()).split(' ')
    fields['tags'] = sorted(fields['tags'], key=str.lower)
    fields['tags'] = '%'+'%'.join(fields['tags'])+'%'
    fields['catg'] = '%'+fields['catg'].upper()+'%'
    fields['spec'] = '%'+fields['spec'].upper()+'%'
    fields['gend'] = '%'+fields['gend'].upper()+'%'
    fields['ratg'] = '%'+fields['ratg'].upper()+'%'

    t1 = time.time()

    if fields['user'] and re.match('^[gs]+$', fields['sect']):
        subs = DB.execute('''SELECT * FROM submissions
            WHERE authorurl LIKE ? AND
            title LIKE ? AND
            UPPER(tags) LIKE ? AND
            UPPER(category) LIKE ? AND
            UPPER(species) LIKE ? AND
            UPPER(gender) LIKE ? AND
            UPPER(Rating) LIKE ?''', tuple(fields.values())[0:1]+tuple(fields.values())[2:]).fetchall()
    else:
        subs = DB.execute('''SELECT * FROM submissions
            WHERE title LIKE ? AND
            UPPER(tags) LIKE ? AND
            UPPER(category) LIKE ? AND
            UPPER(species) LIKE ? AND
            UPPER(gender) LIKE ? AND
            UPPER(Rating) LIKE ?''', tuple(fields.values())[2:]).fetchall()

    subs = {s[0]: s for s in subs}

    if fields['user']:
        fields['user'] = re.sub('[^a-z0-9\-. ]', '', fields['user'].lower())

        subs_u = DB.execute(f'SELECT gallery, scraps, favorites, extras FROM users WHERE name = "{fields["user"]}"')
        subs_u = subs_u.fetchall()
        if not len(subs_u):
            subs_u = [['','','','']]
        subs_u = [[int(si) for si in s.split(',') if si != ''] for s in subs_u[0]]

        subs_u[0] = [[i, 'g'] for i in subs_u[0]]
        subs_u[1] = [[i, 's'] for i in subs_u[1]]
        subs_u[2] = [[i, 'f'] for i in subs_u[2]]
        subs_u[3] = [[i, 'e'] for i in subs_u[3]]

        if fields['sect']:
            subs_t = []
            if 'g' in fields['sect']:
                subs_t += subs_u[0]
            if 's' in fields['sect']:
                subs_t += subs_u[1]
            if 'f' in fields['sect']:
                subs_t += subs_u[2]
            if 'e' in fields['sect']:
                subs_t += subs_u[3]
        else:
            subs_t = subs_u[0] + subs_u[1] + subs_u[2] + subs_u[3]

        subs = [subs.get(i[0]) + (i[1],) for i in subs_t if subs.get(i[0]) != None]
    else:
        subs = list(subs.values())

    subs.sort(key=lambda x: x[0])
    subs.sort(key=lambda x: x[2])

    t2 = time.time()

    str_cl = re.compile('[^\x00-\x7F]')
    for s in subs:
        if fields['user'] and s[1] != fields['user']:
            print(f'({s[-1]}) {s[1][0:14]: ^{14}} |', end='', flush=True)
        else:
            print(f'{s[1][0:18]: <18} |', end='', flush=True)
        print(f' {s[4]} {s[0]:0>10}', end='', flush=True)
        if os.get_terminal_size()[0] > 45:
            print(f' | {str_cl.sub("",s[3][0:os.get_terminal_size()[0]-45])}')
        else:
            print()

    print()
    print(f'{len(subs)} results found in {t2-t1:.3f} seconds')
    if not len(subs):
        print('No results found in the local database\nDo you want to search online (y/n)? ', end='', flush=True)
        c = ''
        while c not in ('y','n'):
            c = readkeys.getkey().lower()
        print(c)

        if c == 'y':
            print()
            search_web(Session, fields_o)

def main(Session, DB):
    fatl.header('Search')

    while True:
        fields = {}

        try:
            fatl.sigint_ublock()
            fields['user'] = readkeys.input('User: "', '"')
            if fields['user']:
                fields['sect'] = readkeys.input('Section: "', '"')
            else:
                fields['sect'] = ''
            fields['titl'] = readkeys.input('Title: "', '"')
            fields['tags'] = readkeys.input('Tags: "', '"')
            fields['catg'] = readkeys.input('Category: "', '"')
            fields['spec'] = readkeys.input('Species: "', '"')
            fields['gend'] = readkeys.input('Gender: "', '"')
            fields['ratg'] = readkeys.input('Rating: "', '"')
            options = readkeys.input('Options: ')
        except:
            return
        finally:
            fatl.sigint_clear()

        print()
        if all(v == '' for v in fields.values()):
            print('At least one field needs to be used')
            print()
            continue

        break

    try:
        fatl.sigint_ublock()

        if 'web' in options.lower():
            search_web(Session, fields)
        else:
            search(Session, DB, fields)

        print('\nPress any key to continue ', end='', flush=True)
        readkeys.getkey()
        print('\b \b'*26, end='')
    except:
        raise
    finally:
        fatl.sigint_clear()

    return Session
