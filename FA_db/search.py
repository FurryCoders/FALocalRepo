import sqlite3
import re
import time
import os
import bs4
import PythonRead as readkeys
import FA_tools as fatl
from FA_dl import session

def mkregexp(case):
    if case:
        def regexp(pattern, input):
            return bool(re.match(pattern, input))
    else:
        def regexp(pattern, input):
            return bool(re.match(pattern, input, flags=re.IGNORECASE))

    return regexp

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
        search_string += f"@lower {fields['user'].lower()} "
    if fields['titl']:
        search_string += f"@title {fields['titl']} "
    if fields['tags']:
        search_string += f"@keywords {fields['tags']} "
    if fields['desc']:
        search_string += f"@message {fields['desc']} "
    search_string = search_string.strip()

    search_url = f'https://www.furaffinity.net/search/?q={search_string}&order-by=date&order-direction=asc'
    page_i = 1
    re_id = re.compile('[^0-9]')
    str_cl = re.compile('[^\x00-\x7F]')
    n = 0

    print('USER               |     ID     | TITLE'[0:os.get_terminal_size()[0]])
    print(('-'*41)[0:os.get_terminal_size()[0]])

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

    return Session

def search(Session, db, fields, regex=False, case=False):
    match = ('LIKE', '%')
    if regex:
        regexp = mkregexp(case)
        db.create_function("REGEXP", 2, regexp)
        match = ('REGEXP', '(?:.)*')

    fields_o = {k: v for k,v in fields.items()}

    fields['user'] = fields['user'].strip().lower()
    fields['sect'] = re.sub('[^gsfe]','', fields['sect'].lower())
    fields['titl'] = match[1]+fields['titl']+match[1]
    fields['desc'] = match[1]+fields['desc']+match[1]
    fields['tags'] = re.sub('( )+', ' ', fields['tags'].upper()).split(' ')
    fields['tags'] = sorted(fields['tags'], key=str.lower)
    fields['tags'] = match[1]+match[1].join(fields['tags'])+match[1]
    fields['catg'] = match[1]+fields['catg'].upper()+match[1]
    fields['spec'] = match[1]+fields['spec'].upper()+match[1]
    fields['gend'] = match[1]+fields['gend'].upper()+match[1]
    fields['ratg'] = match[1]+fields['ratg'].upper()+match[1]

    t1 = time.time()

    if fields['user'] and re.match('^[gs]+$', fields['sect']):
        subs = db.execute(f'''SELECT author, udate, id, title FROM submissions
            WHERE authorurl {match[0]} ? AND
            title {match[0]} ? AND
            description {match[0]} ? AND
            UPPER(tags) {match[0]} ? AND
            UPPER(category) {match[0]} ? AND
            UPPER(species) {match[0]} ? AND
            UPPER(gender) {match[0]} ? AND
            UPPER(Rating) {match[0]} ?''', (match[1]+fields['user']+match[1],) + tuple(fields.values())[2:]).fetchall()
    else:
        subs = db.execute(f'''SELECT author, udate, id, title FROM submissions
            WHERE title {match[0]} ? AND
            description {match[0]} ? AND
            UPPER(tags) {match[0]} ? AND
            UPPER(category) {match[0]} ? AND
            UPPER(species) {match[0]} ? AND
            UPPER(gender) {match[0]} ? AND
            UPPER(Rating) {match[0]} ?''', tuple(fields.values())[2:]).fetchall()

    subs = {s[2]: s for s in subs}

    if fields['user']:
        if not regex:
            fields['user'] = re.sub('[^a-z0-9\-.]', '', fields['user'])

        users = db.execute(f'SELECT gallery, scraps, favorites, extras FROM users WHERE user {match[0]} ?', (match[1]+fields['user']+match[1],))
        users = users.fetchall()
        if not len(users):
            users = [('','','','')]
        subs_u = []

        for u in users:
            u = [[int(si) for si in s.split(',') if si != ''] for s in u]

            u[0] = [[i, 'g'] for i in u[0]]
            u[1] = [[i, 's'] for i in u[1]]
            u[2] = [[i, 'f'] for i in u[2]]
            u[3] = [[i, 'e'] for i in u[3]]

            if fields['sect']:
                if 'g' in fields['sect']:
                    subs_u += u[0]
                if 's' in fields['sect']:
                    subs_u += u[1]
                if 'f' in fields['sect']:
                    subs_u += u[2]
                if 'e' in fields['sect']:
                    subs_u += u[3]
            else:
                subs_u += u[0] + u[1] + u[2] + u[3]

        subs = [subs.get(i[0]) + (i[1],) for i in subs_u if subs.get(i[0]) != None]
    else:
        subs = list(subs.values())

    subs.sort(key=lambda x: x[0])
    subs.sort(key=lambda x: x[2])

    t2 = time.time()

    if fields['user']:
        print('(SECTION) USER  |    DATE        ID     | TITLE'[0:os.get_terminal_size()[0]])
    else:
        print('USER            |    DATE        ID     | TITLE'[0:os.get_terminal_size()[0]])
    print(('-'*49)[0:os.get_terminal_size()[0]])

    str_cl = re.compile('[^\x00-\x7F]')
    for s in subs:
        if fields['user']:
            print(f'({s[-1]}) {s[0][0:11]: ^{11}} |', end='', flush=True)
        else:
            print(f'{s[0][0:15]: <15} |', end='', flush=True)
        print(f' {s[1]} {s[2]:0>10}', end='', flush=True)
        if os.get_terminal_size()[0] > 42:
            print(f' | {str_cl.sub("",s[3][0:os.get_terminal_size()[0]-45])}')
        else:
            print()

    print('\n'*bool(len(subs)) + f'{len(subs)} results found in {t2-t1:.3f} seconds')
    if not len(subs):
        print('\nNo results found in the local database\nDo you want to search online (y/n)? ', end='', flush=True)
        c = ''
        while c not in ('y','n'):
            c = readkeys.getkey().lower()
        print(c)

        if c == 'y':
            print()
            Session = search_web(Session, fields_o)

def main(Session, db):
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
            fields['desc'] = readkeys.input('Description: "', '"')
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
        regex = False
        case = False
        if 'regex' in options.lower():
            regex = True
        if 'case' in options.lower():
            case = True

        fatl.sigint_ublock()

        if 'web' in options.lower():
            Session = search_web(Session, fields)
        else:
            Session = search(Session, db, fields, regex, case)

        print('\nPress any key to continue ', end='', flush=True)
        readkeys.getkey()
        print('\b \b'*26, end='')
    except:
        raise
    finally:
        fatl.sigint_clear()

    return Session
