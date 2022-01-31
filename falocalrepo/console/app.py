from pathlib import Path
from random import choice
from typing import Callable
from typing import Type

import faapi
import falocalrepo_database
import falocalrepo_server
from click import BadParameter
from click import Command
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

try:
    from supports_color import supportsColor

    _supports_truecolor: bool = getattr(supportsColor.stdout, "has16m", False)
except TypeError:
    _supports_truecolor: bool = False

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
from .util import help_option
from .. import __name__ as __prog_name__
from ..__version__ import __version__

_pride_flags: list[str] = [
    "pride", "trans", "bisexual", "pansexual", "nonbinary",
    "lesbian", "agender", "asexual", "genderqueer",
    "genderfluid", "aromantic", "polyamory"
]
_pride_colors: list[str] = [
    hex_to_ansi("E50000"), hex_to_ansi("FF8D00"), hex_to_ansi("FFEE00"),
    hex_to_ansi("028121"), hex_to_ansi("004CFF"), hex_to_ansi("770088"),
] if _supports_truecolor else [
    bright_red, red, bright_yellow, green, bright_blue, magenta
]


# noinspection SpellCheckingInspection
def _pride_colors_8bit(flag: str) -> list[str] | None:
    if flag == "pride":
        return [
            *([bright_red] * 3),
            *([red] * 3),
            *([bright_yellow] * 3),
            *([green] * 3),
            *([bright_blue] * 3),
            *([magenta] * 4),
        ]
    elif flag == "trans":
        return [
            *([cyan] * 4),
            *([magenta] * 4),
            *([bright_white] * 4),
            *([magenta] * 4),
            *([cyan] * 4),
        ]
    elif flag == "bisexual":
        return [
            *([red] * 7),
            *([bright_magenta] * 5),
            *([blue] * 7)
        ]
    elif flag == "pansexual":
        return [
            *([magenta] * 7),
            *([bright_yellow] * 6),
            *([blue] * 7)
        ]
    elif flag == "nonbinary":
        return [
            *([bright_yellow] * 5),
            *([bright_white] * 5),
            *([bright_magenta] * 5),
            *([dim] * 4),
        ]
    elif flag == "lesbian":
        return [
            *([red] * 4),
            *([green] * 4),
            *([white] * 4),
            *([magenta] * 4),
            *([bright_magenta] * 4),
        ]
    elif flag == "agender":
        return [
            *([dim] * 2),
            *([reset + white] * 3),
            *([bright_white] * 3),
            *([green] * 3),
            *([bright_white] * 3),
            *([reset + white] * 3),
            *([dim] * 2),
        ]
    elif flag == "asexual":
        return [
            *([dim] * 5),
            *([reset + white] * 5),
            *([bright_white] * 5),
            *([blue] * 4),
        ]
    elif flag == "genderqueer":
        return [
            *([magenta] * 7),
            *([bright_white] * 6),
            *([green] * 7)
        ]
    elif flag == "genderfluid":
        return [
            *([magenta] * 4),
            *([bright_white] * 4),
            *([bright_magenta] * 4),
            *([dim] * 4),
            *([blue] * 4),
        ]
    elif flag == "aromantic":
        return [
            *([bright_green] * 4),
            *([green] * 4),
            *([bright_white] * 4),
            *([reset + white] * 4),
            *([dim + dim] * 4),
        ]
    elif flag == "polyamory":
        return [
            *([bright_blue] * 5),
            *([bright_red] * 9),
            *([dim] * 5)
        ]
    else:
        return None


