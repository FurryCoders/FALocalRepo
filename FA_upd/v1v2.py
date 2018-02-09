import sqlite3
import sys
from FA_dl import dl_sub
from FA_tools import tiers
from readkeys import getkey

def dl_values(Session, ID):
    url = 'https://www.furaffinity.net/view/'+ID
    page = Session.get(url)
    page = bs4.BeautifulSoup(page.text, 'lxml')

    if page == None or page.find('meta', {"property":"og:title"}) == None:
        return False

    data = []

    extras = [str(e) for e in page.find('div', 'sidebar-section-no-bottom').find_all('div')]
    extras = [e.rstrip('</div>') for e in extras]
    extras = [re.sub('.*> ', '', e).replace('&gt;', '>') for e in extras]
    # [category, species, gender]

    rating = page.find('meta', {"name":"twitter:data2"})
    rating = rating.get('content').lower()

    data += extras
    data.append(rating)

    return data

def db_update_v1v2():
    print('Creating temporary database ... ', end='', flush=True)
    db_new = sqlite3.connect('FA.temp.db')
    db_new.close()
    print('Done')

    db_old = sqlite3.connect('FA.db')
    db_old.execute("ATTACH DATABASE 'FA.temp.db' AS db_new")

    print('Copying INFOS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.INFOS AS SELECT * FROM main.INFOS")
    DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("VERSION", "2.0")')
    db_old.commit()
    print('Done')

    print('Copying USERS data ... ', end='', flush=True)
    db_old.execute("CREATE TABLE IF NOT EXISTS db_new.USERS AS SELECT * FROM main.USERS")
    db_old.commit()
    print('Done')

    print('Finding all submissions ... ', end='', flush=True)
    subs_old = db_old.execute("SELECT * FROM submissions ORDER BY id ASC")
    subs_old = [[si for si in s] for s in subs_old.fetchall()]
    db_old.close()
    print('Done')

    db_new = sqlite3.connect('FA.temp.db')

    db_new.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
        (ID INT UNIQUE PRIMARY KEY NOT NULL,
        AUTHOR TEXT NOT NULL,
        AUTHORURL TEXT NOT NULL,
        TITLE TEXT,
        UDATE CHAR(10) NOT NULL,
        TAGS TEXT,
        CATEGORY TEXT,
        SPECIES TEXT,
        GENDER TEXT,
        RATING TEXT,
        FILELINK TEXT,
        FILENAME TEXT,
        LOCATION TEXT NOT NULL,
        SERVER INT);''')

    print('Editing submissions data to add new values ... ', end='', flush=True)
    subs_new = []
    for s in subs_old:
        s_new = []
        s_new.append(s[0])
        s_new.append(s[1])
        s_new.append(s[2])
        s_new.append(s[3])
        s_new.append(s[4])
        s_new.append(s[5])
        s_new.append('All > All')
        s_new.append('Unspecified / Any')
        s_new.append('Any')
        s_new.append('general')
        s_new.append(s[6])
        s_new.append(s[7])
        s_new.append(s[8])
        s_new.append(1)
        subs_new.append(s_new)
    print('Done')

    print('Creating download session:')
    Session = session()
    if not Session:
        dl = False
        print('Failed to create session')
        print('\nWithout connection to the forum the new fields will be saved with default values.')
        print('Do you want to continue? ', end='', flush=True)
        c = ''
        while c not in ('y','n'):
            c = getkey().lower()
        if c == 'n': sys.exit(0)

    if dl:
        subs_new_dl = subs_new
        subs_new = []
        N = len(subs_new_dl)
        Ni = 0
        print('Getting new values from FA ... ', end='', flush=True)
        for s in subs_new_dl:
            Ni += 1
            print(f'{Ni:0>{len(str(N))}}/{N}', end='', flush=True)
            values = dl_values(Session, s[0])
            if values != False:
                s[6] = values[0]
                s[7] = values[1]
                s[8] = values[2]
                s[9] = values[3]
                subs_new.append(s)
            print('\b \b'+'\b \b'*(len(str(N))*2), end='', flush=True)

    N = len(subs_new)
    Ni = 0
    print('Adding submissions to new database ... ', end='', flush=True)
    for s in subs_new:
        Ni += 1
        print(f'{Ni:0>{len(str(N))}}/{N}', end='', flush=True)
        try:
                db_new.execute(f'''INSERT INTO SUBMISSIONS
                (ID,AUTHOR,AUTHORURL,TITLE,UDATE,TAGS,CATEGORY,SPECIES,GENDER,RATING,FILELINK,FILENAME,LOCATION, SERVER)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', s)
        except sqlite3.IntegrityError:
                pass
        print('\b \b'+'\b \b'*(len(str(N))*2), end='', flush=True)
    db_new.commit()
    print('Done')
