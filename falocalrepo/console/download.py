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
from click import secho
from click.shell_completion import CompletionItem
from faapi import FAAPI
from faapi.exceptions import Unauthorized
from falocalrepo_database import Database
from falocalrepo_database.database import clean_username
from requests.exceptions import RequestException

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
from ..downloader import sort_set


class FolderChoice(CompleteChoice):
    completion_items: list[CompletionItem] = [
        CompletionItem(Folder.gallery.value, help="User's gallery folder"),
        CompletionItem(Folder.scraps.value, help="User's scraps folder"),
        CompletionItem(Folder.favorites.value, help="User's favorites folder"),
        CompletionItem(Folder.journals.value, help="User's journals"),
        CompletionItem(Folder.userpage.value, help="User's profile page"),
    ]


class UpdateFolderChoice(CompleteChoice):
    completion_items: list[CompletionItem] = [
        *FolderChoice.completion_items,
        CompletionItem(f"{Folder.watchlist_by.value}", help=f"User's watches"),
        CompletionItem(f"{Folder.watchlist_to.value}", help=f"Users watching user"),
    ]


class DownloadFolderChoice(CompleteChoice):
    completion_items: list[CompletionItem] = [
        *FolderChoice.completion_items,
        *[CompletionItem(f"{Folder.watchlist_by.value}:{f}", help=f"User's watches ({f})")
          for f in Folder if f != Folder.watchlist_by and f != Folder.watchlist_to],
        *[CompletionItem(f"{Folder.watchlist_to.value}:{f}", help=f"Users watching user ({f})")
          for f in Folder if f != Folder.watchlist_by and f != Folder.watchlist_to],
    ]


output_option = option("--simple-output", is_flag=True, default=False, help="Simplified output.")
dry_run_option = option("--dry-run", is_flag=True, default=False, help="Fetch entries without modifying database.")
verbose_report_option = option("--verbose-report", is_flag=True, default=False, help="Output full report with IDs.")
report_file_option = option("--report-file", default=None, type=File("w"), help="Write download report to a file.")
retry_option = option("--retry", metavar="INTEGER", default=1, type=IntRange(1, 5), show_default=True,
                      help="Retry downloads.")
comments_option = option("--save-comments", is_flag=True, default=False, help="Save entries' comments.")


def users_callback(ctx: Context, param: Option, value: tuple[str]) -> tuple[str]:
    if not value or ctx.params.get("like"):
        return value
    value_clean: list[str] = [u if u == "@me" else clean_username(u) for u in map(str.lower, value)]
    if invalid := [u1 for u1, u2 in zip(value, value_clean) if not u2]:
        raise BadParameter(
            f"User{'s' if len(invalid) - 1 else ''} {', '.join(map(repr, invalid))}"
            f" {'do' if len(invalid) - 1 else 'does'} not contain any valid characters"
            f" (allowed characters are [a-z0-9.~-]).",
            ctx, param)
    return tuple(sort_set(list(filter(bool, value_clean))))


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
    api: FAAPI = open_api(db, ctx, check_login=False)

    echo(f"{bold}Login{reset}", color=ctx.color)

    try:
        echo(f"{blue}User{reset}: ", nl=False, color=ctx.color)
        echo(f"{green}{api.me().name}{reset}", color=ctx.color)
    except (Unauthorized, RequestException) as err:
        echo(f"{red}{' '.join(err.args)}{reset}", color=ctx.color)
        ctx.exit(1)


# noinspection DuplicatedCode
@download_app.command("users", short_help="Download users.", no_args_is_help=True)
@option("--user", "-u", "users", metavar="USER", required=True, multiple=True, type=str, callback=users_callback,
        help="Username.")
@option("--folder", "-f", "folders", metavar="FOLDER", required=True, multiple=True, type=DownloadFolderChoice(),
        callback=lambda _c, _p, v: sort_set(v), help="Folder to download.")
@retry_option
@comments_option
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format(', '.join([c.value for c in FolderChoice.completion_items] +
                            [Folder.watchlist_by.value + f":{yellow}FOLDER{reset}"] +
                            [Folder.watchlist_to.value + f":{yellow}FOLDER{reset}"]))
