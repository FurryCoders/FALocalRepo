import sqlite3
import re
import time
import os
import PythonRead as readkeys
import FA_tools as fatl

# def regexp(pattern, input):
#     return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, fields):
    # DB.create_function("REGEXP", 2, regexp)

    fields['titl'] = '%'+fields['titl']+'%'
    fields['tags'] = re.sub('( )+', ' ', fields['tags'].upper()).split(' ')
    fields['tags'] = sorted(fields['tags'], key=str.lower)
    fields['tags'] = '%'+'%'.join(fields['tags'])+'%'
    fields['catg'] = '%'+fields['catg'].upper()+'%'
    fields['spec'] = '%'+fields['spec'].upper()+'%'
    fields['gend'] = '%'+fields['gend'].upper()+'%'
    fields['ratg'] = '%'+fields['ratg'].upper()+'%'

    t1 = time.time()
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
            print(f'{s[1][0:18]: ^18} |', end='', flush=True)
        print(f' {s[4]} {s[0]:0>10}', end='', flush=True)
        if os.get_terminal_size()[0] > 45:
            print(f' | {str_cl.sub("",s[3][0:os.get_terminal_size()[0]-45])}')
        else:
            print()

    print()
    print(f'{len(subs)} results found in {t2-t1:.3f} seconds')
    print()
    print('Press any key to continue ', end='', flush=True)
    readkeys.getkey()
    print('\b \b'*26, end='')

def main(Session, DB):
    fatl.header('Search')

    while True:
        fields = {}

        try:
            fatl.sigint_ublock()
            fields['user'] = readkeys.input('User: "', '"').strip()
            if fields['user']:
                fields['sect'] = readkeys.input('Section: "', '"').lower()
                fields['sect'] = re.sub('[^gsfe]','', fields['sect'])
            else:
                fields['sect'] = ''
            fields['titl'] = readkeys.input('Title: "', '"')
            fields['tags'] = readkeys.input('Tags: "', '"')
            fields['catg'] = readkeys.input('Category: "', '"')
            fields['spec'] = readkeys.input('Species: "', '"')
            fields['gend'] = readkeys.input('Gender: "', '"')
            fields['ratg'] = readkeys.input('Rating: "', '"')
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
        search(DB, fields)
    except:
        pass
    finally:
        sigint_clear()

    return Session
