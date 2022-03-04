from functools import reduce
from pathlib import Path
from random import choice
from typing import Callable
from typing import Type

import faapi
import falocalrepo_database
import falocalrepo_server
from click import BadParameter
from click import Context
from click import Group
from click import Option
from click import Path as PathClick
from click import UsageError
from click import argument
from click import echo
from click import group
from click import option
from click import pass_context
from click.core import ParameterSource
from click.shell_completion import BashComplete
from click.shell_completion import CompletionItem
from click.shell_completion import FishComplete
from click.shell_completion import ShellComplete
from click.shell_completion import ZshComplete
from click.shell_completion import get_completion_class
from falocalrepo_database import Database
from falocalrepo_server import __name__ as __server_name__
from falocalrepo_server import __version__ as __server_version__
from falocalrepo_server import server

from .colors import *
from .config import config_app
from .database import database_app
from .download import download_app
from .util import CompleteChoice
from .util import CustomHelpColorsGroup
from .util import add_history
from .util import check_update
from .util import color_option
from .util import database_exists_option
from .util import database_no_exists_option
from .util import docstring_format
from .util import get_param
from .util import help_option
from .. import __name__ as __prog_name__
from ..__version__ import __version__

# noinspection SpellCheckingInspection
_pride_colors: dict[str, list[tuple[str, str]]] = {
    "pride": [
        *([(bright_red, "\x1b[38;2;229;0;0m")] * 3),
        *([(red, "\x1b[38;2;255;141;0m")] * 3),
        *([(bright_yellow, "\x1b[38;2;255;238;0m")] * 3),
        *([(green, "\x1b[38;2;2;129;33m")] * 3),
        *([(bright_blue, "\x1b[38;2;0;76;255m")] * 3),
        *([(magenta, "\x1b[38;2;119;0;136m")] * 4),
    ],
    "trans": [
        *([(cyan, "\x1b[38;2;91;207;251m")] * 4),
        *([(magenta, "\x1b[38;2;245;171;185m")] * 4),
        *([(bright_white, "\x1b[38;2;255;255;255m")] * 4),
        *([(magenta, "\x1b[38;2;245;171;185m")] * 4),
        *([(cyan, "\x1b[38;2;91;207;251m")] * 4),
    ],
    "bisexual": [
        *([(red, "\x1b[38;2;214;2;112m")] * 7),
        *([(bright_magenta, "\x1b[38;2;155;79;150m")] * 5),
        *([(blue, "\x1b[38;2;0;56;168m")] * 7)
    ],
    "pansexual": [
        *([(magenta, "\x1b[38;2;255;28;141m")] * 7),
        *([(bright_yellow, "\x1b[38;2;255;215;0m")] * 6),
        *([(blue, "\x1b[38;2;26;179;255m")] * 7)
    ],
    "nonbinary": [
        *([(bright_yellow, "\x1b[38;2;252;244;49m")] * 5),
        *([(bright_white, "\x1b[38;2;252;252;252m")] * 5),
        *([(bright_magenta, "\x1b[38;2;157;89;210m")] * 5),
        *([(dim, "\x1b[38;2;40;40;40m")] * 4),
    ],
    "lesbian": [
        *([(red, "\x1b[38;2;214;40;0m")] * 4),
        *([(green, "\x1b[38;2;255;155;86m")] * 4),
        *([(white, "\x1b[38;2;255;255;255m")] * 4),
        *([(magenta, "\x1b[38;2;212;98;166m")] * 4),
        *([(bright_magenta, "\x1b[38;2;164;0;98m")] * 4),
    ],
    "agender": [
        *([(dim, "\x1b[38;2;16;16;16m")] * 2),
        *([(reset, "\x1b[38;2;186;186;186m")] * 3),
        *([(bright_white, "\x1b[38;2;255;255;255m")] * 3),
        *([(green, "\x1b[38;2;186;244;132m")] * 3),
        *([(bright_white, "\x1b[38;2;255;255;255m")] * 3),
        *([(reset, "\x1b[38;2;186;186;186m")] * 3),
        *([(dim, "\x1b[38;2;16;16;16m")] * 2),
    ],
    "asexual": [
        *([(dim, "\x1b[38;2;16;16;16m")] * 5),
        *([(reset, "\x1b[38;2;164;164;164m")] * 5),
        *([(bright_white, "\x1b[38;2;255;255;255m")] * 5),
        *([(blue, "\x1b[38;2;129;0;129m")] * 4),
    ],
    "genderqueer": [
        *([(magenta, "\x1b[38;2;181;127;221m")] * 7),
        *([(bright_white, "\x1b[38;2;255;255;255m")] * 6),
        *([(green, "\x1b[38;2;73;130;30m")] * 7)
    ],
    "genderfluid": [
        *([(magenta, "\x1b[38;2;254;118;226m")] * 4),
        *([(bright_white, "\x1b[38;2;255;255;255m")] * 4),
        *([(bright_magenta, "\x1b[38;2;191;18;215m")] * 4),
        *([(dim, "\x1b[38;2;16;16;16m")] * 4),
        *([(blue, "\x1b[38;2;48;60;190m")] * 4),
    ],
    "aromantic": [
        *([(bright_green, "\x1b[38;2;59;167;64m")] * 4),
        *([(green, "\x1b[38;2;168;212;122m")] * 4),
        *([(bright_white, "\x1b[38;2;255;255;221m")] * 4),
        *([(reset, "\x1b[38;2;171;171;171m")] * 4),
        *([(dim, "\x1b[38;2;16;16;16m")] * 4),
    ],
    "polyamory": [
        *([(bright_blue, "\x1b[38;2;0;0;255m")] * 5),
        *([(bright_red, "\x1b[38;2;255;0;0m")] * 9),
        *([(dim, "\x1b[38;2;16;16;16m")] * 5)
    ]
}


