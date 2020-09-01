from datetime import datetime
from os.path import isfile
from re import match
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

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


def parameters_multi(args: List[str]) -> Dict[str, List[str]]:
    params: Dict[str, List[str]] = {}
    for param, value in map(lambda p: p.split("=", 1), args):
        param = param.strip().lower()
        params[param] = params.get(param, []) + [value]

    return params


def parameters(args: List[str]) -> Dict[str, str]:
    return {p: v for p, v in map(lambda p: p.split("=", 1), args)}


def parse_args(args: List[str]) -> Tuple[Dict[str, str], List[str]]:
    opts: List[str] = []
    vals: List[str] = []

    for i, arg in enumerate(args):
        if match(r"\w+=\w+", arg):
            opts.append(arg)
        elif arg == "--":
            vals.extend(args[i + 1:])
            break
        else:
            vals.extend(args[i:])
            break

    return parameters(opts), vals


def config(db: Connection, args: List[str]):
    comm: str = args[0] if args else ""
    opts, args = parse_args(args[1:])

    if not comm:
        cookie_a, cookie_b = cookies_read(db)
        folder: str = setting_read(db, "FILESFOLDER")
        print("cookie a:", cookie_a)
        print("cookie b:", cookie_b)
        print("folder  :", folder)
    elif comm == "cookies":
        if not args:
            cookie_a, cookie_b = cookies_read(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif len(args) == 2 and args[0] and args[1]:
            cookies_write(db, args[0], args[1])
        else:
            raise CommandError("Malformed command: cookies needs two arguments")
    elif comm == "files-folder":
        if not args:
            print("files folder:", setting_read(db, "FILESFOLDER"))
        elif len(args) == 1 and args[0]:
            files_folder_move(db, setting_read(db, "FILESFOLDER"), args[0])
        else:
            raise CommandError("Malformed command: files-folder needs one argument")
    else:
        raise CommandError(f"Unknown config command {comm}")


def download(db: Connection, args: List[str]):
    comm: str = args[0] if args else ""
    opts, args = parse_args(args[1:])

    if not comm:
        raise CommandError("Malformed command: download needs a command")

    api: FAAPI = FAAPI()
    cookies_load(api, *cookies_read(db))

    if not api.connection_status:
        raise ConnectionError("FAAPI cannot connect to FA")
    elif comm == "update":
        users: Optional[List[str]] = None
        folders: Optional[List[str]] = None
        if args and args[0] != "@":
            users_tmp: List[str] = list(filter(bool, map(user_clean_name, args[0].split(","))))
            users = sorted(set(users_tmp), key=users_tmp.index)
        if args[1:] and args[1] != "@":
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
            folders = sorted(set(folders_tmp), key=folders_tmp.index)
        users_update(api, db, users, folders, int(opts.get("stop", 1)))
    elif comm == "users":
        if len(args) == 2 and args[0] and args[1]:
            users_tmp: List[str] = list(filter(bool, map(user_clean_name, args[0].split(","))))
            users: List[str] = sorted(set(users_tmp), key=users_tmp.index)
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
            folders: List[str] = sorted(set(folders_tmp), key=folders_tmp.index)
            users_download(api, db, users, folders)
        else:
            raise CommandError("Malformed command: users needs two arguments")
    elif comm == "submissions":
        if not args:
            raise CommandError("Malformed command: submissions needs at least one argument")
        sub_ids_tmp: List[str] = list(filter(str.isdigit, args))
        sub_ids: List[str] = sorted(set(sub_ids_tmp), key=sub_ids_tmp.index)
        submissions_download(api, db, sub_ids)
    elif comm == "journals":
        if not args:
            raise CommandError("Malformed command: journals needs at least one argument")
        journal_ids_tmp: List[str] = list(filter(str.isdigit, args))
        journal_ids: List[str] = sorted(set(journal_ids_tmp), key=journal_ids_tmp.index)
        submissions_download(api, db, journal_ids)
    else:
        raise CommandError(f"Unknown download command {comm}")


def database(db: Connection, args: List[str]):
    comm: str = args[0] if args else ""
    opts, args = parse_args(args[1:])

    if not comm:
        sub_n: int = int(setting_read(db, "SUBN"))
        usr_n: int = int(setting_read(db, "USRN"))
        last_update: float = float(setting_read(db, "LASTUPDATE"))
        version: str = setting_read(db, "VERSION")
        print("Submissions:", sub_n)
        print("Users      :", usr_n)
        print("Last update:", str(datetime.fromtimestamp(last_update)) if last_update else 0)
        print("Version    :", version)
    elif comm == "search-submissions":
        results: List[tuple] = submissions_search(db, **parameters_multi(args))
        submissions_print(results, sort=True)
        print(f"Found {len(results)} results")
    elif comm == "search-journals":
        results: List[tuple] = journals_search(db, **parameters_multi(args))
        journals_print(results, sort=True)
        print(f"Found {len(results)} results")
    elif comm == "add-submission":
        make_params = parameters(args)
        if "id" in make_params:
            del make_params["id"]
        submission_save(db, *submission_make(**make_params))
    elif comm == "add-journal":
        make_params = parameters(args)
        if "id" in make_params:
            del make_params["id"]
        journal_save(db, journal_make(**make_params))
    elif comm == "remove-users":
        for user in map(user_clean_name, args):
            print("Deleting", user)
            delete(db, "USERS", "USERNAME", user)
            db.commit()
    elif comm == "remove-submissions":
        for sub in args:
            print("Deleting", sub)
            delete(db, "SUBMISSIONS", "ID", int(sub))
            db.commit()
    elif comm == "remove-journals":
        for jrn in args:
            print("Deleting", jrn)
            delete(db, "JOURNALS", "ID", int(jrn))
            db.commit()
    elif comm == "check-errors":
        print("Checking submissions table for errors... ", end="", flush=True)
        results: List[tuple] = check_errors(db, "SUBMISSIONS")
        print("Done")
        if results:
            submissions_print(results)
        print("Checking journals table for errors... ", end="", flush=True)
        results: List[tuple] = check_errors(db, "JOURNALS")
        print("Done")
        if results:
            journals_print(results)
    elif comm == "clean":
        vacuum(db)
    else:
        raise CommandError(f"Unknown download command {comm}")


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