def download_users(ctx: Context, database: Callable[..., Database], users: tuple[str], folders: tuple[str],
                   retry: int | None, save_comments: bool, dry_run: bool, verbose_report: bool,
                   report_file: TextIO | None):
    """
    Download specific user folders, where {yellow}FOLDER{reset} is one of {0}. Multiple {yellow}--user{reset} and
    {yellow}--folder{reset} arguments can be passed. {yellow}USER{reset} can be set to {cyan}@me{reset} to fetch own
    username. {cyan}watchlist-by:{yellow}FOLDER{reset} and {cyan}watchlist-to:{yellow}FOLDER{reset} arguments add the
    specified {yellow}FOLDER{reset}(s) to the new user entries.

    The {yellow}--retry{reset} option enables downloads retries for submission files and thumbnails up to 5 retries.

    The {yellow}--save-comments{reset} option allows saving comments for downloaded submissions and journals. Comments
    are otherwise ignored.

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries.
    Users are not added/deactivated.
    """
    db: Database = database()
    api: FAAPI = open_api(db, ctx)
    downloader: Downloader = Downloader(db, api, color=ctx.color, comments=save_comments, retry=retry or 0,
                                        dry_run=dry_run)
    if not dry_run:
        add_history(db, ctx, users=users, folders=folders)
    watchlist_by: list[str] = [f.split(":")[1] for f in folders if f.startswith(Folder.watchlist_by.value)]
    watchlist_to: list[str] = [f.split(":")[1] for f in folders if f.startswith(Folder.watchlist_to.value)]
    folders_ = [f for f in folders
                if not (f.startswith(Folder.watchlist_by.value) or f.startswith(Folder.watchlist_to.value))]
    if watchlist_by:
        folders_.insert(folders.index(next((f for f in folders if f.startswith(Folder.watchlist_by.value)))),
                        f"{Folder.watchlist_by.value}:{':'.join(watchlist_by)}")
    if watchlist_to:
        folders_.insert(folders.index(next((f for f in folders if f.startswith(Folder.watchlist_to.value)))),
                        f"{Folder.watchlist_to.value}:{':'.join(watchlist_to)}")
    folders = folders_
    try:
        downloader.download_users(list(users), list(folders))
    except Unauthorized as err:
        secho(f"\nError: Unauthorized{(': ' + ' '.join(err.args)) if err.args else ''}", fg="red", color=ctx.color)
    except RequestException as err:
        secho(f"\nError: An error occurred during download: {err!r}.", fg="red", color=ctx.color)
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


# noinspection DuplicatedCode
@download_app.command("update", short_help="Download new entries for users in database.")
@option("--user", "-u", "users", metavar="USER", multiple=True, type=str, callback=users_callback,
        help="User to update.")
@option("--folder", "-f", "folders", metavar="FOLDER", multiple=True, type=UpdateFolderChoice(),
        callback=lambda _c, _p, v: sort_set(v), help="Folder to update.")
@option("--stop", metavar="STOP", type=IntRange(0, min_open=True), default=1, show_default=True,
        help="Number of submissions to find in the database before stopping.")
@option("--deactivated", is_flag=True, default=False, help="Check deactivated users.")
@option("--like", is_flag=True, is_eager=True, default=False, help=f"Consider {yellow}USER{reset} to be LIKE queries.")
@retry_option
@comments_option
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format(', '.join(c.value for c in UpdateFolderChoice.completion_items))
def download_update(ctx: Context, database: Callable[..., Database], users: tuple[str], folders: tuple[str], stop: int,
                    deactivated: bool, like: bool, retry: int | None, save_comments: bool, dry_run: bool,
                    verbose_report: bool,
                    report_file: TextIO | None):
    """
    Download new entries using the users and folders already in the database. {yellow}--user{reset} and
    {yellow}--folder{reset} options can be used to restrict the update to specific users and or folders, where
    {yellow}FOLDER{reset} is one of {0}. Multiple {yellow}--user{reset} and {yellow}--folder{reset} arguments can be
    passed. {yellow}USER{reset} can be set to {cyan}@me{reset} to fetch own username.

    If the {yellow}--deactivated{reset} option is used, deactivated users are fetched instead of ignore. If the user is
    no longer inactive, the database entry will be modified as well.

    The {yellow}--stop{reset} option allows setting after how many entries of each folder should be found in the
    database before stopping the update.

    The {yellow}--like{reset} option enables using SQLite LIKE statements for {yellow}USER{reset} values, allowing to
    select multiple users at once.

    The {yellow}--retry{reset} option enables downloads retries for submission files and thumbnails up to 5 retries.

    The {yellow}--save-comments{reset} option allows saving comments for downloaded submissions and journals. Comments
    are otherwise ignored.

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries.
    Users are not added/deactivated.
    """
    db: Database = database()
    api: FAAPI = open_api(db, ctx)
    downloader: Downloader = Downloader(db, api, color=ctx.color, comments=save_comments, retry=retry or 0,
                                        dry_run=dry_run)
    if not dry_run:
        add_history(db, ctx, users=users, folders=folders, stop=stop)
    try:
        downloader.download_users_update(list(users), list(folders), stop, deactivated, like)
    except Unauthorized as err:
        secho(f"\nError: Unauthorized{(': ' + ' '.join(err.args)) if err.args else ''}", fg="red", color=ctx.color)
    except RequestException as err:
        secho(f"\nError: An error occurred during download: {err!r}.", fg="red", color=ctx.color)
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