class ShellChoice(CompleteChoice):
    completion_items: list[CompletionItem] = [
        CompletionItem(BashComplete.name, help="The Bourne Again SHell"),
        CompletionItem(FishComplete.name, help="The friendly interactive shell"),
        CompletionItem(ZshComplete.name, help="The Z shell")
    ]


class FlagChoice(CompleteChoice):
    completion_items: list[CompletionItem] = list(map(CompletionItem, _pride_colors.keys()))


def version_callback(ctx: Context, _param: Option, value: str):
    if not value or ctx.resilient_parsing:
        return
    echo(f"{bold}{__prog_name__}{reset} {yellow}{__version__}{reset}", color=ctx.color)
    ctx.exit()


def versions_callback(ctx: Context, _param: Option, value: str):
    if not value or ctx.resilient_parsing:
        return
    echo(f"{bold}{__prog_name__}{reset} {yellow}{__version__}{reset}\n"
         f"{bold}falocalrepo-database{reset} {yellow}{falocalrepo_database.__version__}{reset}\n"
         f"{bold}falocalrepo-server{reset} {yellow}{falocalrepo_server.__version__}{reset}\n"
         f"{bold}faapi{reset} {yellow}{faapi.__version__}{reset}", color=ctx.color)
    ctx.exit()


def port_callback(ctx: Context, param: Option, value: str | int) -> int | None:
    if ctx.get_parameter_source(param.name) == ParameterSource.DEFAULT:
        return None
    elif isinstance(value, str) and not value.lstrip("-").isdigit():
        raise BadParameter(f"{value!r} is not a valid integer.", ctx, param)
    elif (value := int(value)) <= 0:
        raise BadParameter(f"{value!r} is not a valid port.", ctx, param)
    else:
        return int(value)


def commands_completion(ctx: Context, param: Option, incomplete: str) -> list[CompletionItem]:
    try:
        return [
            CompletionItem(n, help=c.short_help)
            for n, c in reduce(lambda a, c: a.commands[c], ctx.params.get(param.name, ctx.args), app).commands.items()
            if n.lower().startswith(incomplete.lower())
        ]
    except (KeyError, AttributeError):
        return []


@group(name=__prog_name__, no_args_is_help=True, cls=CustomHelpColorsGroup, add_help_option=False)
@option("--version", is_flag=True, expose_value=False, is_eager=True, callback=version_callback,
        help="Show version and exit.")
@option("--versions", is_flag=True, expose_value=False, is_eager=True, callback=versions_callback,
        help="Show components' versions and exit.")
@color_option
@help_option
@docstring_format(__prog_name__, __version__)
def app():
    """
    {bold}{0}{reset} {yellow}{1}{reset}

    Pure Python program to download submissions, journals, and user folders from the FurAffinity forum in an easily
    handled database.
    """
    pass


@app.command("init", short_help="Initialise the database.")
@database_no_exists_option
@color_option
@help_option
@pass_context
def app_init(ctx: Context, database: Callable[..., Database]):
    """
    The init command initialises the database. If a database is already present, no operation is performed except for a
    version check.
    """

    db: Database = database(check_init=False, check_version=False)

    if db.settings not in db:
        db.init()
        add_history(db, ctx, version=db.version)
        echo(f"Database initialised (version {yellow}{db.version}{reset})", color=ctx.color)
    else:
        db.close()
        del db
        db = database(print_envvar=False)
        echo(f"Database ready (version {yellow}{db.version}{reset})", color=ctx.color)


