from functools import partial
from json import dumps
from json import loads
from os import environ
from pathlib import Path
from sys import stderr
from typing import Callable
from typing import TextIO

from click import BadParameter
from click import Choice
from click import Context
from click import Option
from click import Parameter
from click import Path as PathClick
from click import echo
from click import help_option as help_option_click
from click import option
from click.core import ParameterSource
from click.shell_completion import CompletionItem
from click_help_colors import HelpColorsGroup
from faapi import FAAPI
from faapi.exceptions import Unauthorized
from falocalrepo_database import Database
from requests import Response
from requests import get

from .colors import *
from .. import __name__ as __prog_name__

__prog_name__ = __prog_name__.split('/')[-1].split('\\')[-1].strip().upper()
_envar_database: str = f"{__prog_name__}_DATABASE"
_envar_no_color: str = f"{__prog_name__}_NOCOLOR"
_envar_multi_connection: str = f"{__prog_name__}_MULTI_CONNECTION"
_cookies_setting: str = "COOKIES"
_help_option_names: list[str] = ["--help", "-h"]


def database_callback(ctx: Context, param: Option, value: Path) -> Callable[..., Database]:
    return partial(open_database, value, ctx=ctx, param=param)


def color_callback(ctx: Context, param: Option, value: bool) -> bool:
    if (src := ctx.get_parameter_source(param.name)) == ParameterSource.COMMANDLINE:
        ctx.color = value
    elif ctx.color is None and src == ParameterSource.ENVIRONMENT:
        EnvVars.print_nocolor()
        ctx.color = value = False
    return value


database_exists_option = option("--database", default=Path("FA.db"), help="Database file.", envvar=_envar_database,
                                show_envvar=True, callback=database_callback,
                                type=PathClick(exists=True, dir_okay=False, writable=True, resolve_path=True,
                                               path_type=Path))
database_no_exists_option = option("--database", default=Path("FA.db"), help="Database file.", envvar=_envar_database,
                                   show_envvar=True, callback=database_callback,
                                   type=PathClick(dir_okay=False, writable=True, resolve_path=True, path_type=Path))
color_option = option("--color/--no-color", is_flag=True, is_eager=True, default=None, expose_value=False,
                      callback=color_callback, envvar=_envar_no_color, help="Toggle ANSI colors.")
help_option = help_option_click(*_help_option_names, is_eager=True, help="Show help message and exit.")


def open_database(path: Path, *, ctx: Context, param: Parameter, check_init: bool = True,
                  check_version: bool = True, print_envvar: bool = True) -> Database:
    if print_envvar and ctx.get_parameter_source(param.name) == ParameterSource.ENVIRONMENT:
        EnvVars.print_database()
    if EnvVars.MULTI_CONNECTION:
        if print_envvar:
            EnvVars.print_multi_connection()
    elif path.is_file and (ps := Database.check_connection(path, raise_for_error=False)):
        raise BadParameter(f"Multiple connections to database {str(path)!r}: {ps}", ctx, param)

    db: Database = Database(path, check_version=False, check_connections=False)

    if check_init and not db.is_formatted:
        from .app import app, app_init
        raise BadParameter(f"Database is not initialised.\n\nInitialise using '{app.name} {app_init.name}'.",
                           ctx, param)
    elif check_version and (version_error := db.check_version(raise_for_error=False)):
        from .app import app
        from .database import database_app, database_upgrade
        raise BadParameter(" ".join(version_error.args) +
                           f"\n\nUpgrade with '{app.name} {database_app.name} {database_upgrade.name}'.",
                           ctx, param)

    return db


def open_api(db: Database) -> FAAPI:
    if not (cookies := read_cookies(db)):
        raise Unauthorized("No cookies")

    return FAAPI(cookies)


class CustomHelpColorsGroup(HelpColorsGroup):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"


class EnvVars:
    DATABASE: Path | None = Path(p) if (p := environ.get(_envar_database, None)) is not None else None
    NOCOLOR: bool = environ.get(_envar_no_color, None) is not None
    MULTI_CONNECTION: bool = environ.get(_envar_multi_connection, None) is not None

    @classmethod
    def print_database(cls, file: TextIO = stderr):
        if cls.DATABASE:
            echo(f"Using {_envar_database}: {cls.DATABASE}", file=file)

    @classmethod
    def print_nocolor(cls, file: TextIO = stderr):
        if cls.NOCOLOR:
            echo(f"Using {_envar_no_color}", file=file)

    @classmethod
    def print_multi_connection(cls, file: TextIO = stderr):
        if cls.MULTI_CONNECTION:
            echo(f"Using {_envar_multi_connection}", file=file)


class CompleteChoice(Choice):
    completion_items: list[CompletionItem] = []

    def __init__(self):
        super(CompleteChoice, self).__init__([c.value for c in self.completion_items], False)

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> list[CompletionItem]:
        return [i for i in self.completion_items if i.value.lower().startswith(incomplete.lower())]


def read_cookies(db: Database) -> list[dict[str, str]]:
    if not (cs := db.settings[_cookies_setting]):
        return []
    return [{"name": n, "value": v} for n, v in loads(cs).items()]


def write_cookies(db: Database, cookies: dict[str, str]):
    db.settings[_cookies_setting] = dumps(cookies)
    db.commit()


def docstring_format(*args, **kwargs):
    def inner(obj: {__doc__}) -> {__doc__}:
        obj.__doc__ = (obj.__doc__ or "").format(*args, **colors_dict, **kwargs)
        return obj

    return inner


def check_update(version: str, package: str) -> str | None:
    res: Response = get(f"https://pypi.org/pypi/{package}/json")
    res.raise_for_status()
    return latest if (latest := res.json()["info"]["version"]) and latest != version else None


def add_history(db: Database, ctx: Context, **kwargs):
    root, parent, comm = ctx.find_root().command, ctx.parent.command, ctx.command
    db.history.add_event((f"{parent.name} {comm.name}" if root != parent else comm.name) + " " +
                         " ".join(f"{k}={v}" for k, v in kwargs.items()))
    db.commit()
