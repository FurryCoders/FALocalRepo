from typing import Callable
from typing import TextIO

from click import BadParameter
from click import Context
from click import File
from click import IntRange
from click import Option
from click import argument
from click import echo
from click import group
from click import option
from click import pass_context
from click.shell_completion import CompletionItem
from faapi import User
from faapi.exceptions import Unauthorized
from falocalrepo_database import Database
from falocalrepo_database.database import clean_username

from .colors import *
from .util import CompleteChoice
from .util import CustomHelpColorsGroup
from .util import add_history
from .util import color_option
from .util import database_exists_option
from .util import docstring_format
from .util import help_option
from .util import open_api
from ..downloader import Downloader
from ..downloader import Folder


class FolderChoice(CompleteChoice):
    completion_items: list[CompletionItem] = [
        CompletionItem(Folder.gallery.value, help="User's gallery folder"),
        CompletionItem(Folder.scraps.value, help="User's scraps folder"),
        CompletionItem(Folder.favorites.value, help="User's favorites folder"),
        CompletionItem(Folder.journals.value, help="User's journals"),
        CompletionItem(Folder.userpage.value, help="User's profile page"),
    ]


output_option = option("--simple-output", is_flag=True, default=False, help="Simplified output.")
dry_run_option = option("--dry-run", is_flag=True, default=False, help="Fetch entries without modifying database.")
verbose_report_option = option("--verbose-report", is_flag=True, default=False, help="Output full report with IDs.")
report_file_option = option("--report-file", default=None, type=File("w"), help="Write download report to a file.")


@group("download", cls=CustomHelpColorsGroup, short_help="Download resources.", no_args_is_help=True,
       add_help_option=False)
@color_option
@help_option
def download_app():
    """
    The download command performs all download operations to save and update users, submissions, and journals.
    Submissions are downloaded together with their thumbnails, if there are any.
    """
    pass


def users_callback(ctx: Context, param: Option, value: tuple[str]) -> tuple[str]:
    value_clean: list[str] = list(filter(bool, map(clean_username, value)))
    if not value_clean and param.required:
        raise BadParameter("Invalid users", ctx, param)
    return tuple(sorted(set(value_clean), key=value_clean.index))


@download_app.command("login", short_help="Check cookies' validity.")
@database_exists_option
@color_option
@help_option
@pass_context
def download_login(ctx: Context, database: Callable[..., Database]):
    """
    Check whether the cookies stored in the database belong to a login Fur Affinity session.
    """

    db: Database = database()

    echo(f"{bold}Login{reset}", color=ctx.color)

    try:
        echo(f"{blue}User{reset}: ", nl=False, color=ctx.color)
        me: User = open_api(db).me()
        echo(f"{green}{me.name}{reset}", color=ctx.color)
    except Unauthorized as err:
        echo(f"{red}{' '.join(err.args)}{reset}", color=ctx.color)
        ctx.exit(1)


@download_app.command("users", short_help="Download users.", no_args_is_help=True)
@option("--user", "-u", "users", metavar="USER", required=True, multiple=True, type=str, callback=users_callback,
        help="Username.")
@option("--folder", "-f", "folders", metavar="FOLDER", required=True, multiple=True, type=FolderChoice(),
        callback=lambda _c, _p, v: sorted(set(v), key=v.index), help="Folder to download.")
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format(', '.join(Folder))
def download_users(ctx: Context, database: Callable[..., Database], users: tuple[str], folders: tuple[str],
                   dry_run: bool, verbose_report: bool, report_file: TextIO | None):
    """
    Download specific user folders, where {yellow}FOLDER{reset} is one of {0}. Multiple {yellow}--user{reset} and
    {yellow}--folder{reset} arguments can be passed.

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries.
    Users are not added/deactivated.
    """
    db: Database = database()
    add_history(db, ctx, users=users, folders=folders)
    downloader: Downloader = Downloader(db, open_api(db), color=ctx.color, dry_run=dry_run)
    try:
        downloader.download_users(list(users), list(folders))
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


