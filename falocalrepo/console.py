from datetime import datetime
from inspect import cleandoc
from os import environ
from os.path import abspath
from os.path import getsize
from os.path import isfile
from os.path import join
from re import match
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from faapi import FAAPI
from falocalrepo_database import FADatabase
from falocalrepo_database import __version__ as __database_version__
from falocalrepo_server import __version__ as __server_version__
from falocalrepo_server import server

from .__version__ import __version__
from .commands import latest_version
from .commands import make_journal
from .commands import make_submission
from .commands import move_files_folder
from .commands import print_items
from .commands import print_users
from .commands import search
from .download import clean_username
from .download import download_journals
from .download import download_submissions
from .download import download_users
from .download import download_users_update
from .download import read_cookies
from .download import save_submission
from .download import write_cookies


class MalformedCommand(Exception):
    pass


class UnknownCommand(Exception):
    pass


def parameters_multi(args: Iterable[str]) -> Dict[str, List[str]]:
    params: Dict[str, List[str]] = {}
    for param, value in map(lambda p: p.split("=", 1), args):
        param = param.strip()
        params[param] = [*params.get(param, []), value]

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


def check_update(version: str, package: str):
    if (latest := latest_version(package)) and latest != version:
        print(f"New {package} version available: {latest} > {version}")


def help_(comm: str = None, *_args: str) -> str:
    """
    USAGE
        falocalrepo help [<setting>]

    ARGUMENTS
        <command>       Command to get the help of

    AVAILABLE COMMANDS
        help            Display the manual of help
        init            Display the manual of init
        config          Display the manual of config
        download        Display the manual of download
        database        Display the manual of database
    """

    if not comm:
        return cleandoc(console.__doc__)
    elif comm == help_.__name__.rstrip("_"):
        return cleandoc(help_.__doc__)
    elif comm == init.__name__:
        return cleandoc(console.__doc__)
    elif comm == config.__name__:
        return cleandoc(config.__doc__)
    elif comm == download.__name__:
        return cleandoc(download.__doc__)
    elif comm == database.__name__:
        return cleandoc(database.__doc__)
    else:
        raise UnknownCommand(comm)


def init():
    print("Database ready")


