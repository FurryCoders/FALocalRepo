from shutil import move
from typing import List

from faapi import FAAPI

from .database import Connection
from .database import setting_read
from .database import setting_write
from .settings import cookies_change
from .settings import cookies_load


def main_console(workdir: str, api: FAAPI, db: Connection, args: List[str]):
    if not args:
        return

    if args[0] == "read-cookies":
        cookie_a, cookie_b = cookies_load(db)
        print("cookie a:", cookie_a)
        print("cookie b:", cookie_b)
    elif args[0] == "change-cookies":
        if len(args) != 3:
            return
        cookie_a: str = args[1]
        cookie_b: str = args[2]
        cookies_change(db, cookie_a, cookie_b)
    elif args[0] == "read-files-folder":
        print("files folder:", setting_read(db, "FILESLOCATION"))
    elif args[0] == "change-files-folder":
        if len(args) != 2:
            return
        folder_old: str = setting_read(db, "FILESLOCATION")
        setting_write(db, "FILESLOCATION", args[1])
        print("Moving files to new location... ", end="", flush=True)
        move(folder_old, args[1])
        print("Done")