@download_app.command("update", short_help="Download new entries for users in database.")
@option("--user", "-u", "users", metavar="USER", multiple=True, type=str, callback=users_callback,
        help="User to update.")
@option("--folder", "-f", "folders", metavar="FOLDER", multiple=True, type=FolderChoice(),
        callback=lambda _c, _p, v: sorted(set(v), key=v.index), help="Folder to update.")
@option("--stop", metavar="STOP", type=IntRange(0, min_open=True), default=1, show_default=True,
        help="Number of submissions to find in the database before stopping.")
@option("--deactivated", is_flag=True, default=False, help="Check deactivated users.")
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format(', '.join(Folder))
def download_update(ctx: Context, database: Callable[..., Database], users: tuple[str], folders: tuple[str], stop: int,
                    deactivated: bool, dry_run: bool, verbose_report: bool, report_file: TextIO | None):
    """
    Download new entries using the users and folders already in the database. {yellow}--user{reset} and
    {yellow}--folder{reset} options can be used to restrict the update to specific users and or folders, where
    {yellow}FOLDER{reset} is one of {0}. Multiple {yellow}--user{reset} and {yellow}--folder{reset} arguments can be
    passed.

    If the {yellow}--deactivated{reset} option is used, deactivated users are fetched instead of ignore. If the user is
    no longer inactive, the database entry will be modified as well.

    The {yellow}--stop{reset} option allows setting after how many entries of each folder should be found in the
    database before stopping the update.

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries.
    Users are not added/deactivated.
    """
    db: Database = database()
    add_history(db, ctx, users=users, folders=folders, stop=stop)
    downloader: Downloader = Downloader(db, open_api(db), color=ctx.color, dry_run=dry_run)
    try:
        downloader.download_users_update(list(users), list(folders), stop, deactivated)
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


@download_app.command("submissions", short_help="Download single submissions.", no_args_is_help=True)
@argument("submission_id", nargs=-1, required=True, type=IntRange(1),
          callback=lambda _c, _p, v: sorted(set(v), key=v.index))
@option("--replace", is_flag=True, default=False, show_default=True, help="Replace submissions already in database.")
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def download_submissions(ctx: Context, database: Callable[..., Database], submission_id: tuple[int], replace: bool,
                         dry_run: bool, verbose_report: bool, report_file: TextIO | None):
    """
    Download single submissions, where {yellow}SUBMISSION_ID{reset} is the ID of the submission.

    If the {yellow}--replace{reset} option is used, database entries will be overwritten with new data (favorites will
    be maintained).

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries
    """
    db: Database = database()
    add_history(db, ctx, submission_id=submission_id, replace=replace)
    downloader: Downloader = Downloader(db, open_api(db), color=ctx.color, dry_run=dry_run)
    try:
        downloader.download_submissions(list(submission_id), replace)
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


@download_app.command("journals", short_help="Download single journals.", no_args_is_help=True)
@argument("journal_id", nargs=-1, required=True, type=IntRange(1),
          callback=lambda _c, _p, v: sorted(set(v), key=v.index))
@option("--replace", is_flag=True, default=False, show_default=True, help="Replace submissions already in database.")
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def download_journals(ctx: Context, database: Callable[..., Database], journal_id: tuple[int], replace: bool,
                      dry_run: bool, verbose_report: bool, report_file: TextIO | None):
    """
    Download single journals, where {yellow}JOURNAL_ID{reset} is the ID of the journal.

    If the {yellow}--replace{reset} option is used, database entries will be overwritten with new data (favorites will
    be maintained).

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries.
    """
    db: Database = database()
    add_history(db, ctx, journal_id=journal_id, replace=replace)
    downloader: Downloader = Downloader(db, open_api(db), color=ctx.color, dry_run=dry_run)
    try:
        downloader.download_journals(list(journal_id), replace)
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


download_app.list_commands = lambda *_: [
    download_login.name,
    download_users.name,
    download_update.name,
    download_submissions.name,
    download_journals.name,
]