# noinspection DuplicatedCode
@download_app.command("submissions", short_help="Download single submissions.", no_args_is_help=True)
@argument("submission_id", nargs=-1, required=True, type=IntRange(1),
          callback=lambda _c, _p, v: sorted(set(v), key=v.index))
@option("--replace", is_flag=True, default=False, show_default=True, help="Replace submissions already in database.")
@retry_option
@comments_option
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def download_submissions(ctx: Context, database: Callable[..., Database], submission_id: tuple[int], replace: bool,
                         retry: int | None, save_comments: bool, dry_run: bool, verbose_report: bool,
                         report_file: TextIO | None):
    """
    Download single submissions, where {yellow}SUBMISSION_ID{reset} is the ID of the submission.

    If the {yellow}--replace{reset} option is used, database entries will be overwritten with new data (favorites will
    be maintained).

    The {yellow}--retry{reset} option enables downloads retries for submission files and thumbnails up to 5 retries.

    The {yellow}--save-comments{reset} option allows saving comments for downloaded submissions and journals. Comments
    are otherwise ignored.

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries
    """
    db: Database = database()
    api: FAAPI = open_api(db, ctx)
    downloader: Downloader = Downloader(db, api, color=ctx.color, comments=save_comments, retry=retry or 0,
                                        dry_run=dry_run)
    if not dry_run:
        add_history(db, ctx, submission_id=submission_id, replace=replace)
    try:
        downloader.download_submissions(list(submission_id), replace)
    except Unauthorized as err:
        secho(f"\nError: Unauthorized{(': ' + ' '.join(err.args)) if err.args else ''}", fg="red", color=ctx.color)
    except RequestException as err:
        secho(f"\nError: An error occurred during download: {err!r}.", fg="red", color=ctx.color)
    finally:
        echo()
        downloader.verbose_report() if verbose_report else downloader.report()
        if report_file:
            downloader.verbose_report(report_file)


# noinspection DuplicatedCode
@download_app.command("journals", short_help="Download single journals.", no_args_is_help=True)
@argument("journal_id", nargs=-1, required=True, type=IntRange(1),
          callback=lambda _c, _p, v: sorted(set(v), key=v.index))
@option("--replace", is_flag=True, default=False, show_default=True, help="Replace submissions already in database.")
@comments_option
@dry_run_option
@verbose_report_option
@report_file_option
@database_exists_option
@color_option
@help_option
@pass_context
@docstring_format()
def download_journals(ctx: Context, database: Callable[..., Database], journal_id: tuple[int], replace: bool,
                      save_comments: bool, dry_run: bool, verbose_report: bool, report_file: TextIO | None):
    """
    Download single journals, where {yellow}JOURNAL_ID{reset} is the ID of the journal.

    If the {yellow}--replace{reset} option is used, database entries will be overwritten with new data (favorites will
    be maintained).

    The {yellow}--save-comments{reset} option allows saving comments for downloaded submissions and journals. Comments
    are otherwise ignored.

    The optional {yellow}--dry-run{reset} option disables downloading and saving and simply lists fetched entries.
    """
    db: Database = database()
    api: FAAPI = open_api(db, ctx)
    downloader: Downloader = Downloader(db, api, color=ctx.color, comments=save_comments, dry_run=dry_run)
    if not dry_run:
        add_history(db, ctx, journal_id=journal_id, replace=replace)
    try:
        downloader.download_journals(list(journal_id), replace)
    except Unauthorized as err:
        secho(f"\nError: Unauthorized{(': ' + ' '.join(err.args)) if err.args else ''}", fg="red", color=ctx.color)
    except RequestException as err:
        secho(f"\nError: An error occurred during download: {err!r}.", fg="red", color=ctx.color)
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
