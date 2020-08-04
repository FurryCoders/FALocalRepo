from os.path import basename
from os.path import isdir
from shutil import move
from typing import List

from .__version__ import __version__
from .database import Connection
from .settings import cookies_change
from .settings import cookies_load
from .settings import setting_read
from .settings import setting_write


def help_message(args: List[str]) -> str:
    if not args[1:] or (args[1] == "help" and not args[2:]):
        return "\n".join([
            f"{basename(args[0])} version {__version__}\n",
            "\nUSAGE",
            f"    {basename(args[0])} <command> [<arg1>] ... [<argN>]",
            "\nARGUMENTS",
            "    <command>   The command to execute",
            "    <arg>       The arguments of the command",
            "\nAVAILABLE COMMANDS",
            "    help        Show this help message",
            "    interactive Run in interactive mode",
            "    config      Manage settings",
        ])
    if args[2] == "config":
        return "\n".join([
            "USAGE",
            f"    {basename(args[0])} config <setting> [<value1>] ... [<valueN>]",
            "\nARGUMENTS",
            "    <setting>       Setting to read/edit",
            "    <value>         New setting value",
            "\nAVAILABLE SETTINGS",
            "    cookies         Cookies for the API",
            "    files-folder    Files download folder",
        ])


def config(workdir: str, db: Connection, args: List[str]):
    if args[0] == "cookies":
        if not args[1:]:
            cookie_a, cookie_b = cookies_load(db)
            print("cookie a:", cookie_a)
            print("cookie b:", cookie_b)
        elif len(args[1:]) == 2:
            cookie_a: str = args[1]
            cookie_b: str = args[2]
            cookies_change(db, cookie_a, cookie_b)
        else:
            raise Exception("Malformed command: cookies needs two arguments")
    elif args[0] == "files-folder":
        if not args[1:]:
            print("files folder:", setting_read(db, "FILESLOCATION"))
        elif len(args[1:]) == 1:
            folder_old: str = setting_read(db, "FILESLOCATION")
            setting_write(db, "FILESLOCATION", args[1])
            if isdir(folder_old):
                print("Moving files to new location... ", end="", flush=True)
                move(folder_old, args[1])
                print("Done")
        else:
            raise Exception("Malformed command: files-folder needs one argument")
    else:
        raise Exception(f"Unknown setting {args[0]}")


def main_console(workdir: str, db: Connection, args: List[str]):
    if not args or args[1] == "help":
        print(help_message(args))
    elif args[1] == "config":
        config(workdir, db, args[2:])
    else:
        raise Exception(f"Unknown {args[1]} command.")
