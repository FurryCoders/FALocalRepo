from argparse import ArgumentParser
from argparse import Namespace
from os.path import basename
from os.path import isdir
from shutil import move
from typing import List

from faapi import FAAPI

from .__version__ import __version__
from .database import Connection
from .download import load_cookies
from .download import submission_download
from .settings import cookies_read
from .settings import cookies_write
from .settings import setting_read
from .settings import setting_write


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
            \r    {basename(args[0])} config <setting> [<value1>] ... [<valueN>]
            \r\nARGUMENTS
            \r    <setting>       Setting to read/edit
            \r    <value>         New setting value
            \r\nAVAILABLE SETTINGS
            \r    cookies         Cookies for the API
            \r    files-folder    Files download folder"""


def config(workdir: str, db: Connection, args: List[str]):
    if args[0] == "cookies":
        if not args[1:]:
            cookie_a, cookie_b = cookies_read(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif len(args[1:]) == 2:
            cookie_a: str = args[1]
            cookie_b: str = args[2]
            cookies_write(db, cookie_a, cookie_b)
        else:
            raise Exception("Malformed command: cookies needs two arguments")
    elif args[0] == "files-folder":
        if not args[1:]:
            print("files folder:", setting_read(db, "FILESFOLDER"))
        elif len(args[1:]) == 1:
            folder_old: str = setting_read(db, "FILESFOLDER")
            setting_write(db, "FILESFOLDER", args[1])
            if isdir(folder_old):
                print("Moving files to new location... ", end="", flush=True)
                move(folder_old, args[1])
                print("Done")
        else:
            raise Exception("Malformed command: files-folder needs one argument")
    else:
        raise Exception(f"Unknown setting {args[0]}")


def download(db: Connection, args: List[str]):
    api: FAAPI = FAAPI()
    load_cookies(api, *cookies_read(db))

    if args[0] == "users":
        pass
    elif args[0] == "submissions":
        sub_ids: List[str] = list(filter(len, args[1:]))
        if sub_ids_fail := list(filter(lambda i: not i.isdigit(), sub_ids)):
            print("The following ID's are not correct:", *sub_ids_fail)
        for sub_id in map(int, filter(lambda i: i.isdigit(), sub_ids)):
            print(f"Downloading {sub_id}... ", end="", flush=True)
            submission_download(api, db, sub_id)
            print("Done")


def main_console(workdir: str, db: Connection, args: List[str]):
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
        config(workdir, db, args[2:])
    elif args[1] == "download":
        download(db, args[2:])
    else:
        raise Exception(f"Unknown {args[1]} command.")
