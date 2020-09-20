from os.path import basename
from typing import List
from typing import Union

from .__version__ import __version__

Message = List[Union[str, 'Message']]


def format_help(message: Message, depth: int = 0) -> List[str]:
    formatted_message: List[str] = []

    for item in message:
        if isinstance(item, str):
            formatted_message.append((" " * 4 * depth) + item)
        elif isinstance(item, list):
            formatted_message.extend(format_help(item, depth + 1))

    return formatted_message


def help_message(prog: str, args: List[str] = None) -> str:
    prog = basename(prog)
    args = [] if args is None else args
    message: List[str]

    if len(args) > 1:
        raise Exception(f"Too many arguments to help command.")
    elif not args:
        message = [
            f"{prog} version {__version__}",
            "USAGE",
            [
                f"{prog} [-h] [-v] [-d] <command> [<arg1>] ... [<argN>]"
            ],
            "ARGUMENTS",
            [
                "<command>       The command to execute",
                "<arg>           The arguments of the command"
            ],
            "GLOBAL OPTIONS",
            [
                "-h, --help      Display this help message",
                "-v, --version   Display version",
                "-d, --database  Display database version"
            ],
            "AVAILABLE COMMANDS",
            [
                "help            Display the manual of a command",
                "init            Create the database and exit",
                "config          Manage settings",
                "download        Perform downloads",
                "database        Operate on the database"
            ]
        ]
    elif args[0] == "init":
        message = [
            "USAGE",
            [
                f"{prog} init"
            ]
        ]
    elif args[0] == "config":
        message = [
            "USAGE",
            [
                f"{prog} config [<setting>] [<value1>] ... [<valueN>]"
            ],
            "ARGUMENTS",
            [
                "<setting>       Setting to read/edit",
                "<value>         New setting value"
            ],
            "AVAILABLE SETTINGS",
            [
                "cookies         Cookies for the API",
                "files-folder    Files download folder"
            ]
        ]
    elif args[0] == "download":
        message = [
            "USAGE",
            [
                f"{prog} download <command> [<option>=<value>] [<arg1>] ... [<argN>]"
            ],
            "ARGUMENTS",
            [
                "<command>       The type of download to execute",
                "<arg>           Argument for the download command"
            ],
            "AVAILABLE COMMANDS",
            [
                "users           Download users. First argument is a comma-separated list of",
                "                  users, second is a comma-separated list of folders",
                "submissions     Download single submissions. Arguments are submission ID's",
                "update          Update database using the users and folders already saved"
            ]
        ]
    elif args[0] == "database":
        message = [
            "USAGE",
            [
                f"{prog} database [<operation>] [<param1>=<value1>] ...",
                f"{' ' * len(prog)} [<paramN>=<valueN>]"
            ],
            "ARGUMENTS",
            [
                "<command>          The database operation to execute",
                "<param>            Parameter for the database operation",
                "<value>            Value of the parameter"
            ],
            "AVAILABLE COMMANDS",
            [
                "search-submissions Search submissions",
                "search-journals    Search submissions",
                "add-submission     Add a submission to the database manually",
                "add-journal        Add a journal to the database manually",
                "remove-users       Remove users from database",
                "remove-submissions Remove submissions from database",
                "remove-journals    Remove submissions from database",
                "server             Start local server to browse database",
                "check-errors       Check the database for errors",
                "clean              Clean the database with the VACUUM function"
            ]
        ]
    else:
        raise Exception(f"Unknown {args[0]} command.")

    return "\n".join(format_help(message))
