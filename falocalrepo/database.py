from sqlite3 import Connection
from sqlite3 import connect as sqlite3_connect
from typing import List
from typing import Optional


def connect_database(db_name: str) -> Connection:
    return sqlite3_connect(db_name)


def write(db: Connection, table: str, keys: List[str], values: List[str], replace: bool = True):
    db.execute(
        f"""INSERT OR {"REPLACE" if replace else "IGNORE"} INTO {table}
        ({",".join(keys)})
        VALUES ({",".join(["?"] * len(values))})""",
        values
    )


def read(db: Connection, table: str, select: List[str], key: str, key_value: str) -> List[tuple]:
    return db.execute(
        f'''SELECT ({",".join(select)}) FROM {table} WHERE {key} = ?''',
        (key_value,)
    ).fetchall()


def setting_write(db: Connection, key: str, value: str, replace: bool = True):
    write(db, "SETTINGS", ["SETTING", "SVALUE"], [key, value], replace)
    db.commit()


def setting_read(db: Connection, key: str) -> Optional[str]:
    setting = read(db, "SETTINGS", ["SVALUE"], "SETTING", key)

    return None if not setting else setting[0][0]


def make_database(db: Connection):
    # Create submissions table
    db.execute(
        """CREATE TABLE IF NOT EXISTS SUBMISSIONS
        (ID INT UNIQUE NOT NULL,
        AUTHOR TEXT NOT NULL,
        TITLE TEXT,
        UDATE DATE NOT NULL,
        DESCRIPTION TEXT,
        TAGS TEXT,
        CATEGORY TEXT,
        SPECIES TEXT,
        GENDER TEXT,
        RATING TEXT,
        FILE_LINK TEXT,
        FILE_NAME TEXT,
        PRIMARY KEY (ID ASC));"""
    )

    # Create users table
    db.execute(
        """CREATE TABLE IF NOT EXISTS USERS
        (USERNAME TEXT UNIQUE NOT NULL,
        USERFULL TEXT NOT NULL,
        FOLDERS TEXT NOT NULL,
        GALLERY TEXT,
        SCRAPS TEXT,
        FAVORITES TEXT,
        EXTRAS TEXT,
        PRIMARY KEY (USERNAME ASC));"""
    )

    # Create settings table
    db.execute(
        """CREATE TABLE IF NOT EXISTS SETTINGS
        (SETTING TEXT UNIQUE,
        SVALUE TEXT,
        PRIMARY KEY (SETTING ASC));"""
    )

    db.commit()

    # Add settings
    setting_write(db, "USRN", "0", replace=False)
    setting_write(db, "SUBN", "0", replace=False)
    setting_write(db, "LASTUPDATE", "0", replace=False)
    setting_write(db, "LASTDOWNLOAD", "0", replace=False)
    setting_write(db, "LASTSTART", "0", replace=False)
    setting_write(db, "COOKIES", "{}", replace=False)
    setting_write(db, "USERNAME", "", replace=False)
    setting_write(db, "FILESLOCATION", "FA.files", replace=False)
