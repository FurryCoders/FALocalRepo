from os.path import join as path_join
from sqlite3 import Connection
from sqlite3 import connect as sqlite3_connect
from typing import Iterator
from typing import List
from typing import Union

from .__version__ import __database_version__

# Entries guide - USERS
# v3.0        v3.1
# 0 USERNAME  USERNAME
# 1 FOLDERS   FOLDERS
# 2 GALLERY   GALLERY
# 3 SCRAPS    SCRAPS
# 4 FAVORITES FAVORITES
# 5 EXTRAS    MENTIONS

# Entries guide - SUBMISSIONS
# v3.1
# 0  ID
# 1  AUTHOR
# 2  TITLE
# 3  UDATE
# 4  DESCRIPTION
# 5  TAGS
# 6  CATEGORY
# 7  SPECIES
# 8  GENDER
# 9  RATING
# 10 FILELINK
# 11 FILEEXT
# 12 FILESAVED
# 13 LOCATION
# 14 SERVER


keys_submissions: List[str] = [
    "ID", "AUTHOR", "TITLE",
    "UDATE", "DESCRIPTION", "TAGS",
    "CATEGORY", "SPECIES", "GENDER",
    "RATING", "FILELINK", "FILEEXT",
    "FILESAVED"
]

keys_users: List[str] = [
    "USERNAME", "FOLDERS",
    "GALLERY", "SCRAPS",
    "FAVORITES", "MENTIONS"
]


def tiered_path(id_: Union[int, str], tiers: int = 5, depth: int = 2) -> str:
    assert isinstance(id_, int) or (isinstance(id_, str) and id_.isdigit())
    assert isinstance(tiers, int)
    assert isinstance(depth, int)

    id_str: str = str(id_).lstrip("0").zfill(tiers * depth)
    id_tiered: List[str] = []
    for n in range(0, tiers * depth, depth):
        id_tiered.append(id_str[n:n + depth])

    return path_join(*id_tiered)


def connect_database(db_name: str) -> Connection:
    return sqlite3_connect(db_name)


def insert(db: Connection, table: str, keys: List[str], values: List[Union[int, str]], replace: bool = True):
    db.execute(
        f"""INSERT OR {"REPLACE" if replace else "IGNORE"} INTO {table}
        ({",".join(keys)})
        VALUES ({",".join(["?"] * len(values))})""",
        values
    )


def select(db: Connection, table: str, select_fields: List[str], key: str, key_value: Union[int, str]
           ) -> Iterator[tuple]:
    return db.execute(
        f'''SELECT {",".join(select_fields)} FROM {table} WHERE {key} = ?''',
        (key_value,)
    )


def select_all(db: Connection, table: str, select_fields: List[str]) -> Iterator[tuple]:
    return db.execute(f'''SELECT {",".join(select_fields)} FROM {table}''')


def update(db: Connection, table: str, fields: List[str], values: List[Union[int, str]], key: str, key_value: str):
    assert len(fields) == len(values) and len(fields) > 0

    update_values: List[str] = [f"{u} = ?" for u in fields]

    db.execute(
        f"""UPDATE {table}
        SET {",".join(update_values)}
        WHERE {key} = ?""",
        (*values, key_value,)
    )


def delete(db: Connection, table: str, key: str, key_value: Union[int, str]):
    db.execute(f"""DELETE FROM {table} where {key} = ?""", (key_value,))


def count(db: Connection, table: str) -> int:
    return db.execute(f"SELECT COUNT(*) FROM {table}").fetchall()[0][0]


def vacuum(db: Connection):
    db.execute("VACUUM")


def check_errors(db: Connection, table: str) -> List[tuple]:
    if (table := table.upper()) == "SUBMISSIONS":
        id_errors: List[tuple] = select(db, table, ["*"], "ID", 0)
        author_errors: List[tuple] = select(db, table, ["*"], "AUTHOR", "")
        title_errors: List[tuple] = select(db, table, ["*"], "TITLE", "")
        date_errors: List[tuple] = select(db, table, ["*"], "UDATE", "")
        file_url_errors: List[tuple] = select(db, table, ["*"], "FILELINK", "")

        return list(set(id_errors + author_errors + title_errors + date_errors + file_url_errors))
    else:
        return []


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
        FILESAVED INT,
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
        MENTIONS TEXT,
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
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["USRN", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["SUBN", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTUPDATE", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTSTART", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["COOKIES", "{}"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["FILESFOLDER", "FA.files"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["VERSION", str(__database_version__)], False)

    db.commit()
