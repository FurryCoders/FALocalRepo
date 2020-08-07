from argparse import ArgumentParser
from argparse import Namespace
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from faapi import FAAPI

from .__doc__ import help_message
from .__version__ import __version__
from .commands import files_folder_move
from .commands import submission_make
from .commands import submissions_download
from .commands import submissions_print
from .commands import submissions_search
from .commands import users_download
from .commands import users_update
from .database import Connection
from .database import check_errors
from .database import connect_database
from .database import make_database
from .download import load_cookies
from .download import submission_save
from .settings import cookies_read
from .settings import cookies_write
from .settings import setting_read
from .settings import setting_write


def config(db: Connection, args: List[str]):
    if not args:
        cookie_a, cookie_b = cookies_read(db)
        folder: str = setting_read(db, "FILESFOLDER")
        version: str = setting_read(db, "VERSION")
        print("cookie a:", cookie_a)
        print("cookie b:", cookie_b)
        print("folder  :", folder)
        print("version :", version)
    elif args[0] == "cookies":
        if not args[1:]:
            cookie_a, cookie_b = cookies_read(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif len(args[1:]) == 2 and args[1] and args[2]:
            cookies_write(db, args[1], args[2])
        else:
            raise Exception("Malformed command: cookies needs two arguments")
    elif args[0] == "files-folder":
        if not args[1:]:
            print("files folder:", setting_read(db, "FILESFOLDER"))
        elif len(args[1:]) == 1 and args[1]:
            files_folder_move(db, setting_read(db, "FILESFOLDER"), args[1])
        else:
            raise Exception("Malformed command: files-folder needs one argument")
    else:
        raise Exception(f"Unknown config command {args[0]}")


def download(db: Connection, args: List[str]):
    api: FAAPI = FAAPI()
    load_cookies(api, *cookies_read(db))

    if not args:
        raise Exception("Malformed command: download needs a command")
    elif args[0] == "update":
        users_update(api, db)
    elif args[0] == "users":
        if len(args[1:]) == 2 and args[1] and args[2]:
            users: List[str] = list(map(lambda s: s.strip(), args[1].split(",")))
            folders: List[str] = list(map(lambda s: s.strip(), args[2].split(",")))
            users_download(api, db, users, folders)
        else:
            raise Exception("Malformed command: users needs two arguments")
    elif args[0] == "submissions":
        if not args[1:]:
            raise Exception("Malformed command: submissions needs at least one argument")
        sub_ids: List[str] = list(filter(len, args[1:]))
        submissions_download(api, db, sub_ids)
    else:
        raise Exception(f"Unknown download command {args[0]}")


def database(db: Connection, args: List[str]):
    if not args:
        raise Exception("Malformed command: database needs a command")
    elif args[0] == "search":
        if len(args[1:]) > 9:
            raise Exception("Malformed command: search needs 9 or less arguments")
        elif not any(args[1:]):
            raise Exception("Malformed command: search needs at least 1 argument")
        search_params: Dict[str, str] = {(p := arg.split("="))[0].strip().lower(): p[1].strip() for arg in args[1:]}
        results: List[tuple] = submissions_search(
            db,
            authors=[search_params["author"]] if search_params.get("author", None) else [],
            titles=[search_params["title"]] if search_params.get("title", None) else [],
            dates=[search_params["date"]] if search_params.get("date", None) else [],
            descriptions=[search_params["description"]] if search_params.get("description", None) else [],
            tags=search_params["tags"].split(",") if search_params.get("tags", None) else [],
            categories=[search_params["category"]] if search_params.get("category", None) else [],
            species=[search_params["species"]] if search_params.get("species", None) else [],
            genders=[search_params["gender"]] if search_params.get("gender", None) else [],
            ratings=[search_params["rating"]] if search_params.get("rating", None) else [],
        )
        submissions_print(results, sort=True)
    elif args[0] == "manual-entry":
        if len(args[1:]) > 11:
            raise Exception("Malformed command: search needs 11 or less arguments")
        elif len(args[1:]) < 11:
            raise Exception("Malformed command: search needs at least 8 arguments")
        make_params: Dict[str, str] = {(p := arg.split("="))[0].strip().lower(): p[1].strip() for arg in args[1:]}
        submission_save(db, *submission_make(
            id_=make_params.get("id", ""),
            author=make_params.get("author", ""),
            title=make_params.get("title", ""),
            date=make_params.get("date", ""),
            tags=make_params.get("tags", ""),
            description=make_params.get("description", ""),
            rating=make_params.get("rating", ""),
            category=make_params.get("category", ""),
            species=make_params.get("species", ""),
            gender=make_params.get("gender", ""),
            file_url=make_params.get("file_url", ""),
            file_local_url=make_params.get("file_local_url", "")
        ))
    elif args[0] == "check-errors":
        print("Checking submissions table for errors... ", end="", flush=True)
        results: List[tuple] = check_errors(db, "SUBMISSIONS")
        print("Done")
        if results:
            submissions_print(results)


def main_console(args: List[str]):
    prog: str = args[0]
    comm: str = args[1] if args[1:] else ""
    args = list(filter(bool, args[2:]))

    args_parser: ArgumentParser = ArgumentParser(add_help=False)
    args_parser.add_argument("-h, --help", dest="help", action="store_true", default=False)
    args_parser.add_argument("-v, --version", dest="version", action="store_true", default=False)

    global_options: List[str] = [arg for arg in args[1:] if arg.startswith("-")]
    args_parsed: Namespace = args_parser.parse_args(global_options)

    if args_parsed.help:
        print(help_message(prog))
    elif args_parsed.version:
        print(__version__)
    elif (not comm and not args) or comm == "help":
        print(help_message(prog, args))

    db: Optional[Connection] = None

    try:
        # Initialise and prepare database
        db = connect_database("FA.db")
        make_database(db)
        setting_write(db, "LASTSTART", str(datetime.now().timestamp()))

        if comm == "config":
            config(db, args)
        elif comm == "download":
            download(db, args)
        elif comm == "database":
            database(db, args)
        else:
            raise Exception(f"Unknown {comm} command.")
    finally:
        # Close database
        if db is not None:
            db.commit()
            db.close()