def config(db: FADatabase, comm: str = "", *args: str):
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
        cookie_a, cookie_b = read_cookies(db)
        folder: str = db.settings["FILESFOLDER"]
        print("cookie a:", cookie_a)
        print("cookie b:", cookie_b)
        print("folder  :", folder)
    elif comm == "cookies":
        if not args:
            cookie_a, cookie_b = read_cookies(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif len(args) == 2:
            write_cookies(db, args[0], args[1])
        else:
            raise MalformedCommand("cookies needs two arguments")
    elif comm == "files-folder":
        if not args:
            print("files folder:", db.settings["FILESFOLDER"])
        elif len(args) == 1:
            move_files_folder(db.settings["FILESFOLDER"], args[0])
            db.settings["FILESFOLDER"] = args[0]
        else:
            raise MalformedCommand("files-folder needs one argument")
    else:
        raise UnknownCommand(f"config {comm}")


def download(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo download <command> [<option>=<value>] [<arg1>] ... [<argN>]

    ARGUMENTS
        <command>       The type of download to execute
        <arg>           Argument for the download command

    AVAILABLE COMMANDS
        users           Download users
        update          Update database using the users and folders already saved
        submissions     Download single submissions
        journals        Download single journals
    """

    if not comm:
        raise MalformedCommand("download needs a command")

    print((s := "Connecting... "), end="", flush=True)
    api: FAAPI = FAAPI(read_cookies(db))
    print("\r" + (" " * len(s)), end="\r", flush=True)

    if not api.connection_status:
        raise ConnectionError("FAAPI cannot connect to FA")
    elif comm == "users":
        if len(args) != 2:
            raise MalformedCommand("users needs two arguments")
        users_tmp: List[str] = list(filter(bool, map(clean_username, args[0].split(","))))
        users: List[str] = sorted(set(users_tmp), key=users_tmp.index)
        folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
        folders: List[str] = sorted(set(folders_tmp), key=folders_tmp.index)
        download_users(api, db, users, folders)
    elif comm == "update":
        users: List[str] = []
        folders: List[str] = []
        opts, args = parse_args(args)
        if args and args[0] != "@":
            users_tmp: List[str] = list(filter(bool, map(clean_username, args[0].split(","))))
            users = sorted(set(users_tmp), key=users_tmp.index)
        if args[1:] and args[1] != "@":
            folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
            folders = sorted(set(folders_tmp), key=folders_tmp.index)
        download_users_update(api, db, users, folders, int(opts.get("stop", 1)))
    elif comm == "submissions":
        if not args:
            raise MalformedCommand("submissions needs at least one argument")
        sub_ids_tmp: List[str] = list(filter(str.isdigit, args))
        sub_ids: List[str] = sorted(set(sub_ids_tmp), key=sub_ids_tmp.index)
        download_submissions(api, db, sub_ids)
    elif comm == "journals":
        if not args:
            raise MalformedCommand("journals needs at least one argument")
        journal_ids_tmp: List[str] = list(filter(str.isdigit, args))
        journal_ids: List[str] = sorted(set(journal_ids_tmp), key=journal_ids_tmp.index)
        download_journals(api, db, journal_ids)
    else:
        raise UnknownCommand(f"download {comm}")


def database(db: FADatabase, comm: str = "", *args: str):
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
        history            Show commands history
        search-users       Search users
        search-submissions Search submissions
        search-journals    Search journals
        add-submission     Add a submission to the database manually
        add-journal        Add a journal to the database manually
        remove-users       Remove users from database
        remove-submissions Remove submissions from database
        remove-journals    Remove submissions from database
        server             Start local server to browse database
        merge              Merge with a second database
        clean              Clean the database with the VACUUM function
    """

    if not comm or comm == "info":
        print("Size        :", f"{getsize(db.database_path) / 1e6:.1f}MB")
        print("Users       :", len(db.users))
        print("Submissions :", len(db.submissions))
        print("Journals    :", len(db.journals))
        print("History     :", len(db.settings.read_history()) - 1)
        print("Version     :", db.settings["VERSION"])
    elif comm == "history":
        for time, command in db.settings.read_history():
            print(str(datetime.fromtimestamp(time)), command)
    elif comm == "search-users":
        results: List[Dict[str, str]] = search(db.users, parameters_multi(args))
        print_users(results)
        print(f"Found {len(results)} results")
    elif comm == "search-submissions":
        results: List[Dict[str, Union[int, str]]] = search(db.submissions, parameters_multi(args))
        print_items(results)
        print(f"Found {len(results)} results")
    elif comm == "search-journals":
        results: List[Dict[str, Union[int, str]]] = search(db.journals, parameters_multi(args))
        print_items(results)
        print(f"Found {len(results)} results")
    elif comm == "add-submission":
        make_params = parameters(args)
        make_params["id_"] = make_params.get("id", "")
        if "id" in make_params:
            del make_params["id"]
        save_submission(db, *make_submission(**make_params))
    elif comm == "add-journal":
        make_params = parameters(args)
        make_params["id_"] = make_params.get("id", "")
        if "id" in make_params:
            del make_params["id"]
        db.journals.save_journal(dict(make_journal(**make_params)))
        db.commit()
    elif comm == "remove-users":
        for user in map(clean_username, args):
            print("Deleting", user)
            del db.users[user]
            db.commit()
    elif comm == "remove-submissions":
        for sub in args:
            print("Deleting", sub)
            del db.submissions[int(sub)]
            for (user, *_) in db.users.find_from_submission(int(sub)):
                db.users.remove_submission(user, int(sub))
            db.commit()
    elif comm == "remove-journals":
        for jrn in args:
            print("Deleting", jrn)
            del db.journals[int(jrn)]
            for (user, *_) in db.users.find_from_journal(int(jrn)):
                db.users.remove_journal(user, int(jrn))
        db.commit()
    elif comm == "server":
        opts, _ = parse_args(args)
        server(db.database_path, **opts)
        print()
    elif comm == "merge":
        if len(args) != 1:
            raise MalformedCommand("merge needs one argument")
        elif not isfile(args[0]):
            raise FileNotFoundError(f"No such file or directory: '{args[0]}'")
        with FADatabase(args[0]) as db2:
            print(f"Merging with database {db2.database_path}...")
            db.update(db2)
            db.commit()
            print("Done")
    elif comm == "clean":
        db.vacuum()
    else:
        raise UnknownCommand(f"database {comm}")


def console(comm: str = "", *args: str) -> None:
    """
    USAGE
        falocalrepo [-h | -v | -d | -s] [<command>] [<arg1>] ... [<argN>]

    ARGUMENTS
        <command>       The command to execute
        <arg>           The arguments of the command

    GLOBAL OPTIONS
        -h, --help      Display this help message
        -v, --version   Display version
        -d, --database  Display database version
        -s, --server    Display server version

    AVAILABLE COMMANDS
        help            Display the manual of a command
        init            Create/update the database and exit
        config          Manage settings
        download        Perform downloads
        database        Operate on the database
    """

    console.__doc__ = f"""
    falocalrepo: {__version__}
    falocalrepo-database: {__database_version__}
    falocalrepo-server: {__server_version__}
    """ + console.__doc__

    if not comm:
        print(help_())
        return
    elif comm in ("-h", "--help"):
        print(help_())
        return
    elif comm == "help":
        print(help_(*args))
        return
    elif comm in ("-v", "--version"):
        print(__version__)
        return
    elif comm in ("-d", "--database"):
        print(__database_version__)
        return
    elif comm in ("-s", "--server"):
        print(__server_version__)
        return
    elif comm not in (init.__name__, config.__name__, download.__name__, database.__name__):
        raise UnknownCommand(comm)

    check_update(__version__, "falocalrepo")
    check_update(__database_version__, "falocalrepo-database")
    check_update(__server_version__, "falocalrepo-server")

    # Initialise and prepare database
    database_path = "FA.db"

    if db_path := environ.get("FALOCALREPO_DATABASE", None):
        print(f"Using FALOCALREPO_DATABASE: {db_path}")
        database_path = db_path if db_path.endswith(".db") else join(db_path, database_path)

    db: FADatabase = FADatabase(abspath(database_path))

    try:
        db.upgrade()
        db.settings.add_history(f"{comm} {' '.join(args)}".strip())
        db.commit()

        if comm == init.__name__:
            init()
        elif comm == config.__name__:
            config(db, *args)
        elif comm == download.__name__:
            download(db, *args)
        elif comm == database.__name__:
            database(db, *args)
    finally:
        # Close database and update totals
        if db is not None:
            db.settings["USRN"] = str(len(db.users))
            db.settings["SUBN"] = str(len(db.submissions))
            db.settings["JRNN"] = str(len(db.journals))
            db.commit()
            db.close()
