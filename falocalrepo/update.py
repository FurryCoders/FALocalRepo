from glob import glob
from os import makedirs
from os.path import basename
from os.path import isdir
from os.path import join as path_join
from shutil import copy
from shutil import move
from shutil import rmtree
from sqlite3 import OperationalError
from typing import List
from typing import Optional

from .__version__ import __database_version__
from .database import Connection
from .database import connect_database
from .database import count
from .database import insert
from .database import make_database
from .database import select
from .database import select_all
from .database import tiered_path
from .database import update
from .settings import setting_read
from .settings import setting_write


def get_version(db: Connection) -> str:
    try:
        # Database version 3.0.0 and above
        return setting_read(db, "VERSION")
    except OperationalError:
        # Database version 2.7.0
        return next(select(db, "INFOS", ["VALUE"], "FIELD", "VERSION"))[0]


def compare_versions(a: str, b: str) -> int:
    a_split = list(map(int, a.split("-", 1)[0].split(".")))
    b_split = list(map(int, b.split("-", 1)[0].split(".")))
    a_split.extend([0] * (3 - len(a_split)))
    b_split.extend([0] * (3 - len(b_split)))

    for a_, b_ in zip(a_split, b_split):
        if a_ > b_:
            return 1
        elif a_ < b_:
            return -1
    return 0


