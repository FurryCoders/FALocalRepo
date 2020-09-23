from datetime import datetime
from inspect import cleandoc
from os.path import getsize
from os.path import isfile
from re import match
from sqlite3 import Connection
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from faapi import FAAPI
from falocalrepo_database import __version__ as __database_version__
from falocalrepo_database import check_errors
from falocalrepo_database import connect_database
from falocalrepo_database import count
from falocalrepo_database import delete
from falocalrepo_database import journals_indexes
from falocalrepo_database import make_tables
from falocalrepo_database import read_setting
from falocalrepo_database import save_journal
from falocalrepo_database import save_submission
from falocalrepo_database import search_journals
from falocalrepo_database import search_submissions
from falocalrepo_database import submissions_indexes
from falocalrepo_database import update_database
from falocalrepo_database import vacuum
from falocalrepo_database import write_setting
from falocalrepo_server import __version__ as __server_version__
from falocalrepo_server import server

from .__version__ import __version__
from .commands import make_journal
from .commands import make_submission
from .commands import move_files_folder
from .commands import print_items
from .download import clean_username
from .download import cookies_load
from .download import cookies_read
from .download import cookies_write
from .download import journals_download
from .download import submissions_download
from .download import users_download
from .download import users_update


class MalformedCommand(Exception):
    pass


class UnknownCommand(Exception):
    pass


def parameters_multi(args: Iterable[str]) -> Dict[str, List[str]]:
    params: Dict[str, List[str]] = {}
    for param, value in map(lambda p: p.split("=", 1), args):
        param = param.strip()
        params[param] = params.get(param, []) + [value]

    return params


def parameters(args: Iterable[str]) -> Dict[str, str]:
    return {p: v for p, v in map(lambda p: p.split("=", 1), args)}


def parse_args(args_raw: Iterable[str]) -> Tuple[Dict[str, str], List[str]]:
    opts: List[str] = []
    args: List[str] = []

    for i, arg in enumerate(args_raw):
        if match(r"\w+=\w+", arg):
            opts.append(arg)
        elif arg == "--":
            args.extend(args_raw[i + 1:])
            break
        else:
            args.extend(args_raw[i:])
            break

    return parameters(opts), args


def help_message(comm: str = None, *_args: str) -> str:
    if not comm:
        return cleandoc(console.__doc__)
    elif comm == config.__name__:
        return cleandoc(config.__doc__)
    elif comm == download.__name__:
        return cleandoc(download.__doc__)
    elif comm == database.__name__:
        return cleandoc(database.__doc__)
    else:
        raise UnknownCommand(comm)