@app.command("updates", short_help="Check for updates to components.")
@option("--shell", is_flag=True, help="Print shell command to upgrade components.")
@color_option
@help_option
@option("--database", expose_value=False, required=False, hidden=True)
@pass_context
@docstring_format()
def app_updates(ctx: Context, shell: bool):
    """
    Check for updates to falocalrepo and its main dependencies on PyPi. The {yellow}shell{reset} option can be used to
    output the shell command to upgrade any component that has available updates.
    """

    packages: list[tuple[str, str]] = [
        (__version__, __prog_name__),
        (falocalrepo_database.__version__, falocalrepo_database.__name__),
        (falocalrepo_server.__version__, falocalrepo_server.__name__),
        (faapi.__version__, faapi.__name__)
    ]
    updates: list[tuple[str, str, str]] = [
        (current, latest, package)
        for [current, package] in packages
        if (latest := check_update(current, package))
    ]

    if shell:
        if updates:
            echo(f"pip install --upgrade {' '.join(package for [*_, package] in updates)}")
        return

    for [current, latest, package] in updates:
        echo(f"New {bold}{package}{reset} version available: "
             f"{yellow}{latest}{reset} (current {yellow}{current}{reset})", color=ctx.color)
    if not updates:
        echo("No updates available")


@app.command("help", context_settings={"ignore_unknown_options": True})
@argument("commands", nargs=-1, required=False, type=str, callback=lambda _c, _p, v: list(v),
          shell_complete=commands_completion)
@color_option
@help_option
@option("--database", expose_value=False, required=False, hidden=True)
@pass_context
def app_help(ctx: Context, commands: list[str]):
    """
    Show the help for a command.
    """

    try:
        commands = [c for c in commands if not c.startswith("-")]
        command = reduce(lambda a, c: a.commands[c] if isinstance(a, Group) else a, commands, app)
        echo(command.get_help(app.make_context(command.name, commands, ctx.parent)), color=ctx.color)
    except (KeyError, AttributeError):
        raise UsageError(f"No such command {' '.join(commands)!r}.", ctx)


@app.command("completions", short_help="Generate tab-completion scripts.")
@argument("shell", type=ShellChoice(), callback=lambda _c, _p, v: get_completion_class(v))
@option("--alias", type=str, metavar="NAME", default=None, help="Alternate program name for completion script.")
@color_option
@help_option
@option("--database", expose_value=False, required=False, hidden=True)
@pass_context
@docstring_format("\n    ".join(f" * {s.value}\t{s.help}" for s in ShellChoice.completion_items))
def app_completions(ctx: Context, shell: Type[ShellComplete], alias: str | None):
    """
    Generate tab-completion scripts for your shell. The generated completion must be saved in the correct location for
    it to be recognized and used by the shell.

    \b
    Supported shells are:
    {0}
    """

    echo(shell((prog := ctx.find_root()).command, {}, prog_name := alias or prog.info_name,
               f"_{prog_name.replace('-', '_').upper()}_COMPLETE").source())


# noinspection HttpUrlsUsage
@app.command("server", short_help="Start a server to browse the database.")
@option("--host", metavar="HOST", type=str, default="0.0.0.0", show_default=True, help="Server host.")
@option("--port", metavar="PORT", type=str, default="80, 443", show_default=True, callback=port_callback,
        help="Server port.")
@option("--ssl-cert", type=PathClick(exists=True, dir_okay=False, path_type=Path), default=None,
        help="Path to SSL certificate file for HTTPS")
@option("--ssl-key", type=PathClick(exists=True, dir_okay=False, path_type=Path), default=None,
        help="Path to SSL key file for HTTPS")
@option("--redirect-http", metavar="PORT2", type=int, default=None, callback=port_callback,
        help=f"Redirect all traffic from http://HOST:{yellow}PORT{reset} to https://HOST:{yellow}PORT2{reset}")
@option("--auth", metavar="USERNAME:PASSWORD", type=str, default=None,
        help=f"Enable HTTP Basic authentication.")