def make_database_3(db: Connection):
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
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["USRN", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["SUBN", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTUPDATE", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["LASTSTART", "0"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["COOKIES", "{}"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["FILESFOLDER", "FA.files"], False)
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["VERSION", "3.0.0"], False)

    db.commit()


def make_database_3_1(db: Connection):
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
    insert(db, "SETTINGS", ["SETTING", "SVALUE"], ["VERSION", "3.1.0"], False)

    db.commit()


def update_2_7_to_3(db: Connection) -> Connection:
    print("Updating 2.7.0 to 3.0.0")
    db_new: Optional[Connection] = None

    try:
        db_new = connect_database("FA_new.db")
        make_database_3(db_new)

        # Transfer common submissions and users data
        print("Transfer common submissions and users data")
        db.execute("ATTACH DATABASE 'FA_new.db' AS db_new")
        db.execute(
            """INSERT OR IGNORE INTO
            db_new.SUBMISSIONS(ID, AUTHOR, UDATE, TITLE, DESCRIPTION, TAGS, CATEGORY, SPECIES, GENDER, RATING, FILELINK)
            SELECT ID, AUTHOR, UDATE, TITLE, DESCRIPTION, TAGS, CATEGORY, SPECIES, GENDER, RATING, FILELINK
            FROM SUBMISSIONS"""
        )
        db.execute(
            """INSERT OR IGNORE INTO
            db_new.USERS(USERNAME, FOLDERS, GALLERY, SCRAPS, FAVORITES, EXTRAS)
            SELECT USER, FOLDERS, GALLERY, SCRAPS, FAVORITES, EXTRAS
            FROM USERS"""
        )

        db.commit()
        db_new.commit()

        # Update users folders
        print("Update users folders")
        user: str
        folders: str
        user_n: int = 0
        for user, folders in select_all(db_new, "USERS", ["USERNAME", "FOLDERS"]):
            user_n += 1
            print(user_n, end="\r", flush=True)
            folders_new: List[str] = []
            for folder in folders.split(","):
                folder_new = ""
                folder_disabled = folder.endswith("!")
                if (folder := folder.strip("!")) == "g":
                    folder_new = "gallery"
                elif folder == "s":
                    folder_new = "scraps"
                elif folder == "f":
                    folder_new = "favorites"
                elif folder == "e":
                    folder_new = "extras"
                elif folder == "E":
                    folder_new = "Extras"
                folders_new.append(folder_new + ("!" if folder_disabled else ""))
            update(db_new, "USERS", ["FOLDERS"], [",".join(folders_new)], "USERNAME", user)
            db_new.commit() if user_n % 1000 == 0 else None
        db_new.commit()
        print()

        # Update submissions FILEEXT and FILESAVED and move to new location
        print("Update submissions FILEEXT and FILESAVED and move to new location")
        sub_n: int = 0
        sub_not_found: List[int] = []
        for id_, location in select_all(db, "SUBMISSIONS", ["ID", "LOCATION"]):
            sub_n += 1
            print(sub_n, end="\r", flush=True)
            if isdir(folder_old := path_join("FA.files", location.strip("/"))):
                fileglob = glob(path_join(folder_old, "submission*"))
                fileext = ""
                if filename := fileglob[0] if fileglob else "":
                    makedirs((folder_new := path_join("FA.files_new", tiered_path(id_))), exist_ok=True)
                    copy(filename, path_join(folder_new, (filename := basename(filename))))
                    fileext = filename.split(".")[-1] if "." in filename else ""
                else:
                    sub_not_found.append(id_)
                update(db_new, "SUBMISSIONS", ["FILEEXT", "FILESAVED"], [fileext, bool(filename)], "ID", id_)
                rmtree(folder_old)
            elif isdir(path_join("FA.files_new", tiered_path(id_))):
                # if this block is reached, original folder was removed and database entry updated
                continue
            else:
                sub_not_found.append(id_)
                update(db_new, "SUBMISSIONS", ["FILEEXT", "FILESAVED"], ["", False], "ID", id_)
            db_new.commit() if sub_n % 10000 == 0 else None
        db_new.commit()
        print()
        if sub_not_found:
            print(f"{len(sub_not_found)} submissions not found in FA.files\n" +
                  "Writing ID's to FA_update_2_7_to_3.txt")
            with open("FA_update_2_7_to_3.txt", "w") as f:
                for i, sub in enumerate(sorted(sub_not_found)):
                    print(i, end="\r", flush=True)
                    f.write(str(sub) + "\n")

        # Replace older files folder with new
        print("Replace older files folder with new")
        if isdir("FA.files"):
            if not sub_not_found:
                rmtree("FA.files")
            else:
                print("Saving older FA.files to FA.files_old")
                move("FA.files", "FA.files_old")
        if isdir("FA.files_new"):
            move("FA.files_new", "FA.files")

        # Update counters for new database
        setting_write(db_new, "SUBN", str(count(db_new, "SUBMISSIONS")))
        setting_write(db_new, "USRN", str(count(db_new, "USERS")))

        # Close databases and replace old database
        print("Close databases and replace old database")
        db.commit()
        db.close()
        db_new.commit()
        db_new.close()
        move("FA.db", "FA_2_7.db")
        move("FA_new.db", "FA.db")
    except (BaseException, Exception) as err:
        print("Database update interrupted!")
        db.commit()
        db.close()
        if db_new is not None:
            db_new.commit()
            db_new.close()
        raise err

    return connect_database("FA.db")


def update_3_to_3_1(db: Connection) -> Connection:
    print("Updating 3.0.0 to 3.1.0")
    db_new: Optional[Connection] = None

    try:
        db_new = connect_database("FA_new.db")
        make_database_3_1(db_new)

        # Transfer common submissions and users data
        print("Transfer common submissions and users data")
        db.execute("ATTACH DATABASE 'FA_new.db' AS db_new")
        db.execute(
            """INSERT OR IGNORE INTO db_new.SUBMISSIONS
            SELECT * FROM SUBMISSIONS"""
        )
        db.execute(
            """INSERT OR IGNORE INTO db_new.USERS
            SELECT * FROM USERS"""
        )
        db.execute(
            """INSERT OR REPLACE INTO db_new.SETTINGS
            SELECT * FROM SETTINGS"""
        )
        db.execute("UPDATE db_new.SETTINGS SET SVALUE = '3.1.0' WHERE SETTING = 'VERSION'")

        db.commit()
        db_new.commit()

        # Update users folders
        print("Update user folders")
        db_new.execute("UPDATE USERS SET FOLDERS = replace(FOLDERS, 'extras', 'mentions')")
        db_new.execute("UPDATE USERS SET FOLDERS = replace(FOLDERS, 'Extras', 'mentions_all')")

        # Close databases and replace old database
        print("Close databases and replace old database")
        db.commit()
        db.close()
        db_new.commit()
        db_new.close()
        move("FA.db", "FA_3.db")
        move("FA_new.db", "FA.db")
    except (BaseException, Exception) as err:
        print("Database update interrupted!")
        db.commit()
        db.close()
        if db_new is not None:
            db_new.commit()
            db_new.close()
        raise err

    return connect_database("FA.db")


def update_3_1_to_3_2(db: Connection) -> Connection:
    print("Updating 3.1.0 to 3.2.0")
    db_new: Optional[Connection] = None

    try:
        db_new = connect_database("FA_new.db")
        make_database(db_new)

        # Transfer common submissions and users data
        print("Transfer common submissions and users data")
        db.execute("ATTACH DATABASE 'FA_new.db' AS db_new")
        db.execute(
            """INSERT OR IGNORE INTO db_new.SUBMISSIONS
            SELECT * FROM SUBMISSIONS"""
        )
        db.execute(
            """INSERT OR IGNORE INTO db_new.USERS(USERNAME, FOLDERS, GALLERY, SCRAPS, FAVORITES, MENTIONS)
        SELECT USERNAME, FOLDERS, GALLERY, SCRAPS, FAVORITES, MENTIONS FROM USERS"""
        )
        db.execute(
            """INSERT OR REPLACE INTO db_new.SETTINGS
            SELECT * FROM SETTINGS"""
        )
        db.execute("UPDATE db_new.SETTINGS SET SVALUE = '3.2.0' WHERE SETTING = 'VERSION'")
        db.execute("UPDATE db_new.USERS SET JOURNALS = ''")

        db.commit()
        db_new.commit()

        # Close databases and replace old database
        print("Close databases and replace old database")
        db.commit()
        db.close()
        db_new.commit()
        db_new.close()
        move("FA.db", "FA_3.db")
        move("FA_new.db", "FA.db")
    except (BaseException, Exception) as err:
        print("Database update interrupted!")
        db.commit()
        db.close()
        if db_new is not None:
            db_new.commit()
            db_new.close()
        raise err

    return connect_database("FA.db")


def update_database(db: Connection) -> Connection:
    if not (db_version := get_version(db)):
        raise Exception("Cannot read version from database.")
    elif (v := compare_versions(db_version, __database_version__)) == 0:
        return db
    elif v > 0:
        raise Exception("Database version is newer than program.")
    elif compare_versions(db_version, "2.7.0") == 0:
        db = update_2_7_to_3(db)
        db = update_3_to_3_1(db)
        db = update_3_1_to_3_2(db)
    elif compare_versions(db_version, "3.0.0") == 0:
        db = update_3_to_3_1(db)
        db = update_3_1_to_3_2(db)
    elif compare_versions(db_version, "3.1.0") == 0:
        db = update_3_1_to_3_2(db)
    elif compare_versions(db_version, "2.7.0") < 0:
        raise Exception("Update does not support versions lower than 2.11.2")

    return db
