from datetime import datetime
from os.path import isfile
from typing import Dict
from typing import List
from typing import Optional

from faapi import FAAPI

from .__doc__ import help_message
from .__version__ import __database_version__
from .__version__ import __version__
from .commands import files_folder_move
from .commands import journal_make
from .commands import journals_print
from .commands import journals_search
from .commands import submission_make
from .commands import submissions_download
from .commands import submissions_print
from .commands import submissions_search
from .database import Connection
from .database import check_errors
from .database import connect_database
from .database import count
from .database import delete
from .database import make_database
from .database import vacuum
from .download import cookies_load
from .download import journal_save
from .download import submission_save
from .download import user_clean_name
from .download import users_download
from .download import users_update
from .settings import cookies_read
from .settings import cookies_write
from .settings import setting_read
from .settings import setting_write
from .update import update_database


class CommandError(Exception):
    pass


def config(db: Connection, args: List[str]):
    if not args:
        cookie_a, cookie_b = cookies_read(db)
        folder: str = setting_read(db, "FILESFOLDER")
        print("cookie a:", cookie_a)
        print("cookie b:", cookie_b)
        print("folder  :", folder)
    elif args[0] == "cookies":
        if not args[1:]:
            cookie_a, cookie_b = cookies_read(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif len(args[1:]) == 2 and args[1] and args[2]:
            cookies_write(db, args[1], args[2])
        else:
            raise CommandError("Malformed command: cookies needs two arguments")
    elif args[0] == "files-folder":
        if not args[1:]:
            print("files folder:", setting_read(db, "FILESFOLDER"))
        elif len(args[1:]) == 1 and args[1]:
            files_folder_move(db, setting_read(db, "FILESFOLDER"), args[1])
        else:
            raise CommandError("Malformed command: files-folder needs one argument")
    else:
        raise CommandError(f"Unknown config command {args[0]}")


def download(db: Connection, args: List[str]):
    api: FAAPI = FAAPI()
    cookies_load(api, *cookies_read(db))

    if not args:
        raise CommandError("Malformed command: download needs a command")
    elif args[0] == "update":
        users: Optional[List[str]] = None
        folders: Optional[List[str]] = None
        if args[1:] and args[1] != "--":
            users_tmp: List[str] = list(filter(bool, map(user_clean_name, args[1].split(","))))
            users = sorted(set(users_tmp), key=users_tmp.index)
        if args[2:] and args[2] != "--":
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[2].split(","))))
            folders = sorted(set(folders_tmp), key=folders_tmp.index)
        users_update(api, db, users, folders)
    elif args[0] == "users":
        if len(args[1:]) == 2 and args[1] and args[2]:
            users_tmp: List[str] = list(filter(bool, map(user_clean_name, args[1].split(","))))
            users: List[str] = sorted(set(users_tmp), key=users_tmp.index)
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[2].split(","))))
            folders: List[str] = sorted(set(folders_tmp), key=folders_tmp.index)
            users_download(api, db, users, folders)
        else:
            raise CommandError("Malformed command: users needs two arguments")
    elif args[0] == "submissions":
        if not args[1:]:
            raise CommandError("Malformed command: submissions needs at least one argument")
        sub_ids_tmp: List[str] = list(filter(str.isdigit, args[1:]))
        sub_ids: List[str] = sorted(set(sub_ids_tmp), key=sub_ids_tmp.index)
        submissions_download(api, db, sub_ids)
    elif args[0] == "journals":
        if not args[1:]:
            raise CommandError("Malformed command: journals needs at least one argument")
        journal_ids_tmp: List[str] = list(filter(str.isdigit, args[1:]))
        journal_ids: List[str] = sorted(set(journal_ids_tmp), key=journal_ids_tmp.index)
        submissions_download(api, db, journal_ids)
    else:
        raise CommandError(f"Unknown download command {args[0]}")