# noinspection SpellCheckingInspection
def _pride_colors_24bit(flag: str) -> list[str] | None:
    if flag == "pride":
        return [
            *(["E50000"] * 3),
            *(["FF8D00"] * 3),
            *(["FFEE00"] * 3),
            *(["028121"] * 3),
            *(["004CFF"] * 3),
            *(["770088"] * 4),
        ]
    elif flag == "trans":
        return [
            *(["5BCFFB"] * 4),
            *(["F5ABB9"] * 4),
            *(["FFFFFF"] * 4),
            *(["F5ABB9"] * 4),
            *(["5BCFFB"] * 4),
        ]
    elif flag == "bisexual":
        return [
            *(["D60270"] * 7),
            *(["9B4F96"] * 5),
            *(["0038A8"] * 7)
        ]
    elif flag == "pansexual":
        return [
            *(["FF1C8D"] * 7),
            *(["FFD700"] * 6),
            *(["1AB3FF"] * 7)
        ]
    elif flag == "nonbinary":
        return [
            *(["FCF431"] * 5),
            *(["FCFCFC"] * 5),
            *(["9D59D2"] * 5),
            *(["282828"] * 4),
        ]
    elif flag == "lesbian":
        return [
            *(["D62800"] * 4),
            *(["FF9B56"] * 4),
            *(["FFFFFF"] * 4),
            *(["D462A6"] * 4),
            *(["A40062"] * 4),
        ]
    elif flag == "agender":
        return [
            *(["101010"] * 2),
            *(["BABABA"] * 3),
            *(["FFFFFF"] * 3),
            *(["BAF484"] * 3),
            *(["FFFFFF"] * 3),
            *(["BABABA"] * 3),
            *(["101010"] * 2),
        ]
    elif flag == "asexual":
        return [
            *(["101010"] * 5),
            *(["A4A4A4"] * 5),
            *(["FFFFFF"] * 5),
            *(["810081"] * 4),
        ]
    elif flag == "genderqueer":
        return [
            *(["B57FDD"] * 7),
            *(["FFFFFF"] * 6),
            *(["49821E"] * 7)
        ]
    elif flag == "genderfluid":
        return [
            *(["FE76E2"] * 4),
            *(["FFFFFF"] * 4),
            *(["BF12D7"] * 4),
            *(["101010"] * 4),
            *(["303CBE"] * 4),
        ]
    elif flag == "aromantic":
        return [
            *(["3BA740"] * 4),
            *(["A8D47A"] * 4),
            *(["FFFFDD"] * 4),
            *(["ABABAB"] * 4),
            *(["101010"] * 4),
        ]
    elif flag == "polyamory":
        return [
            *(["0000FF"] * 5),
            *(["FF0000"] * 9),
            *(["101010"] * 5)
        ]
    else:
        return None


class ShellChoice(CompleteChoice):
    completion_items: list[CompletionItem] = [
        CompletionItem(BashComplete.name, help="The Bourne Again SHell"),
        CompletionItem(FishComplete.name, help="The friendly interactive shell"),
        CompletionItem(ZshComplete.name, help="The Z shell")
    ]


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
@argument("commands", nargs=-1, required=False, type=str, callback=lambda _c, _p, v: list(v))
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
        context: Context = ctx.parent
        command: Group | Command = app
        for i, command_name in enumerate(commands, 1):
            command = command.get_command(context, command_name)
            context = command.make_context(command.name,
                                           commands[i:i + 1] if isinstance(command, Group) else [],
                                           context)
        echo(command.get_help(context), color=ctx.color)
    except (KeyError, AttributeError, UsageError):
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
        raise BadParameter(f"'--ssl-cert' and '--ssl-key' must be set together.", ctx,
                           next(_p for _p in ctx.command.params if _p.name == 'ssl_key'))
    elif ssl_key and not ssl_cert:
        raise BadParameter(f"'--ssl-cert' and '--ssl-key' must be set together.", ctx,
                           next(_p for _p in ctx.command.params if _p.name == 'ssl_cert'))

    db: Database = database()
    db_path: Path = db.path
    db.close()
    del db

    server(db_path, host=host, port=port, ssl_cert=ssl_cert, ssl_key=ssl_key, redirect_port=redirect_http,
           precache=precache, authentication=auth)


@app.command("paw", short_help="Print the PRIDE paw!")
@argument("flag", type=str, default="pride", required=False)
@option("--true-color / --8bit-color", is_flag=True, default=_supports_truecolor, show_default=True,
        help="Force enable color mode.")
@color_option
@help_option
@pass_context
@docstring_format("\n    ".join(f"* {_pride_colors[i % len(_pride_colors)]}{f}{reset}"
                                for i, f in enumerate(_pride_flags)))
def paw(ctx: Context, flag: str, true_color: bool):
    """
    Print a PRIDE {yellow}FLAG{reset} paw!

    If used inside a truecolor-supporting terminal, the full 24bit color range will be used for the most colorful flags!

    truecolor/8bit color modes can be forcefully enabled using the {yellow}--true-color{reset}
    and {yellow}--8bit-color{reset} options.

    \b
    {0}

    {italic}Note{reset}: the paw works best with a dark background.
    """
    if flag not in _pride_flags:
        flag = choice(_pride_flags)
        echo("Your flag isn't in the program yet :(\n"
             f"In the meantime, hope you enjoy the {flag} flag :)\n")

    colors: list[str] = list(map(hex_to_ansi, _pride_colors_24bit(flag))) if true_color else _pride_colors_8bit(flag)

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
    """.removeprefix("\n").removesuffix("\n")

    paw_ascii = "\n".join(line.ljust(46) for line in paw_ascii.splitlines())
    paw_ascii = "\n".join(bold + color + line + reset for color, line in zip(colors, paw_ascii.splitlines()))
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
