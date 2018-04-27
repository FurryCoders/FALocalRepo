import sqlite3

# Entries guide - USERS
# 0 NAME
# 1 NAMEFULL
# 2 (1 v2.0) FOLDERS
# 3 (2 v2.0) GALLERY
# 4 (3 v2.0) SCRAPS
# 5 (4 v2.0) FAVORITES
# 6 (5 v2.0) EXTRAS

# Entries guide - SUBMISSIONS
# 0 ID          the submission id
# 1 AUTHOR      the author as written by the user (with underscores and capital letters)
# 2 AUTHORURL   the author for search and downloads (no underscores and lowercase)
# 3 TITLE       the title as posted with the submission
# 4 UDATE       upload date in YYYY-MM-DD format (no need for HH:MM as the id already orders submissions)
# 5 TAGS        tags sorted by alphanumeric order
# 6 CATEGORY    submission category
# 7 SPECIES     submission species
# 8 GENDER      submission gender
# 9 RATING      submission rating
# 10 (6 v1) FILELINK   link to submission file
# 11 (7 v1) FILENAME   the filename of the submission (0 if absent and 'submission' + the extension otherwise)
# 12 (8 v1) LOCATION   the location of the submission inside the files folder
# 13 (9 v1) SERVER     1 if the submission is available on FA, 0 if it was disabled, deleted, etc...

def usr_ins(db, user, user_full=''):
    if user_full.lower().replace('_','') != user:
        user_full = user
    exists = db.execute(f'SELECT EXISTS(SELECT name FROM users WHERE name = "{user}" LIMIT 1);')
    if exists.fetchall()[0][0]:
        return
    try:
        db.execute(f'''INSERT INTO USERS
            (NAME,NAMEFULL,FOLDERS,GALLERY,SCRAPS,FAVORITES,EXTRAS)
            VALUES ("{user}", "{user_full}", "", "", "", "", "")''')
    except sqlite3.IntegrityError:
        pass
    except:
        raise
    finally:
        db.commit()

def usr_rm(db, user, isempty=False):
    try:
        if isempty:
            db.execute(f'DELETE FROM users WHERE name = "{user}" AND folders = "" AND gallery = "" AND scraps = "" AND favorites = "" AND extras = ""')
        else:
            db.execute(f'DELETE FROM users WHERE name = "{user}"')
    except:
        pass
    finally:
        db.commit()

def usr_up(db, user, to_add, column):
    col = db.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()
    if not len(col):
        raise sqlite3.IntegrityError
    col = col[0][0].split(',')
    if to_add in col:
        return 1
    if col[0] == '':
        col = [to_add]
    else:
        col.append(to_add)
    col.sort(key=str.lower)
    col = ",".join(col)
    db.execute(f"UPDATE users SET {column} = '{col}' WHERE name = '{user}'")
    db.commit()

def usr_rep(db, user, find, replace, column):
    col = db.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()
    if not len(col):
        raise sqlite3.IntegrityError
    col = col[0][0].split(',')
    if replace in col:
        return 1
    elif col[0] == '':
        col = [replace]
    elif find not in col:
        col.append(replace)
    else:
        col = [e.replace(find, replace) for e in col]
    col.sort(key=str.lower)
    col = ",".join(col)
    db.execute(f"UPDATE users SET {column} = '{col}' WHERE name = '{user}'")
    db.commit()

def usr_src(db, user, find, column):
    col = db.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()[0]
    col = "".join(col).split(',')
    if find in col: return True
    else: return False

def usr_isempty(db, user):
    usr = db.execute(f"SELECT name FROM users WHERE name = '{user}' AND folders = '' AND gallery = '' AND scraps = '' AND favorites = '' AND extras = ''")
    usr = usr.fetchall()
    return bool(len(usr))

def sub_ins(db, infos):
    try:
        db.execute(f'''INSERT INTO SUBMISSIONS
            (ID,AUTHOR,AUTHORURL,TITLE,UDATE,DESCRIPTION,TAGS,CATEGORY,SPECIES,GENDER,RATING,FILELINK,FILENAME,LOCATION, SERVER)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', infos)
    except sqlite3.IntegrityError:
        pass
    except:
        raise
    finally:
        db.commit()

def sub_up(db, ID, new_value, column):
    if type(new_value) != list:
        new_value = [new_value]
    if type(column) != list:
        column = [column]
    if len(new_value) != len(column):
        return False

    cols = []
    for i in range(0, len(column)):
        col = db.execute(f"SELECT {column[i]} FROM submissions WHERE id = '{ID}'")
        cols.append(col.fetchall())
    if any(len(col) == 0 for col in cols):
        return False

    cols = [col[0][0] for col in cols]
    for i in range(0, len(new_value)):
        db.execute(f"UPDATE submissions SET {column[i]} = '{new_value[i]}' WHERE id = '{ID}'")
    db.commit()

    return True

def sub_read(db, ID, column):
    col = db.execute(f"SELECT {column} FROM submissions WHERE id = '{ID}'")
    col = col.fetchall()[0]
    return col[0]

def sub_search(db, terms):
    return db.execute('''SELECT author, udate, title FROM submissions
        WHERE id LIKE ? AND
        authorurl LIKE ? AND
        title LIKE ? AND
        tags REGEXP ?
        ORDER BY authorurl ASC, id ASC''', terms)

def sub_exists(db, ID):
    exists = db.execute(f'SELECT EXISTS(SELECT id FROM submissions WHERE id = "{ID}" LIMIT 1);')
    return exists.fetchall()[0][0]

def info_up(db, field, value):
    db.execute(f'UPDATE infos SET value = "{value}" WHERE field = "{field}"')
    db.commit()

def table_n(db, table):
    table_b = db.execute(f'SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "{table}");')
    table_b = table_b.fetchall()[0][0]

    if table_b:
        num = db.execute(f'SELECT * FROM {table}')
        return len(num.fetchall())

def mktable(db, table):
    if table == 'submissions':
        db.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
            (ID INT UNIQUE PRIMARY KEY NOT NULL,
            AUTHOR TEXT NOT NULL,
            AUTHORURL TEXT NOT NULL,
            TITLE TEXT,
            UDATE CHAR(10) NOT NULL,
            DESCRIPTION TEXT,
            TAGS TEXT,
            CATEGORY TEXT,
            SPECIES TEXT,
            GENDER TEXT,
            RATING TEXT,
            FILELINK TEXT,
            FILENAME TEXT,
            LOCATION TEXT NOT NULL,
            SERVER INT);''')
    elif table == 'users':
        db.execute('''CREATE TABLE IF NOT EXISTS USERS
            (NAME TEXT UNIQUE PRIMARY KEY NOT NULL,
            NAMEFULL TEXT NOT NULL,
            FOLDERS TEXT NOT NULL,
            GALLERY TEXT,
            SCRAPS TEXT,
            FAVORITES TEXT,
            EXTRAS TEXT);''')
    elif table == 'infos':
        infos = db.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "INFOS")')
        infos = infos.fetchall()[0][0]

        if not infos:
            db.execute('''CREATE TABLE INFOS
                (FIELD CHAR,
                VALUE CHAR);''')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("dbNAME", "")')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("VERSION", "2.3")')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("USRN", 0)')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("SUBN", 0)')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTUP", 0)')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTUPT", 0)')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTDL", 0)')
            db.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTDLT", 0)')
            db.commit()
            info_up(db, 'USRN', table_n(db, 'USERS'))
            info_up(db, 'SUBN', table_n(db, 'SUBMISSIONS'))
