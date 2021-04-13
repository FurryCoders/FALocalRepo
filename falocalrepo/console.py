from datetime import datetime
from inspect import cleandoc
from json import dumps
from json import load
from os import environ
from os.path import getsize
from os.path import join
from os.path import split
from re import match
from sys import stderr
from typing import Callable
from typing import Iterable
from typing import Union

from faapi import __version__ as __faapi_version__
from falocalrepo_database import FADatabase
from falocalrepo_database import FADatabaseCursor
from falocalrepo_database import FADatabaseTable
from falocalrepo_database import __version__ as __database_version__
from falocalrepo_server import __version__ as __server_version__
from falocalrepo_server import server
from psutil import AccessDenied
from psutil import NoSuchProcess
from psutil import process_iter

from .__version__ import __version__
from .commands import latest_version
from .commands import make_journal
from .commands import make_submission
from .commands import move_files_folder
from .commands import print_items
from .commands import print_users
from .commands import search
from .download import clean_username
from .download import download_journals as download_journals_
from .download import download_submissions as download_submissions_
from .download import download_users as download_users_
from .download import download_users_update
from .download import read_cookies
from .download import write_cookies


class MalformedCommand(Exception):
    pass


class UnknownCommand(Exception):
    pass


class MultipleInstances(Exception):
    pass


def check_process(process: str):
    ps: int = 0
    for p in process_iter():
        try:
            ps += "python" in p.name().lower() and any(process in split(cmd) for cmd in p.cmdline())
        except (NoSuchProcess, AccessDenied):
            pass
        if ps > 1:
            raise MultipleInstances(f"Another instance of {process} was detected")


def check_database_version(db: FADatabase, raise_for_error: bool = True):
    if (err := db.check_version(raise_for_error=False)) is not None:
        print(f"Database version is not latest: {db.version} != {__database_version__}")
        print("Use database upgrade command to upgrade database")
        if raise_for_error:
            raise err


def check_database_connections(db: FADatabase):
    if len(db.check_connection(raise_for_error=False)) > 1:
        db.close()
        raise MultipleInstances(f"Another connection to {db.database_path} was detected")


def raiser(e: Exception) -> Callable:
    def inner(*_):
        raise e

    return inner


def docstring_parameter(*args, **kwargs):
    def inner(obj: {__doc__}) -> {__doc__}:
        obj.__doc__ = obj.__doc__.format(*args, **kwargs)
        return obj

    return inner


def parameters_multi(args: Iterable[str]) -> dict[str, list[str]]:
    params: dict[str, list[str]] = {}
    for param, value in map(lambda p: p.split("=", 1), args):
        param = param.strip()
        params[param] = [*params.get(param, []), value]

    return params


def parameters(args: Iterable[str]) -> dict[str, str]:
    return {p: v for p, v in map(lambda p: p.split("=", 1), args)}


def parse_args(args_raw: Iterable[str]) -> tuple[dict[str, str], list[str]]:
    opts: list[str] = []
    args: list[str] = []

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


def check_update(version: str, package: str) -> bool:
    if (latest := latest_version(package)) and latest != version:
        print(f"New {package} version available: {version} > {latest}")
        return True
    return False


def help_(comm: str = "", op: str = "", *_rest) -> str:
    """
    USAGE
        falocalrepo help [<command> [<operation>]]

    ARGUMENTS
        <command>       Command to get the help of
        <operation>     Command operation to get the help of

    DESCRIPTION
        Get help for a specific command or operation. If no command is passed
        then a general help message is given instead.
    """

    f = {
        "": console,
        "help": help_,
        "init": init,
        "config": config,
        "config list": config_list,
        "config cookies": config_cookies,
        "config files-folder": config_files_folder,
        "download": download,
        "download users": download_users,
        "download update": download_update,
        "download submissions": download_submissions,
        "download journals": download_journals,
        "database": database,
        "database info": database_info,
        "database history": database_history,
        "database search-users": database_search_users,
        "database search-submissions": database_search_submissions,
        "database search-journals": database_search_journals,
        "database add-submission": database_add_submission,
        "database add-journal": database_add_journal,
        "database add-user": database_add_user,
        "database remove-users": database_remove_users,
        "database remove-submissions": database_remove_submissions,
        "database remove-journals": database_remove_journals,
        "database server": database_server,
        "database merge": database_merge,
        "database copy": database_copy,
        "database clean": database_clean,
        "database upgrade": database_upgrade,
    }.get(comm := f"{comm} {op}".strip(), None)

    if f is None:
        raise UnknownCommand(comm)

    return cleandoc(f.__doc__)