@option("--precache", is_flag=True, default=False, help="Cache tables on startup.")
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format(server_name=__server_name__, server_version=__server_version__)
def app_server(ctx: Context, database: Callable[..., Database], host: str | None, port: int | None,
               ssl_cert: Path | None, ssl_key: Path | None, redirect_http: int | None, auth: str | None,
               precache: bool):
    """
    Start a server at {yellow}HOST{reset}:{yellow}PORT{reset} to navigate the database. The {yellow}--ssl-cert{reset}
    and {yellow}--ssl-cert{reset} allow serving with HTTPS. Setting {yellow}--redirect-http{reset} starts the server in
    HTTP to HTTPS redirection mode. For more details on usage see
    {blue}https://pypi.org/project/{server_name}/{server_version}{reset}.
    """

    if ssl_cert and not ssl_key:
        raise BadParameter(f"'--ssl-cert' and '--ssl-key' must be set together.", ctx, get_param(ctx, "ssl_key"))
    elif ssl_key and not ssl_cert:
        raise BadParameter(f"'--ssl-cert' and '--ssl-key' must be set together.", ctx, get_param(ctx, 'ssl_cert'))

    db: Database = database()
    db_path: Path = db.path
    db.close()
    del db

    server(db_path, host=host, port=port, ssl_cert=ssl_cert, ssl_key=ssl_key, redirect_port=redirect_http,
           precache=precache, authentication=auth)


@app.command("paw", short_help="Print the PRIDE paw!")
@argument("flag", type=str, default="pride", required=False, shell_complete=FlagChoice().shell_complete)
@option("--truecolor / --8bit-color", is_flag=True, default=supports_truecolor, show_default=True,
        help="Force enable color mode.")
@color_option
@help_option
@pass_context
@docstring_format("\n    ".join(
    f"* {_pride_colors['pride'][(i % ((len(_pride_colors[f]) - 1) // 3)) * 3][supports_truecolor]}{f}{reset}"
    for i, f in enumerate(_pride_colors.keys())))
def paw(ctx: Context, flag: str, truecolor: bool):
    """
    Print a PRIDE {yellow}FLAG{reset} paw!

    If used inside a truecolor-supporting terminal, the full 24bit color range will be used for the most colorful flags!

    truecolor/8bit color modes can be forcefully enabled using the {yellow}--truecolor{reset} and
    {yellow}--8bit-color{reset} options.

    \b
    {0}

    {italic}Note{reset}: the paw works best with a dark background.
    """
    if flag not in _pride_colors:
        flag = choice(list(_pride_colors.keys()))
        echo("Your flag isn't in the program yet :(\n"
             f"In the meantime, hope you enjoy the {flag} flag :)\n")

    paw_ascii = """
                            -*#%%#=               
                :=++=.    :%@@@@@@@*              
              -%@@@@@@+  :@@@@@@@@@@.             
             =@@@@@@@@@- #@@@@@@@@@%              
            .@@@@@@@@@@- =@@@@@@@@%.              
            .@@@@@@@@@#   =%@@@@#=  -*%@@@%#=     
             =@@@@@@@=   ...:..   :%@@@@@@@@@*    
               -++=-.:+%@@@@%*:  :@@@@@@@@@@@#    
          :-+++==++#@@@@@@@@@@@* -@@@@@@@@@@%.    
        :%@@@@@@@@@@@@@@@@@@@@@@- =%@@@@@@#=      
        @@@@@@@@@@@@@@@@@@@@@@@@:   .:-:.         
        +@@@@@@@@@@@@@@@@@@@@@@=  :=+**+-.        
         -#@@@@@@@@@@@@@@@@@@@- +%@@@@@@@@+       
           .=%@@@@@@@@@@@@@@@+ #@@@@@@@@@@@.      
              -#@@@@@@@@@@@@@..@@@@@@@@@@@#       
                :#@@@@@@@@@@@: +@@@@@@@@%=        
                  =@@@@@@@@@@.  .-++++-.          
                   .#@@@@@@@*                     
                     -*%@@#=                      
    """.strip("\n").rstrip()

    paw_ascii = "\n".join(line.ljust(max(map(len, paw_ascii.splitlines()))) for line in paw_ascii.splitlines())
    paw_ascii = "\n".join(bold + c[truecolor] + l + reset for c, l in zip(_pride_colors[flag], paw_ascii.splitlines()))
    echo(paw_ascii, color=ctx.color)


app.add_command(config_app, config_app.name)
app.add_command(download_app, download_app.name)
app.add_command(database_app, database_app.name)
app.list_commands = lambda *_: [
    app_init.name,
    config_app.name,
    database_app.name,
    download_app.name,
    app_server.name,
    app_completions.name,
    app_updates.name,
    app_help.name,
    paw.name,
]
