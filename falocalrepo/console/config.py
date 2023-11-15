from json import dumps
from json import loads
from math import ceil
from math import log10
from os import makedirs
from pathlib import Path
from shutil import copy2
from shutil import get_terminal_size
from typing import Callable

from click import Choice
from click import Context
from click import Path as PathClick
from click import UsageError
from click import argument
from click import echo
from click import group
from click import option
from click import pass_context
from falocalrepo_database import Cursor
from falocalrepo_database import Database
from falocalrepo_database.tables import SubmissionsColumns

from .colors import *
from .util import CustomHelpColorsGroup
from .util import add_history
from .util import backup_database
from .util import color_option
from .util import database_exists_option
from .util import docstring_format
from .util import help_option
from .util import read_cookies
from .util import write_cookies


def move_submission_file(file: Path, old_folder: Path, new_folder: Path):
    file_no_root: Path = Path(str(file).removeprefix(str(old_folder)))
    new_file: Path = new_folder / str(file_no_root).removeprefix(file_no_root.anchor)
    try:
        makedirs(new_file.parent, exist_ok=True)
        new_file.unlink(missing_ok=True)
        copy2(file, new_file)
        file.unlink(missing_ok=True)
    except BaseException:
        new_file.unlink(missing_ok=True)
        raise


@group("config", cls=CustomHelpColorsGroup, no_args_is_help=True, short_help="Change settings.")
@color_option
@help_option
def config_app():
    """
    The config command allows reading and changing the settings used by the program.
    """
    pass


@config_app.command("list", short_help="List settings.")
@database_exists_option
@color_option
@help_option
def config_list(database: Callable[..., Database]):
    """
    Show a list of all stored settings.
    """

    db: Database = database()
    config_files_folder.callback(database=lambda: db, new_folder=None, move=False)
    echo()
    config_cookies.callback(database=lambda: db, cookie=[])
    echo()
    config_backup.callback(database=lambda: db, date_format=None, trigger=None, folder=None, remove=False)


@config_app.command("backup", short_help="Configure backup settings.")
@argument("trigger", type=Choice(["download", "database", "config", "predownload", "predatabase", "preconfig"]),
          required=False, default=None)
@option("--date-format", type=str, metavar="FMT", default="%Y %W", show_default=True,
        help="Set a date format for the trigger.")
@option("--folder", type=PathClick(file_okay=False, writable=True, path_type=Path), default=None,
        help="Set backup folder.")
@option("--remove", is_flag=True, default=False, help="Remove a trigger.")
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def config_backup(ctx: Context, database: Callable[..., Database], trigger: str | None, date_format: str,
                  folder: Path | None, remove: bool):
    """
    Read or modify automatic backup settings. Backup will be performed automatically based on stored triggers and date
    formats. The date format {yellow}FMT{reset} supports the standard C {italic}strftime{reset} codes, and it defaults
    to {cyan}%Y %W{reset} (year and week).

    To set the backup folder, use the {yellow}--folder{reset} option.

    To remove a trigger from the settings, use the {yellow}--remove{reset} option.

    \b
    {cyan}Triggers{reset}
    * download     backup after performing download operations
    * database     backup after editing the database
    * config       backup after changing settings
    * predownload  backup before performing download operations
    * predatabase  backup before editing the database
    * preconfig    backup before changing settings
    """

    if remove and trigger is None:
        raise UsageError("--remove option requires a trigger.", ctx)

    db: Database = database()
    backup_settings: dict[str, str] = loads(bs) if (bs := db.settings["BACKUPSETTINGS"]) else {}

    if folder or remove or trigger:
        backup_database(db, ctx, "preconfig")

    echo(f"{bold}Backup{reset}")

    if folder:
        db.settings.backup_folder = folder
        db.commit()

    if remove:
        backup_settings = {t: f for t, f in backup_settings.items() if t != trigger}
        db.settings["BACKUPSETTINGS"] = dumps(backup_settings, separators=(",", ":"))
        db.commit()
    elif trigger:
        backup_settings |= {trigger: date_format}
        db.settings["BACKUPSETTINGS"] = dumps(backup_settings, separators=(",", ":"))
        db.commit()

    if bf := db.settings[db.settings.backup_folder_setting]:
        bfp: Path = Path(bf)
        echo(f"{blue}Folder{reset}: {yellow}{bfp}{reset}"
             f" ({yellow}{db.path.parent / bfp}{reset})" if not bfp.is_absolute() else "")
    else:
        echo(f"{red}No folder set{reset}")
    for trg, fmt in backup_settings.items():
        echo(f"{blue}Trigger{reset} {yellow}{trg}{reset}: {yellow}{fmt}{reset}")
    if not backup_settings:
        echo(f"{red}No triggers set{reset}")

    if folder or remove or trigger:
        add_history(db, ctx, trigger=trigger, date_format=date_format, folder=folder, remove=remove)
        backup_database(db, ctx, "config")


