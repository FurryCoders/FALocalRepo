import sqlite3

def db_usr_up(DB, user, to_add, column):
    col = DB.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()[0]
    col = "".join(col).split(',')
    if to_add in col: return 1
    if col[0] == '':
        col = [to_add]
    else:
        col.append(to_add)
    col.sort()
    col = ",".join(col)
    DB.execute(f"UPDATE users SET {column} = '{col}' WHERE name = '{user}'")
    DB.commit()

def db_ins_usr(DB, user):
    try:
        DB.execute(f'''INSERT INTO USERS
            (NAME,FOLDERS,GALLERY,SCRAPS,FAVORITES,EXTRAS)
            VALUES ({user}, "", "", "", "", "")''')
        DB.commit()
    except sqlite3.IntegrityError:
        pass
    except:
        raise

def db_ins_sub(DB, infos):
    try:
        DB.execute(f'''INSERT INTO SUBMISSIONS
            (ID,AUTHOR,AUTHORURL,TITLE,UDATE,TAGS,FILE,LOCATION)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', infos)
        DB.commit()
    except sqlite3.IntegrityError:
        pass
    except:
        raise

def db_usr_rep(DB, user, find, replace, column):
    col = DB.execute(f"SELECT {column} FROM users WHERE name = '{user}'")
    col = col.fetchall()[0]
    col = "".join(col).split(',')
    col_new = [] ; rep = False
    for entry in col:
        if entry == find:
            entry = replace
            rep = True
        col_new.append(entry)
    if not rep: col_new.append(replace)
    col_new.sort()
    col_new = ",".join(col)
    DB.execute(f"UPDATE users SET {column} = '{col_new}' WHERE name = '{user}'")
    DB.commit()
