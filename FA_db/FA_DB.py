import sqlite3

# Entries guide
# 0 ID
# 1 AUTHOR
# 2 AUTHORURL
# 3 TITLE
# 4 UDATE
# 5 TAGS
# 6 CATEGORY
# 7 SPECIES
# 8 GENDER
# 9 RATING
# 10 FILELINK
# 11 FILENAME
# 12 LOCATION
# 13 SERVER

def ins_usr(DB, user):
    try:
        DB.execute(f'''INSERT INTO USERS
            (NAME,FOLDERS,GALLERY,SCRAPS,FAVORITES,EXTRAS)
            VALUES ("{user}", "", "", "", "", "")''')
    except sqlite3.IntegrityError:
        pass
    except:
        raise
    finally:
        DB.commit()

def ins_sub(DB, infos):
    try:
        DB.execute(f'''INSERT INTO SUBMISSIONS
            (ID,AUTHOR,AUTHORURL,TITLE,UDATE,TAGS,CATEGORY,SPECIES,GENDER,RATING,FILELINK,FILENAME,LOCATION, SERVER)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', infos)
    except sqlite3.IntegrityError:
        pass
    except:
        raise
    finally:
        DB.commit()

def usr_up(DB, user, to_add, column):
    col = DB.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()[0]
    col = "".join(col).split(',')
    if to_add in col: return 1
    if col[0] == '':
        col = [to_add]
    else:
        col.append(to_add)
    col.sort(key=str.lower)
    col = ",".join(col)
    DB.execute(f"UPDATE users SET {column} = '{col}' WHERE name = '{user}'")
    DB.commit()

def usr_rep(DB, user, find, replace, column):
    col = DB.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()[0]
    col = "".join(col).split(',')
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
    DB.execute(f"UPDATE users SET {column} = '{col}' WHERE name = '{user}'")
    DB.commit()

def usr_src(DB, user, find, column):
    col = DB.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()[0]
    col = "".join(col).split(',')
    if find in col: return True
    else: return False

def sub_read(DB, ID, column):
    col = DB.execute(f"SELECT {column} FROM submissions WHERE id = '{ID}'")
    col = col.fetchall()[0]
    return col[0]

def sub_search(DB, terms):
    return DB.execute('''SELECT author, udate, title FROM submissions
        WHERE id LIKE ? AND
        authorurl LIKE ? AND
        title LIKE ? AND
        tags REGEXP ?
        ORDER BY authorurl ASC, id ASC''', terms)

def sub_exists(DB, ID):
    exists = DB.execute(f'SELECT EXISTS(SELECT id FROM submissions WHERE id = "{ID}" LIMIT 1);')
    return exists.fetchall()[0][0]

def info_up(DB, field, value):
    DB.execute(f'UPDATE infos SET value = "{value}" WHERE field = "{field}"')
    DB.commit()

def table_n(DB, table):
    table_b = DB.execute(f'SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "{table}");')
    table_b = table_b.fetchall()[0][0]

    if table_b:
        num = DB.execute(f'SELECT * FROM {table}')
        return len(num.fetchall())

def mktable(DB, table):
    if table == 'submissions':
        DB.execute('''CREATE TABLE IF NOT EXISTS SUBMISSIONS
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
    elif table == 'users':
        DB.execute('''CREATE TABLE IF NOT EXISTS USERS
            (NAME TEXT UNIQUE PRIMARY KEY NOT NULL,
            FOLDERS CHAR(4) NOT NULL,
            GALLERY TEXT,
            SCRAPS TEXT,
            FAVORITES TEXT,
            EXTRAS TEXT);''')
    elif table == 'infos':
        infos = DB.execute('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = "table" AND name = "INFOS")')
        infos = infos.fetchall()[0][0]

        if not infos:
            DB.execute('''CREATE TABLE INFOS
                (FIELD CHAR,
                VALUE CHAR);''')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("DBNAME", "")')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("USRN", 0)')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("SUBN", 0)')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTUP", 0)')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTUPT", 0)')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTDL", 0)')
            DB.execute('INSERT INTO INFOS (FIELD, VALUE) VALUES ("LASTDLT", 0)')
            DB.commit()
            info_up(DB, 'USRN', table_n(DB, 'USERS'))
            info_up(DB, 'SUBN', table_n(DB, 'SUBMISSIONS'))
