from os.path import join as path_join, isdir
from shutil import move
from typing import List

from .database import Connection
from .settings import cookies_change
from .settings import cookies_load
from .settings import setting_read
from .settings import setting_write


def config(workdir: str, db: Connection, args: List[str]):
    if args[0] == "get":
        if args[1] == "cookies":
            cookie_a, cookie_b = cookies_load(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif args[1] == "files-folder":
            print("files folder:", setting_read(db, "FILESLOCATION"))
        else:
            raise Exception(f"Unknown setting {args[1]}")
    elif args[0] == "set":
        if args[1] == "cookies":
            cookie_a: str = args[2]
            cookie_b: str = args[3]
            cookies_change(db, cookie_a, cookie_b)
        elif args[1] == "files-folder":
            folder_old: str = setting_read(db, "FILESLOCATION")
            setting_write(db, "FILESLOCATION", args[1])
            if isdir(path_join(folder_old)):
                print("Moving files to new location... ", end="", flush=True)
                move(path_join(workdir, folder_old), path_join(workdir, args[1]))
                print("Done")
        else:
            raise Exception(f"Unknown setting {args[1]}")
    else:
        raise Exception(f"Unknown {args[0]} command for config.")


def main_console(workdir: str, db: Connection, args: List[str]):
    if not args:
        return

    if args[0] == "config":
        config(workdir, db, args[1:])
    else:
        raise Exception(f"Unknown {args[0]} command.")