def database(db: Connection, args: List[str]):
    if not args:
        sub_n: int = int(setting_read(db, "SUBN"))
        usr_n: int = int(setting_read(db, "USRN"))
        last_update: float = float(setting_read(db, "LASTUPDATE"))
        version: str = setting_read(db, "VERSION")
        print("Submissions:", sub_n)
        print("Users      :", usr_n)
        print("Last update:", str(datetime.fromtimestamp(last_update)) if last_update else 0)
        print("Version    :", version)
    elif args[0] == "search-submissions":
        search_params: Dict[str, List[str]] = {}
        for param, value in map(lambda p: p.split("=", 1), args[1:]):
            param = param.strip().lower()
            search_params[param] = search_params.get(param, []) + [value]
        results: List[tuple] = submissions_search(db, **search_params)
        submissions_print(results, sort=True)
        print(f"Found {len(results)} results")
    elif args[0] == "search-journals":
        search_params: Dict[str, List[str]] = {}
        for param, value in map(lambda p: p.split("=", 1), args[1:]):
            param = param.strip().lower()
            search_params[param] = search_params.get(param, []) + [value]
        results: List[tuple] = journals_search(db, **search_params)
        journals_print(results, sort=True)
        print(f"Found {len(results)} results")
    elif args[0] == "add-submission":
        make_params: Dict[str, str] = {(p := arg.split("="))[0].lower(): p[1].strip() for arg in args[1:]}
        make_params["id_"] = make_params.get("id", "")
        if "id" in make_params:
            del make_params["id"]
        submission_save(db, *submission_make(**make_params))
    elif args[0] == "add-journal":
        make_params: Dict[str, str] = {(p := arg.split("="))[0].lower(): p[1].strip() for arg in args[1:]}
        make_params["id_"] = make_params.get("id", "")
        if "id" in make_params:
            del make_params["id"]
        journal_save(db, journal_make(**make_params))
    elif args[0] == "remove-users":
        for user in map(user_clean_name, args[1:]):
            print("Deleting", user)
            delete(db, "USERS", "USERNAME", user)
            db.commit()
    elif args[0] == "remove-submissions":
        for sub in args[1:]:
            print("Deleting", sub)
            delete(db, "SUBMISSIONS", "ID", int(sub))
            db.commit()
    elif args[0] == "remove-journals":
        for sub in args[1:]:
            print("Deleting", sub)
            delete(db, "JOURNALS", "ID", int(sub))
            db.commit()
    elif args[0] == "check-errors":
        print("Checking submissions table for errors... ", end="", flush=True)
        results: List[tuple] = check_errors(db, "SUBMISSIONS")
        print("Done")
        if results:
            submissions_print(results)
    elif args[0] == "clean":
        vacuum(db)


def main_console(args: List[str]):
    prog: str
    comm: str

    prog, *args = list(filter(bool, args))
    comm = args[0] if args else ""
    args = args[1:]

    if comm in ("-h", "--help"):
        print(help_message(prog))
        return
    elif comm in ("-v", "--version"):
        print(__version__)
        return
    elif comm in ("-d", "--database"):
        print(__database_version__)
        return
    elif comm.startswith("-"):
        raise CommandError(f"Unknown option {comm}")
    elif (not comm and not args) or comm == "help":
        print(help_message(prog, args))
        return

    db: Optional[Connection] = None

    try:
        # Initialise and prepare database
        if isfile("FA.db"):
            db = update_database(connect_database("FA.db"))
        else:
            db = connect_database("FA.db")
            make_database(db)

        setting_write(db, "LASTSTART", str(datetime.now().timestamp()))

        if comm == "init":
            return
        elif comm == "config":
            config(db, args)
        elif comm == "download":
            download(db, args)
        elif comm == "database":
            database(db, args)
        else:
            raise CommandError(f"Unknown {comm} command.")
    finally:
        # Close database and update totals
        if db is not None:
            setting_write(db, "USRN", str(count(db, "USERS")))
            setting_write(db, "SUBN", str(count(db, "SUBMISSIONS")))
            setting_write(db, "JRNN", str(count(db, "JOURNALS")))
            db.commit()
            db.close()
