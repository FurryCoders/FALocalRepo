from argparse import ArgumentParser
from argparse import Namespace
from os.path import basename
from typing import List

from faapi import FAAPI

from .__version__ import __version__
from .commands import download_submissions
from .commands import download_users
from .commands import files_folder_move
from .commands import update_users
from .database import Connection
from .download import load_cookies
from .settings import cookies_read
from .settings import cookies_write
from .settings import setting_read


def help_message(args: List[str]) -> str:
    if not args[1:] or (args[1] == "help" and not args[2:]):
        return f"""{basename(args[0])} version {__version__}
            \r\nUSAGE
            \r    {basename(args[0])} [-h] [-v] <command> [<arg1>] ... [<argN>]
            \r\nARGUMENTS
            \r    <command>       The command to execute
            \r    <arg>           The arguments of the command
            \r\nGLOBAL OPTIONS
            \r    -h, --help      Display this help message
            \r    -v, --version   Display version
            \r\nAVAILABLE COMMANDS"
            \r    help            Display the manual of a command
            \r    interactive     Run in interactive mode
            \r    config          Manage settings"""
    if args[2] == "config":
        return f"""USAGE
            \r    {basename(args[0])} config [<setting>] [<value1>] ... [<valueN>]
            \r\nARGUMENTS
            \r    <setting>       Setting to read/edit
            \r    <value>         New setting value
            \r\nAVAILABLE SETTINGS
            \r    cookies         Cookies for the API
            \r    files-folder    Files download folder"""


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
        raise Exception("Malformed command: database needs a command")
    elif args[0] == "update":
        update_users(api, db)
    elif args[0] == "users":
        if len(args[1:3]) != 2:
            raise Exception("Malformed command: users needs two arguments")
        users: List[str] = list(map(lambda s: s.strip(), args[1].split(",")))
        folders: List[str] = list(map(lambda s: s.strip(), args[2].split(",")))
        download_users(api, db, users, folders)
    elif args[0] == "submissions":
        if not args[1:]:
            raise Exception("Malformed command: submissions needs at least one argument")
        sub_ids: List[str] = list(filter(len, args[1:]))
        download_submissions(api, db, sub_ids)
    else:
        raise Exception(f"Unknown download command {args[0]}")


def main_console(db: Connection, args: List[str]):
    args_parser: ArgumentParser = ArgumentParser(add_help=False)
    args_parser.add_argument("-h, --help", dest="help", action="store_true", default=False)
    args_parser.add_argument("-v, --version", dest="version", action="store_true", default=False)

    global_options: List[str] = [arg for arg in args[1:] if arg.startswith("-")]
    args_parsed: Namespace = args_parser.parse_args(global_options)

    if args_parsed.help:
        print(help_message([args[0], "help"]))
    elif args_parsed.version:
        print(__version__)
    elif not args or args[1] == "help":
        print(help_message(args))
    elif args[1] == "config":
        config(db, args[2:])
    elif args[1] == "download":
        download(db, args[2:])
    else:
        raise Exception(f"Unknown {args[1]} command.")
