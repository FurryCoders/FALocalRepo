from os.path import join as path_join
from sqlite3 import Connection
from sqlite3 import connect as sqlite3_connect
from typing import List
from typing import Union

from .__version__ import __version__

# Entries guide - USERS
# v2.6      v3.0
# USER      USERNAME
# USERFULL  FOLDERS
# FOLDERS   GALLERY
# GALLERY   SCRAPS
# SCRAPS    FAVORITES
# FAVORITES EXTRAS
# EXTRAS

# Entries guide - SUBMISSIONS
# v2.6              v3.0
# 0   ID            ID
# 1   AUTHOR        AUTHOR
# 2   AUTHORURL     TITLE
# 3   TITLE         UDATE
# 4   UDATE         DESCRIPTION
# 5   DESCRIPTION   TAGS
# 6   TAGS          CATEGORY
# 7   CATEGORY      SPECIES
# 8   SPECIES       GENDER
# 9   GENDER        RATING
# 10  RATING        FILELINK
# 11  FILELINK      FILEEXT
# 12  FILENAME
# 13  LOCATION
# 14  SERVER


keys_submissions: List[str] = [
    "ID", "AUTHOR", "TITLE",
    "UDATE", "DESCRIPTION", "TAGS",
    "CATEGORY", "SPECIES", "GENDER",
    "RATING", "FILELINK", "FILEEXT",
]

keys_users: List[str] = [
    "USERNAME", "FOLDERS",
    "GALLERY", "SCRAPS",
    "FAVORITES", "EXTRAS"
]


def tiered_path(id_: Union[int, str], tiers: int = 5, depth: int = 2) -> str:
    assert isinstance(id_, int) or (isinstance(id_, str) and id_.isdigit())
    assert isinstance(tiers, int)
    assert isinstance(depth, int)

    id_str: str = str(id_).strip("0").zfill(tiers * depth)
    id_tiered: List[str] = []
    for n in range(0, tiers * depth, depth):
        id_tiered.append(id_str[n:n + depth])

    return path_join(*id_tiered)


def connect_database(db_name: str) -> Connection:
    return sqlite3_connect(db_name)


def write(db: Connection, table: str, keys: List[str], values: List[Union[int, str]], replace: bool = True):
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
        FILELINK TEXT,
        FILEEXT TEXT,
        PRIMARY KEY (ID ASC));"""
    )

    # Create users table
    db.execute(
        """CREATE TABLE IF NOT EXISTS USERS
        (USERNAME TEXT UNIQUE NOT NULL,
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
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["FILESFOLDER", "FA.files"], False)
    write(db, "SETTINGS", ["SETTING", "SVALUE"], ["VERSION", str(__version__)], False)

    db.commit()