@config_app.command("cookies")
@option("--cookie", "-c", "cookie", type=(str, str), metavar="<NAME VALUE>", multiple=True, default=[],
        help="New cookie.")
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def config_cookies(ctx: Context, database: Callable[..., Database], cookie: list[tuple[str, str]]):
    """
    Read or modify stored cookies. If no {yellow}--cookie{reset} option is given, the current values are read instead.
    """

    db: Database = database()

    if cookie:
        backup_database(db, ctx, "preconfig")
        write_cookies(db, dict(cookie))
        add_history(db, ctx, cookies=cookie)

    echo(f"{bold}Cookies{reset}")

    cookies = read_cookies(db)

    len_max_name = max(map(len, (c['name'] for c in cookies)))
    len_max_val = min(get_terminal_size((0, 0)).columns - len_max_name - 10 - 4, 72)

    for c in cookies:
        echo(f"{blue}Cookie{reset} {yellow}{c['name']:<{len_max_name}}{reset}: "
             f"{yellow}{c['value'][:len_max_val]}{'...' if len(c['value']) > len_max_val else ''}{reset}")

    if cookie:
        backup_database(db, ctx, "config")


@config_app.command("files-folder", short_help="Read or modify the submission files folder.")
@argument("new_folder", nargs=1, default=None, required=False,
          type=PathClick(file_okay=False, writable=True, path_type=Path))
@option("--move", is_flag=True, default=False, help="Move files from old folder.")
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def config_files_folder(ctx: Context, database: Callable[..., Database], new_folder: Path | None, move: bool):
    """
    Read or modify the folder used to store submission files, where {yellow}NEW_FOLDER{reset} is the path to the new
    folder. If {yellow}NEW_FOLDER{reset} is omitted, the current value is read instead.


    If the {yellow}--move{reset} option is used, all files will be moved to the new location.
    """

    db: Database = database()

    if new_folder:
        backup_database(db, ctx, "preconfig")

    folder: str = db.settings[db.settings.files_folder_setting]
    folder_p: Path = Path(folder)
    echo(f"{bold}Files Folder{reset}\n" +
         f"{blue}Folder{reset}: {yellow}{folder}{reset}" +
         (f" ({yellow}{db.path.parent / folder_p}{reset})" if not folder_p.is_absolute() else ""), color=ctx.color)

    if new_folder is None:
        return
    elif str(new_folder) == db.settings[db.settings.files_folder_setting]:
        echo(f"Files folder is already {yellow}{new_folder}{reset}", color=ctx.color)
        return

    echo(f"{blue}New Folder{reset}: {yellow}{new_folder}{reset}", color=ctx.color)

    try:
        if move:
            echo(f"Moving files to new folder {yellow}{new_folder}{reset}", color=ctx.color)
            folder: Path = db.settings.files_folder
            new_folder_abs: Path = new_folder.resolve()
            total: int = len(db.submissions)
            total_log: int = ceil(log10(total or 1))
            submissions: Cursor = db.submissions.select(columns=[SubmissionsColumns.ID])
            for i, [id_] in enumerate(submissions.tuples, 1):
                echo(f"\r{i:0{total_log}}/{total} ", nl=False)
                fs, t = db.submissions.get_submission_files(id_)
                for f in fs or []:
                    if f.is_file():
                        move_submission_file(f.resolve(), folder, new_folder_abs)
                if t and t.is_file():
                    move_submission_file(t.resolve(), folder, new_folder_abs)
                if i == 10:
                    break
        db.settings.files_folder = new_folder
    finally:
        add_history(db, ctx, new_folder=new_folder, move=move)
        db.commit()

    backup_database(db, ctx, "config")


config_app.list_commands = lambda *_: [
    config_list.name,
    config_cookies.name,
    config_files_folder.name,
    config_backup.name,
]
