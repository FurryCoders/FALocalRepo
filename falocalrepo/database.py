from sqlite3 import Connection
from sqlite3 import connect as sqlite3_connect
from typing import List


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
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["USRN", "0"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["USRN", "0"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["SUBN", "0"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTUPDATE", "0"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTDOWNLOAD", "0"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTSTART", "0"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["COOKIES", "{}"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["USERNAME", ""], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["FILESLOCATION", "FA.files"], False)

    db.commit()
