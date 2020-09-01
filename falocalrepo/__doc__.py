from os.path import basename
from typing import List

from .__version__ import __database_version__
from .__version__ import __version__


def help_message(prog: str, args: List[str] = None) -> str:
    args = [] if args is None else args

    if len(args) > 1:
        raise Exception(f"Too many arguments to help command.")
    elif not args:
        return f"""{basename(prog)} version {__version__}
            \r{basename(prog)} database version {__database_version__}
            \r\nUSAGE
            \r    {basename(prog)} [-h] [-v] [-d] <command> [<arg1>] ... [<argN>]
            \r\nARGUMENTS
            \r    <command>       The command to execute
            \r    <arg>           The arguments of the command
            \r\nGLOBAL OPTIONS
            \r    -h, --help      Display this help message
            \r    -v, --version   Display version
            \r    -d, --database  Display database version
            \r\nAVAILABLE COMMANDS
            \r    help            Display the manual of a command
            \r    init            Create the database and exit
            \r    config          Manage settings
            \r    download        Perform downloads
            \r    database        Operate on the database"""
    elif args[0] == "init":
        return f"""USAGE
            \r    {basename(prog)} init"""
    elif args[0] == "config":
        return f"""USAGE
            \r    {basename(prog)} config [<setting>] [<value1>] ... [<valueN>]
            \r\nARGUMENTS
            \r    <setting>       Setting to read/edit
            \r    <value>         New setting value
            \r\nAVAILABLE SETTINGS
            \r    cookies         Cookies for the API
            \r    files-folder    Files download folder"""
    elif args[0] == "download":
        return f"""USAGE
            \r    {basename(prog)} download <command> [<option>=<value>] [<arg1>] ... [<argN>]
            \r\nARGUMENTS
            \r    <command>       The type of download to execute
            \r    <arg>           Argument for the download command
            \r\nAVAILABLE COMMANDS
            \r    users           Download users. First argument is a comma-separated list of
            \r                      users, second is a comma-separated list of folders
            \r    submissions     Download single submissions. Arguments are submission ID's
            \r    update          Update database using the users and folders already saved"""
    elif args[0] == "database":
        return f"""USAGE
            \r    {basename(prog)} database [<operation>] [<param1>=<value1>] ... [<paramN>=<valueN>]
            \r\nARGUMENTS
            \r    <command>          The database operation to execute
            \r    <param>            Parameter for the database operation
            \r    <value>            Value of the parameter
            \r\nAVAILABLE COMMANDS
            \r    search-submissions Search submissions
            \r    search-journals    Search submissions
            \r    add-submission     Add a submission to the database manually     
            \r    add-journal        Add a journal to the database manually     
            \r    remove-users       Remove users from database
            \r    remove-submissions Remove submissions from database
            \r    remove-journals    Remove submissions from database
            \r    check-errors       Check the database for errors
            \r    clean              Clean the database with the VACUUM function"""
    else:
        raise Exception(f"Unknown {args[0]} command.")