def init(db: FADatabase):
    """
    USAGE
        falocalrepo init

    DESCRIPTION
        The init command initialises the database and then exits. It can be used to
        create the database without performing any other operation. If a database is
        already present, no operation is performed.
    """

    check_database_version(db)
    print("Database ready")


def config_list(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo config list

    DESCRIPTION
        Prints a list of stored settings.
    """

    for c in read_cookies(db):
        print(f"cookie {c['name']}:", c['value'])
    print("files folder:", db.settings["FILESFOLDER"])


def config_cookies(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo config cookies [<name1>=<value1> ... <nameN>=<valueN>]

    ARGUMENTS
        <name>   The name of the cookie (e.g. a)
        <value>  The value of the cookie

    DESCRIPTION
        Read or modify stored cookies.

    EXAMPLES
        falocalrepo config cookies a=a1b2c3d4-1234 b=e5f6g7h8-5678
    """

    if not args:
        for c in read_cookies(db):
            print(f"cookie {c['name']}:", c['value'])
    elif len(args) == 2:
        write_cookies(db, **parse_args(args)[0])
    else:
        raise MalformedCommand("cookies needs two arguments")


def config_files_folder(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo config files-folder [<new folder>]

    ARGUMENTS
        <new folder>    Path to new files folder

    DESCRIPTION
        Read or modify the folder used to store submission files. This can be any
        path relative to the folder of the database. If a new value is given, the
        program will move any files to the new location.
    """

    if not args:
        print("files folder:", db.settings["FILESFOLDER"])
    elif len(args) == 1:
        move_files_folder(db.settings["FILESFOLDER"], args[0])
        db.settings["FILESFOLDER"] = args[0]
    else:
        raise MalformedCommand("files-folder needs one argument")


def config(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo config [<setting> [<value1>] ... [<valueN>]]

    ARGUMENTS
        <setting>       Setting to read/edit
        <value>         New setting value

    AVAILABLE SETTINGS
        list            List settings
        cookies         Cookies for the API
        files-folder    Files download folder

    DESCRIPTION
        The config command allows to change the settings used by the program.
    """

    check_database_version(db)

    {
        "": config_list,
        "list": config_list,
        "cookies": config_cookies,
        "files-folder": config_files_folder,
    }.get(comm, raiser(UnknownCommand(f"config {comm}")))(db, *args)


def download_users(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download users <user1>[,...,<userN>] <folder1>[,...,<folderN>]

    ARGUMENTS
        <user>      Username
        <folder>    One of gallery, scraps, favorites, journals

    DESCRIPTION
        Download specific user folders. Requires two arguments with comma separated
        users and folders. Prepending 'list-' to a folder allows to list all remote
        items in a user folder without downloading them. Supported folders are:
            * gallery
            * scraps
            * favorites
            * journals

    EXAMPLES
        falocalrepo download users tom,jerry gallery,scraps,journals
        falocalrepo download users tom list-favorites
    """

    if len(args) != 2:
        raise MalformedCommand("users needs two arguments")

    users_tmp: list[str] = list(filter(bool, map(clean_username, args[0].split(","))))
    users: list[str] = sorted(set(users_tmp), key=users_tmp.index)
    folders_tmp: list[str] = list(filter(bool, map(str.strip, args[1].split(","))))
    folders: list[str] = sorted(set(folders_tmp), key=folders_tmp.index)
    download_users_(db, users, folders)


def download_update(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download update [stop=<stop n>] [deactivated=<deactivated>]
                    [<user1>,...,<userN> | @] [<folder1>,...,<folderN> | @]

    ARGUMENTS
        <stop n>       Number of submissions to find in database before stopping,
                       defaults to 1
        <deactivated>  Set to 'true' to check previously deactivated users, other
                       values are ignored
        <user>         Username
        <folder>       One of gallery, scraps, favorites, journals

    DESCRIPTION
        Update the repository by checking the previously downloaded folders
        (gallery, scraps, favorites or journals) of each user and stopping when it
        finds a submission that is already present in the database. If a list of
        users and/or folders is passed, the update will be limited to those. To
        limit the update to certain folders without skipping any user, use '@' in
        place of the users argument. The stop=<n> option allows to stop updating
        after finding n submissions in a user's database entry, defaults to 1. If a
        user is deactivated, the folders in the database will be prepended with a
        '!'. Deactivated users will be skipped during the update unless the
        <deactivated> option is set to 'true'.

    EXAMPLES
        falocalrepo download update stop=5
        falocalrepo download update deactivated=true @ gallery,scraps
        falocalrepo download update tom,jerry
    """

    users: list[str] = []
    folders: list[str] = []
    opts, args = parse_args(args)
    if args and args[0] != "@":
        users_tmp: list[str] = list(filter(bool, map(clean_username, args[0].split(","))))
        users = sorted(set(users_tmp), key=users_tmp.index)
    if args[1:] and args[1] != "@":
        folders_tmp: list[str] = list(filter(bool, map(str.strip, args[1].split(","))))
        folders = sorted(set(folders_tmp), key=folders_tmp.index)
    download_users_update(db, users, folders, int(opts.get("stop", 1)), opts.get("deactivated", "").lower() == "true")


def download_submissions(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download submissions <id1> ... [<idN>]

    ARGUMENTS
        <id>    Submission ID

    DESCRIPTION
        Download specific submissions. Requires submission ID's provided as separate
        arguments. If the submission is already in the database it is ignored.

    EXAMPLES
        falocalrepo download submissions 12345678 13572468 87651234
    """

    if not args:
        raise MalformedCommand("submissions needs at least one argument")
    sub_ids_tmp: list[str] = list(filter(str.isdigit, args))
    sub_ids: list[str] = sorted(set(sub_ids_tmp), key=sub_ids_tmp.index)
    download_submissions_(db, sub_ids)


def download_journals(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download journals <id1> ... [<idN>]

    ARGUMENTS
        <id>    Journal ID

    DESCRIPTION
        Download specific journals. Requires journal ID's provided as separate
        arguments. If the journal is already in the database it is ignored.

    EXAMPLES
        falocalrepo download journals 123456 135724 876512
    """

    if not args:
        raise MalformedCommand("journals needs at least one argument")
    journal_ids_tmp: list[str] = list(filter(str.isdigit, args))
    journal_ids: list[str] = sorted(set(journal_ids_tmp), key=journal_ids_tmp.index)
    download_journals_(db, journal_ids)


def download(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo download <operation> [<option>=<value>] [<arg1>] ... [<argN>]

    ARGUMENTS
        <operation>     The download operation to execute
        <option>        Option for the download command
        <value>         Value of an option
        <arg>           Argument for the download command

    AVAILABLE COMMANDS
        users           Download users
        update          Update database using the users and folders already saved
        submissions     Download single submissions
        journals        Download single journals

    DESCRIPTION
        The download command performs all download operations to save and update
        users, submissions, and journals. Submissions are downloaded together with
        their thumbnails, if there are any.
    """

    check_database_version(db)
    check_process("falocalrepo")

    {
        "": raiser(MalformedCommand("download needs a command")),
        "users": download_users,
        "update": download_update,
        "submissions": download_submissions,
        "journals": download_journals,
    }.get(comm, raiser(UnknownCommand(f"download {comm}")))(db, *args)


def database_info(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo database info

    DESCRIPTION
        Show database information, statistics and version.
    """

    print("Size        :", f"{getsize(db.database_path) / 1e6:.1f}MB")
    print("Users       :", len(db.users))
    print("Submissions :", len(db.submissions))
    print("Journals    :", len(db.journals))
    print("History     :", (len(h) - 1) if (h := db.settings.read_history()) else 0)
    print("Version     :", db.version)


def database_history(db: FADatabase):
    """
    USAGE
        falocalrepo database history

    DESCRIPTION
        Show commands history.
    """

    for time, command in db.settings.read_history():
        print(str(datetime.fromtimestamp(time)), command)


def database_search(table: FADatabaseTable, print_func: Callable, *args: str):
    """
    USAGE
        falocalrepo database search-{0} [json=<json>] [columns=<columns>]
                    [<param1>=<value1>] ... [<paramN>=<valueN>]

    ARGUMENTS
        <json>      Set to 'true' to output metadata in JSON format
        <columns>   Comma-separated list of columns to select, only active for JSON
        <param>     Search parameter
        <value>     Value of the parameter

    DESCRIPTION
        Search the {0} entries using metadata fields. Search parameters can
        be passed multiple times to act as OR values. All columns of the {0}
        table are supported. Parameters can be lowercase. If no parameters are
        supplied, a list of all {0} will be returned instead. If <json> is
        set to 'true', the results are printed as a list of objects in JSON format.
        If <columns> is passed, then the objects printed with the JSON option will
        only contain those fields.
    """

    opts = parameters_multi(args)
    json, cols = opts.get("json", [None])[0] == "true", opts["columns"][0].split(",") if "columns" in opts else None
    results: list[dict[str, Union[int, str]]] = search(table, opts, cols if cols and json else None)
    if json:
        print(dumps(results))
    else:
        print_func(results)
        print(f"Found {len(results)} users")


@docstring_parameter(database_search.__doc__.format("users"))
def database_search_users(db: FADatabase, *args: str):
    """
    {0}

    EXAMPLES
        falocalrepo database search-users json=true folders=%gallery%
    """

    database_search(db.users, print_users, *args)


@docstring_parameter(database_search.__doc__.format("submissions"))
def database_search_submissions(db: FADatabase, *args: str):
    """
    {0}

    EXAMPLES
        falocalrepo database search-submissions tags=%|cat|%|mouse|% date=2020-% \\
            category=%artwork% order="AUTHOR" order="ID"
        falocalrepo database search-submissions json=true columns=id,author,title \\
            tags=%|cat|% tags=%|mouse|% date=2020-% category=%artwork%
    """

    database_search(db.submissions, print_items, *args)


@docstring_parameter(database_search.__doc__.format("journals"))
def database_search_journals(db: FADatabase, *args: str):
    """
    {0}

    EXAMPLES
        falocalrepo database search-journals date=2020-% author=CatArtist \\
            order="ID DESC"
        falocalrepo database search-journals json=true columns=id,author,title \\
            date=2020-% date=2019-% content=%commission%
    """

    database_search(db.journals, print_items, *args)


def database_add_user(db: FADatabase, *args):
    """
    USAGE
        falocalrepo database add-user <json>

    ARGUMENTS
        <json>  Path to a JSON file containing the user metadata

    DESCRIPTION
        Add or replace a user entry into the database using metadata from a JSON
        file. If the user already exists in the database, fields may be omitted from
        the JSON, except for the ID. Omitted fields will not be replaced in the
        database and will remain as they are. The following fields are supported:
            * 'username'
        The following fields are optional:
            * 'folders'

    EXAMPLES
        falocalrepo database add-user ./user.json
    """

    make_params: dict[str, str] = parameters(args)
    username: str = db.users.new_user(make_params["username"])
    if make_params.get("folders", None) is not None:
        folders: set[str] = set(db.users[username]["FOLDERS"])
        folders_new: set[str] = set(filter(bool, map(str.lower, make_params["folders"].split(","))))
        for f in folders - folders_new:
            db.users.remove_user_folder(username, f)
        for f in folders_new - folders:
            db.users.add_user_folder(username, f)
    db.commit()


def database_add_submission(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database add-submissions <json> [file=<file>] [thumb=<thumb>]

    ARGUMENTS
        <json>  Path to a JSON file containing the submission metadata
        <file>  Path to new file
        <thumb> Path to new thumbnail

    DESCRIPTION
        Add or replace a submission entry into the database using metadata from a
        JSON file. If the submission already exists in the database, fields may be
        omitted from the JSON, except for the ID. Omitted fields will not be
        replaced in the database and will remain as they are. The optional <file>
        and <thumb> parameters allow to add or replace the submission file and
        thumbnail respectively. The following fields are supported:
            * 'id'
            * 'title'
            * 'author'
            * 'date' date in the format YYYY-MM-DD
            * 'description'
            * 'category'
            * 'species'
            * 'gender'
            * 'rating'
            * 'type' image, text, music, or flash
            * 'folder' gallery or scraps
            * 'fileurl' the remote URL of the submission file
        The following fields are optional:
            * 'tags' list of tags, if omitted it defaults to existing entry or empty
            * 'favorite' list of users that faved the submission, if omitted it
                defaults to existing entry or empty
            * 'mentions' list of mentioned users, if omitted it defaults to existing
                entry or mentions are extracted from the description
            * 'userupdate' 1 if the submission is downloaded as part of a user
                gallery/scraps else 0, if omitted it defaults to entry or 0

    EXAMPLES
        falocalrepo database add-submission ./submission/metadata.json \\
            file=./submission/submission.pdf thumb=./submission/thumbnail.jpg
    """

    data: dict = load(open(args[0]))
    opts: dict = parameters(args[1:])
    make_submission(db, data, opts.get("file", None), opts.get("thumbnail", None))


def database_add_journal(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database add-journal <json>

    ARGUMENTS
        <json>  Path to a JSON file containing the journal metadata

    DESCRIPTION
        Add or replace a journal entry into the database using metadata from a JSON
        file. If the journal already exists in the database, fields may be omitted
        from the JSON, except for the ID. Omitted fields will not be replaced in the
        database and will remain as they are. The following fields are supported:
            * 'id'
            * 'title'
            * 'author'
            * 'date' date in the format YYYY-MM-DD
            * 'content' the body of the journal
        The following fields are optional:
             * 'mentions' list of mentioned users, if omitted it defaults to existing
                entry or mentions are extracted from the content

    EXAMPLES
        falocalrepo database add-journal ./journal.json"
    """

    data: dict = load(open(args[0]))
    make_journal(db, data)


def database_remove_users(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database remove-users <user1> ... [<userN>]

    ARGUMENTS
        <user>  Username

    DESCRIPTION
        Remove specific users from the database.
    """

    for user in map(clean_username, args):
        print("Deleting", user)
        del db.users[user]
        db.commit()


def database_remove_submissions(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database remove-submissions <id1> ... [<idN>]

    ARGUMENTS
        <id>    Submission ID

    DESCRIPTION
        Remove specific submissions from the database.
    """

    for sub in args:
        print("Deleting", sub)
        del db.submissions[int(sub)]
        db.commit()


def database_remove_journals(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database remove-journals <id1> ... [<idN>]

    ARGUMENTS
        <id>    Journal ID

    DESCRIPTION
        Remove specific journals from the database.
    """

    for jrn in args:
        print("Deleting", jrn)
        del db.journals[int(jrn)]
    db.commit()


@docstring_parameter(__server_version__)
def database_server(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database server [host=<host>] [port=<port>]

    ARGUMENTS
        <host>  Host address
        <port>  Port

    DESCRIPTION
        Starts a server at <host>:<port> to navigate the database, defaults to
        0.0.0.0:8080. For more details on usage see
        https://pypi.org/project/falocalrepo-server/{0}.

    EXAMPLES
        falocalrepo database server host=127.0.0.1 port=5000
    """

    opts, _ = parse_args(args)
    server(db.database_path, **opts)
    print()


def database_merge_copy(db: FADatabase, merge: bool = True, *args):
    if not args:
        raise MalformedCommand("copy needs at least a database argument")

    opts = parameters_multi(args[1:])
    usrs_opts: dict[str, list[str]] = {m.group(1): v for k, v in opts.items() if (m := match(r"users\.(.+)", k))}
    subs_opts: dict[str, list[str]] = {m.group(1): v for k, v in opts.items() if (m := match(r"submissions\.(.+)", k))}
    jrns_opts: dict[str, list[str]] = {m.group(1): v for k, v in opts.items() if (m := match(r"journals\.(.+)", k))}

    with FADatabase(args[0]) as db2:
        print(f"{'Merging with database' if merge else 'Copying entries to'} {db2.database_path}...")
        cursors: list[FADatabaseCursor] = []
        cursors.append((db2 if merge else db).users.select(usrs_opts, like=True)) if usrs_opts else None
        cursors.append((db2 if merge else db).submissions.select(subs_opts, like=True)) if subs_opts else None
        cursors.append((db2 if merge else db).journals.select(jrns_opts, like=True)) if jrns_opts else None
        db.merge(db2, *cursors) if merge else db.copy(db2, *cursors)
        db.commit()
        print("Done")


def database_merge(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database merge <path> [<table1>.<param1>=<value1> ...
                    <tableN>.<paramN>=<valueN>]

    ARGUMENTS
        <path>  Path to second database file
        <table> One of users, submissions, journals
        <param> Search parameter
        <value> Value of the parameter

    DESCRIPTION
        Merge selected entries from a second database to the main database (the one
        opened with the program). To select entries, use the same parameters as the
        search commands precede by a table name. Search parameters can be passed
        multiple times to act as OR values. All columns of the entries table are
        supported. Parameters can be lowercase. If no parameters are passed then all
        the database entries are copied. If submissions entries are selected, their
        files are copied to the files' folder of the main database.

    EXAMPLES
        falocalrepo database merge ~/Documents/FA.backup/A/FA.db users.username=a% \\
            submissions.author=a% journals.author=a%
        falocalrepo database merge ~/Documents/FA2020/FA.db \\
            submissions.date=2020-% journals.date=2020-%
        falocalrepo database merge ~/Documents/FA.backup/FA.db
    """

    database_merge_copy(db, True, *args)


def database_copy(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database copy <path> [<table1>.<param1>=<value1> ...
                    <tableN>.<paramN>=<valueN>]

    ARGUMENTS
        <path>  Path to second database file
        <table> One of users, submissions, journals
        <param> Search parameter
        <value> Value of the parameter

    DESCRIPTION
        Copy selected entries to a new or existing database. To select entries, use
        the same parameters as the search commands precede by a table name. Search
        parameters can be passed multiple times to act as OR values. All columns of
        the entries table are supported. Parameters can be lowercase. If no
        parameters are passed then all the database entries are copied. If
        submissions entries are selected, their files are copied to the files'
        folder of the target database.

    EXAMPLES
        falocalrepo database copy ~/Documents/FA.backup/A/FA.db users.username=a% \\
            submissions.author=a% journals.author=a%
        falocalrepo database copy ~/Documents/FA2020/FA.db submissions.date=2020-% \\
            journals.date=2020-%
        falocalrepo database copy ~/Documents/FA.backup/FA.db
    """

    database_merge_copy(db, False, *args)


def database_clean(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo database clean

    DESCRIPTION
        Clean the database using the SQLite VACUUM function.
    """

    db.vacuum()


@docstring_parameter(__database_version__)
def database_upgrade(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo database upgrade

    DESCRIPTION
        Upgrade the database to the latest version ({0}).
    """

    db.upgrade()


@docstring_parameter(__database_version__)
def database(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo database [<operation> [<param1>=<value1> ... <paramN>=<valueN>]]

    ARGUMENTS
        <operation>         The database operation to execute
        <param>             Parameter for the database operation
        <value>             Value of the parameter

    AVAILABLE COMMANDS
        info                Show database information
        history             Show commands history
        search-users        Search users
        search-submissions  Search submissions
        search-journals     Search journals
        add-user            Add a user to the database manually
        add-submission      Add a submission to the database manually
        add-journal         Add a journal to the database manually
        remove-users        Remove users from database
        remove-submissions  Remove submissions from database
        remove-journals     Remove submissions from database
        server              Start local server to browse database
        merge               Merge with a second database
        copy                Copy entries to a second database
        clean               Clean the database with the VACUUM function
        upgrade             Upgrade the database to the latest version.

    DESCRIPTION
        The database command allows to operate on the database. Calling the database
        command without an operation defaults to 'list'. For more details on tables
        see https://pypi.org/project/falocalrepo-database/{0}.

        All search operations are conducted case-insensitively using the SQLite like
        expression which allows for limited pattern matching. For example this
        expression can be used to search two words together separated by an unknown
        amount of characters '%cat%mouse%'. Fields missing wildcards will only match
        an exact result, i.e. 'cat' will only match a field equal to 'cat' whereas
        '%cat%' wil match a field that contains 'cat'. Bars ('|') can be used to
        isolate individual items in list fields.

        All search operations support the extra 'order', 'limit', and 'offset'
        parameters with values in SQLite 'ORDER BY', 'LIMIT', and 'OFFSET' clause
        formats. The 'order' parameter supports all fields of the searched table.
    """

    check_database_version(db, raise_for_error=comm not in ("", "info", "upgrade"))

    {
        "": database_info,
        "info": database_info,
        "history": database_history,
        "search-users": database_search_users,
        "search-submissions": database_search_submissions,
        "search-journals": database_search_journals,
        "add-user": database_add_user,
        "add-submission": database_add_submission,
        "add-journal": database_add_journal,
        "remove-users": database_remove_users,
        "remove-submissions": database_remove_submissions,
        "remove-journals": database_remove_journals,
        "server": database_server,
        "merge": database_merge,
        "copy": database_copy,
        "clean": database_clean,
        "upgrade": database_upgrade,
    }.get(comm, raiser(UnknownCommand(f"database {comm}")))(db, *args)


@docstring_parameter(__version__, __database_version__, __server_version__, __faapi_version__)
def console(comm: str = "", *args: str) -> None:
    """
    falocalrepo: {0}
    falocalrepo-database: {1}
    falocalrepo-server: {2}
    faapi: {3}

    USAGE
        falocalrepo [-h | -v | -d | -s | -u] [<command> [<operation>] [<arg1> ...
                    <argN>]]

    ARGUMENTS
        <command>       The command to execute
        <operation>     The operation to execute for the given command
        <arg>           The arguments of the command or operation

    GLOBAL OPTIONS
        -h, --help      Display this help message
        -v, --version   Display version
        -d, --database  Display database version
        -s, --server    Display server version
        -u, --updates   Check for updates on PyPi

    AVAILABLE COMMANDS
        help            Display the manual of a command
        init            Create/update the database and exit
        config          Manage settings
        download        Perform downloads
        database        Operate on the database
    """

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
    elif comm in ("-u", "--updates"):
        v = check_update(__version__, "falocalrepo")
        v += check_update(__database_version__, "falocalrepo-database")
        v += check_update(__server_version__, "falocalrepo-server")
        v += check_update(__faapi_version__, "faapi")
        if not v:
            print("No updates available")
        return
    elif comm not in (init.__name__, config.__name__, download.__name__, database.__name__):
        raise UnknownCommand(comm)

    if environ.get("FALOCALREPO_DEBUG", None) is not None:
        print(f"Using FALOCALREPO_DEBUG", file=stderr)

    # Initialise and prepare database
    database_path = "FA.db"

    if db_path := environ.get("FALOCALREPO_DATABASE", None):
        print(f"Using FALOCALREPO_DATABASE: {db_path}", file=stderr)
        database_path = db_path if db_path.endswith(".db") else join(db_path, database_path)

    db: FADatabase = FADatabase(database_path)
    check_database_connections(db)

    try:
        db.settings.add_history(f"{comm} {' '.join(args)}".strip())
        db.commit()

        if comm == init.__name__:
            init(db)
        elif comm == config.__name__:
            config(db, *args)
        elif comm == download.__name__:
            download(db, *args)
        elif comm == database.__name__:
            database(db, *args)
    finally:
        if db is not None:
            db.commit()
            db.close()