def config(db: Connection, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo config [<setting>] [<value1>] ... [<valueN>]

    ARGUMENTS
        <setting>       Setting to read/edit
        <value>         New setting value

    AVAILABLE SETTINGS
        list            List settings
        cookies         Cookies for the API
        files-folder    Files download folder
    """

    if not comm or comm == "list":
        cookie_a, cookie_b = cookies_read(db)
        folder: str = read_setting(db, "FILESFOLDER")
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
            raise MalformedCommand("cookies needs two arguments")
    elif comm == "files-folder":
        if not args:
            print("files folder:", read_setting(db, "FILESFOLDER"))
        elif len(args) == 1 and args[0]:
            move_files_folder(db, read_setting(db, "FILESFOLDER"), args[0])
        else:
            raise MalformedCommand("files-folder needs one argument")
    else:
        raise UnknownCommand(f"config {comm}")


def download(db: Connection, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo download <command> [<option>=<value>] [<arg1>] ... [<argN>]

    ARGUMENTS
        <command>       The type of download to execute
        <arg>           Argument for the download command

    AVAILABLE COMMANDS
        users           Download users. First argument is a comma-separated list of
                          users, second is a comma-separated list of folders
        submissions     Download single submissions. Arguments are submission ID's
        update          Update database using the users and folders already saved
    """

    if not comm:
        raise MalformedCommand("download needs a command")

    api: FAAPI = FAAPI()
    cookies_load(api, *cookies_read(db))

    if not api.connection_status:
        raise ConnectionError("FAAPI cannot connect to FA")
    elif comm == "update":
        users: Optional[List[str]] = None
        folders: Optional[List[str]] = None
        opts, args = parse_args(args)
        if args and args[0] != "@":
            users_tmp: List[str] = list(filter(bool, map(clean_username, args[0].split(","))))
            users = sorted(set(users_tmp), key=users_tmp.index)
        if args[1:] and args[1] != "@":
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
            folders = sorted(set(folders_tmp), key=folders_tmp.index)
        users_update(api, db, users, folders, int(opts.get("stop", 1)))
    elif comm == "users":
        if len(args) == 2 and args[0] and args[1]:
            users_tmp: List[str] = list(filter(bool, map(clean_username, args[0].split(","))))
            users: List[str] = sorted(set(users_tmp), key=users_tmp.index)
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
            folders: List[str] = sorted(set(folders_tmp), key=folders_tmp.index)
            users_download(api, db, users, folders)
        else:
            raise MalformedCommand("users needs two arguments")
    elif comm == "submissions":
        if not args:
            raise MalformedCommand("submissions needs at least one argument")
        sub_ids_tmp: List[str] = list(filter(str.isdigit, args))
        sub_ids: List[str] = sorted(set(sub_ids_tmp), key=sub_ids_tmp.index)
        submissions_download(api, db, sub_ids)
    elif comm == "journals":
        if not args:
            raise MalformedCommand("journals needs at least one argument")
        journal_ids_tmp: List[str] = list(filter(str.isdigit, args))
        journal_ids: List[str] = sorted(set(journal_ids_tmp), key=journal_ids_tmp.index)
        journals_download(api, db, journal_ids)
    else:
        raise UnknownCommand(f"download {comm}")


def database(db: Connection, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo database [<operation>] [<param1>=<value1>] ...
                    [<paramN>=<valueN>]

    ARGUMENTS
        <command>          The database operation to execute
        <param>            Parameter for the database operation
        <value>            Value of the parameter

    AVAILABLE COMMANDS
        info               Show database information
        search-submissions Search submissions
        search-journals    Search submissions
        add-submission     Add a submission to the database manually
        add-journal        Add a journal to the database manually
        remove-users       Remove users from database
        remove-submissions Remove submissions from database
        remove-journals    Remove submissions from database
        server             Start local server to browse database
        check-errors       Check the database for errors
        clean              Clean the database with the VACUUM function
    """

    if not comm or comm == "info":
        size: int = getsize("FA.db")
        sub_n: int = int(read_setting(db, "SUBN"))
        usr_n: int = int(read_setting(db, "USRN"))
        jrn_n: int = int(read_setting(db, "JRNN"))
        last_update: float = float(read_setting(db, "LASTUPDATE"))
        last_start: float = float(read_setting(db, "LASTSTART"))
        version: str = read_setting(db, "VERSION")
        print("Size       :", f"{size / 1e6:.1f}MB")
        print("Submissions:", sub_n)
        print("Users      :", usr_n)
        print("Journals   :", jrn_n)
        print("Last update:", str(datetime.fromtimestamp(last_update)) if last_update else 0)
        print("Last start :", str(datetime.fromtimestamp(last_start)) if last_start else 0)
        print("Version    :", version)
    elif comm == "search-submissions":
        results: List[tuple] = search_submissions(db, **{"order": ["AUTHOR", "ID"], **parameters_multi(args)})
        print_items(results, submissions_indexes)
        print(f"Found {len(results)} results")
    elif comm == "search-journals":
        results: List[tuple] = search_journals(db, **{"order": ["AUTHOR", "ID"], **parameters_multi(args)})
        print_items(results, journals_indexes)
        print(f"Found {len(results)} results")
    elif comm == "add-submission":
        make_params = parameters(args)
        if "id" in make_params:
            del make_params["id"]
        save_submission(db, *make_submission(**make_params))
    elif comm == "add-journal":
        make_params = parameters(args)
        if "id" in make_params:
            del make_params["id"]
        save_journal(db, make_journal(**make_params))
    elif comm == "remove-users":
        for user in map(clean_username, args):
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
    elif comm == "server":
        opts, _ = parse_args(args)
        server(**opts)
    elif comm == "check-errors":
        print("Checking submissions table for errors... ", end="", flush=True)
        results: List[tuple] = check_errors(db, "SUBMISSIONS")
        print("Done")
        if results:
            print_items(results, submissions_indexes)
        print("Checking journals table for errors... ", end="", flush=True)
        results: List[tuple] = check_errors(db, "JOURNALS")
        print("Done")
        if results:
            print_items(results, journals_indexes)
    elif comm == "clean":
        vacuum(db)
    else:
        raise UnknownCommand(f"database {comm}")


def console(comm: str = "", *args: str) -> None:
    """
    USAGE
        falocalrepo [-h] [-v] [-d] [<command>] [<arg1>] ... [<argN>]

    ARGUMENTS
        <command>       The command to execute
        <arg>           The arguments of the command

    GLOBAL OPTIONS
        -h, --help      Display this help message
        -v, --version   Display version
        -d, --database  Display database version

    AVAILABLE COMMANDS
        help            Display the manual of a command
        init            Create/update the database and exit, default command
        config          Manage settings
        download        Perform downloads
        database        Operate on the database
    """

    console.__doc__ = f"    falocalrepo: {__version__}\n" + \
                      f"    falocalrepo-database: {__database_version__}\n" + \
                      f"    falocalrepo-server: {__server_version__}\n" + \
                      console.__doc__

    if comm in ("-v", "--version"):
        print(__version__)
        return
    elif comm in ("-d", "--database"):
        print(__database_version__)
        return
    elif comm in ("-h", "--help"):
        print(help_message())
        return
    elif not comm or comm == "help":
        print(help_message(*args))
        return
    elif comm not in ("init", config.__name__, download.__name__, database.__name__):
        raise UnknownCommand(comm)

    db: Optional[Connection] = None

    try:
        # Initialise and prepare database
        if isfile("FA.db"):
            db = update_database(connect_database("FA.db"))
        else:
            db = connect_database("FA.db")
            make_tables(db)

        if comm == "init":
            print("Database ready")
            return

        write_setting(db, "LASTSTART", str(datetime.now().timestamp()))

        if comm == config.__name__:
            config(db, *args)
        elif comm == download.__name__:
            download(db, *args)
        elif comm == database.__name__:
            database(db, *args)
    finally:
        # Close database and update totals
        if db is not None:
            write_setting(db, "USRN", str(count(db, "USERS")))
            write_setting(db, "SUBN", str(count(db, "SUBMISSIONS")))
            write_setting(db, "JRNN", str(count(db, "JOURNALS")))
            db.commit()
            db.close()
