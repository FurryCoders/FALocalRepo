from enum import Enum
from enum import EnumMeta
from enum import auto
from json import dump
from operator import itemgetter
from shutil import get_terminal_size
from typing import Any
from typing import Callable
from typing import Iterable
from typing import TextIO
from typing import TypeVar

from click import echo
from faapi import Comment
from faapi import FAAPI
from faapi import Journal
from faapi import Submission
from faapi import SubmissionPartial
from faapi import UserPartial
from faapi.comment import flatten_comments
from faapi.exceptions import DisabledAccount
from faapi.exceptions import NotFound
from faapi.exceptions import NoticeMessage
from faapi.exceptions import ServerError
from faapi.journal import JournalPartial
from falocalrepo_database import Column
from falocalrepo_database import Database
from falocalrepo_database.selector import SelectorBuilder as Sb
from falocalrepo_database.tables import CommentsColumns
from falocalrepo_database.tables import JournalsColumns
from falocalrepo_database.tables import SubmissionsColumns
from falocalrepo_database.tables import UsersColumns
from falocalrepo_database.tables import journals_table
from falocalrepo_database.tables import submissions_table
from requests import RequestException
from requests import Response

from .console.colors import *
from .console.util import clean_string

_FolderDownloader = Callable[[str, int | str], tuple[list[SubmissionPartial], str | int]]

T = TypeVar("T")
P = TypeVar("P")


class OutputType(str, Enum):
    rich = auto()
    simple = auto()


class Folder(str, Enum):
    gallery = "gallery"
    scraps = "scraps"
    favorites = "favorites"
    journals = "journals"
    userpage = "userpage"
    watchlist_by = "watchlist-by"
    watchlist_to = "watchlist-to"

    @classmethod
    def as_list(cls: EnumMeta) -> list[str]:
        return [c.value for c in cls]


def terminal_width() -> int:
    return get_terminal_size((0, 0)).columns


def fit_string(value: str, width: int | None) -> str:
    return value.encode(errors="replace")[:width].decode(errors="replace") if width and width > 0 else value


def format_entry(entry: dict[str, Any], columns: list[Column]) -> dict:
    columns_: list[str] = [c.name.upper() for c in columns]
    return {k.upper().replace("_", ""): v for k, v in entry.items() if k.upper().replace("_", "") in columns_}


def sort_set(obj: list[T]) -> list[T]:
    return sorted(set(obj), key=obj.index)


def get_downloader(api: FAAPI, folder: Folder) -> _FolderDownloader:
    if folder == Folder.gallery:
        return api.gallery
    elif folder == Folder.scraps:
        return api.scraps
    elif folder == Folder.favorites:
        return api.favorites
    else:
        raise KeyError(f"Unknown folder {folder}")


def download_catch(func: Callable[..., T], *args, **kwargs) -> tuple[T | None, int]:
    """
    0 no errors

    1 not found

    2 user disabled

    3 server error
    """
    try:
        return func(*args, **kwargs), 0
    except NotFound:
        return None, 1
    except DisabledAccount:
        return None, 2
    except (NoticeMessage, ServerError):
        return None, 3


def save_comments(db: Database, parent_table: str, parent_id: int, comments: list[Comment], *, replace: bool = False):
    for comment in filter(lambda c: not c.hidden, flatten_comments(comments)):
        db.comments.save_comment(
            {CommentsColumns.ID.name: comment.id,
             CommentsColumns.PARENT_TABLE.name: parent_table,
             CommentsColumns.PARENT_ID.name: parent_id,
             CommentsColumns.REPLY_TO.name: comment.reply_to.id if comment.reply_to else None,
             CommentsColumns.AUTHOR.name: comment.author.name,
             CommentsColumns.DATE.name: comment.date,
             CommentsColumns.TEXT.name: comment.text}, replace=replace)


class Bar:
    def __init__(self, length: int = 0, *, message: str = ""):
        self.length: int = length
        self.level: int = 0
        self.message_: str = ""

        echo(f"[{' ' * self.length}]" + ("\b" * (self.length + 1)), nl=False)

        self.message(message) if message else None

    def clear(self):
        echo("\b \b" * self.level, nl=False)
        self.level = 0
        self.message_ = ""

    def delete(self):
        self.clear()
        echo("\b" + (" " * (self.length + 2)) + ("\b" * (self.length + 2)), nl=False)

    @staticmethod
    def close(end: str = "\n"):
        echo(end, nl=False)

    def update(self, total: int, current: int):
        self.clear() if self.message_ else None

        if (new_level := int((current / total) * self.length)) == self.level:
            return

        echo(("\b \b" * -(diff_level := new_level - self.level)) + (f"{bold}#{reset}" * diff_level), nl=False)

        self.level = new_level

    def message(self, message: str, color: str = ""):
        self.clear()
        self.level = len(message := f"{(message[:self.length]):^{self.length}}")
        echo(color + message + (reset if color else ""), nl=False)
        self.message_: str = message


# noinspection DuplicatedCode
class Downloader:
    def __init__(self, db: Database, api: FAAPI, *, color: bool = True, retry: int = 0, comments: bool = False,
                 dry_run: bool = False):
        self.db: Database = db
        self.output: OutputType = OutputType.rich if terminal_width() > 0 else OutputType.simple
        self.color: bool = color
        self.retry: int = retry
        self.save_comments: bool = comments
        self.dry_run: bool = dry_run
        self.api: FAAPI = api
        self.bar_width: int = 10
        self._bar: Bar | None = None

        self.added_users: list[int | str] = []
        self.added_userpages: list[int | str] = []
        self.added_submissions: list[int | str] = []
        self.added_journals: list[int | str] = []
        self.modified_users: list[int | str] = []
        self.modified_userpages: list[int | str] = []
        self.modified_submissions: list[int | str] = []
        self.modified_journals: list[int | str] = []
        self.user_errors: list[str] = []
        self.user_deactivated: list[str] = []
        self.submission_errors: list[int] = []
        self.file_errors: list[int] = []
        self.thumbnail_errors: list[int] = []
        self.journal_errors: list[int] = []

    def report(self):
        items: list[tuple[str, int]] = [
            ("Added users", len(set(self.added_users))),
            ("Modified users", len(set(self.modified_users))),
            ("Added userpages", len(set(self.added_userpages))),
            ("Modified userpages", len(set(self.modified_userpages))),
            ("Users deactivated", len(set(self.user_deactivated))),
            ("User errors", len(set(self.user_errors))),
            ("Added submissions", len(set(self.added_submissions))),
            ("Modified submissions", len(set(self.modified_submissions))),
            ("Submission errors", len(set(self.submission_errors))),
            ("File errors", len(set(self.file_errors))),
            ("Thumbnail errors", len(set(self.thumbnail_errors))),
            ("Added journals", len(set(self.added_journals))),
            ("Modified journals", len(set(self.modified_journals))),
            ("Journal Errors", len(set(self.journal_errors))),
        ]
        if items := list(filter(itemgetter(1), items)):
            name_padding: int = max(map(len, map(itemgetter(0), items or [""])))
            for name, value in items:
                echo(f"{blue}{name:<{name_padding}}{reset}: {yellow}{value}{reset}", color=self.color)

    def verbose_report(self, file: TextIO | None = None):
        if file:
            dump({
                "users": {
                    "added": sort_set(self.added_users),
                    "modified": sort_set(self.modified_users),
                    "errors": sort_set(self.user_errors),
                    "deactivated": sort_set(self.user_deactivated),
                    "added_userpages": sort_set(self.added_userpages),
                    "modified_userpages": sort_set(self.modified_userpages),
                },
                "submissions": {
                    "added": sort_set(self.added_submissions),
                    "modified": sort_set(self.modified_submissions),
                    "errors": sort_set(self.submission_errors),
                    "file_errors": sort_set(self.file_errors),
                    "thumbnail_errors": sort_set(self.thumbnail_errors),
                },
                "journals": {
                    "added": sort_set(self.added_journals),
                    "modified": sort_set(self.modified_journals),
                    "errors": sort_set(self.journal_errors)
                }}, file)
        else:
            items: list[tuple[str, list[int | str]]] = [
                ("Added users", sort_set(self.added_users)),
                ("Modified users", sort_set(self.modified_users)),
                ("Added userpages", sort_set(self.added_userpages)),
                ("Modified userpages", sort_set(self.modified_userpages)),
                ("Users deactivated", sort_set(self.user_deactivated)),
                ("User errors", sort_set(self.user_errors)),
                ("Added submission", sort_set(self.added_submissions)),
                ("Modified submission", sort_set(self.modified_submissions)),
                ("Submission errors", sort_set(self.submission_errors)),
                ("File errors", sort_set(self.file_errors)),
                ("Thumbnail errors", sort_set(self.thumbnail_errors)),
                ("Added journal", sort_set(self.added_journals)),
                ("Modified journal", sort_set(self.modified_journals)),
                ("Journal Errors", sort_set(self.journal_errors)),
            ]
            name_padding: int = max(map(len, map(itemgetter(0), items)))
            for name, value in items:
                echo(f"{blue}{name:<{name_padding}}{reset}: {yellow}{value}{reset}", color=self.color)

    def _make_bar(self, bar_width: int = None):
        return Bar(self.bar_width if bar_width is None else bar_width)

    def clear_line(self):
        if self.output == OutputType.simple:
            return
        echo("\r" + (" " * (terminal_width() - 1)) + "\r", nl=False)

    def bar(self, bar_width: int = None):
        if self.output == OutputType.simple:
            return
        self._bar = self._make_bar(bar_width) if self._bar is None else self._bar
        return self._bar

    def bar_update(self, total: int, level: int):
        if self._bar is None or self.output == OutputType.simple:
            return
        self._bar.update(total, level)

    def bar_message(self, message: str, color: str = "", *, always: bool = False):
        if self._bar is None or self.output == OutputType.simple:
            if always:
                echo(message)
            return
        self._bar.message(message, color)

    def bar_close(self, end: str = "\n"):
        if self._bar is None or self.output == OutputType.simple:
            return
        self._bar.close(end)
        self._bar = None

    def bar_clear(self):
        if self._bar is None or self.output == OutputType.simple:
            return
        self._bar.clear()

    def bar_delete(self):
        if self._bar is None or self.output == OutputType.simple:
            return
        self._bar.delete()

    def download_bytes(self, url: str) -> bytes | None:
        try:
            stream: Response = self.api.session.get(url, stream=True)
            stream.raise_for_status()
            size: int = int(stream.headers.get("Content-Length", 0))
            on_chunk = self.bar_update if size else lambda *_: None
            file: bytes = bytes()
            for chunk in stream.iter_content(chunk_size=int(1e3)):
                file += chunk
                on_chunk(size, len(file))
            return file
        except RequestException:
            return None

    def err_to_bar(self, err: int, *, close: bool = True, close_end: str = "\n") -> int:
        if err == 1:
            self.bar_message("NOT FOUND", red)
        elif err == 2:
            self.bar_message("NOT ACTIVE", red)
        elif err == 3:
            self.bar_message("SERVER ERR", red)
        if err and close:
            self.bar_close(close_end)
        return err

    def download_journal(self, journal_id: int, user_update: bool, replace: bool = False) -> int:
        self.bar_clear()
        self.bar_message("DOWNLOAD")
        result, err = download_catch(self.api.journal, journal_id)
        if self.err_to_bar(err):
            self.journal_errors += [journal_id]
            return err
        journal: Journal = result
        self.db.journals.save_journal({
            **format_entry(dict(journal), self.db.journals.columns),
            JournalsColumns.AUTHOR.name: journal.author.name,
            JournalsColumns.USERUPDATE.name: user_update
        }, replace=replace)
        if self.save_comments:
            save_comments(self.db, journals_table, journal.id, journal.comments, replace=replace)
        self.db.commit()
        self.bar_message("ADDED", green, always=True)
        return 0

    def download_submission(self, submission_id: int, user_update: bool, favorites: Iterable[str] | None,
                            thumbnail: str, replace: bool = False) -> int:
        self.bar_clear()
        self.bar_message("DOWNLOAD")
        result, err = download_catch(self.api.submission, submission_id)
        if self.err_to_bar(err):
            self.submission_errors += [submission_id]
            return err
        submission: Submission = result[0]
        self.bar_clear()
        self.bar_close("\b")
        self.bar(7)
        file: bytes | None = self.download_bytes(submission.file_url)
        retry: int = self.retry + 1
        while file is None and (retry := retry - 1):
            self.bar_message(f"RETRY {self.retry - retry + 1}", red)
            self.api.handle_delay()
            file = self.download_bytes(submission.file_url)
        self.bar_message(("#" * self.bar_width) if file else "ERROR", green if file else red, always=True)
        self.bar_close("]")
        self.bar(1)
        thumb: bytes | None = self.download_bytes(submission.thumbnail_url or thumbnail)
        retry = self.retry + 1
        while thumb is None and (retry := retry - 1):
            self.bar_message(f"RETRY {self.retry - retry + 1}", red)
            self.api.handle_delay()
            thumb = self.download_bytes(submission.thumbnail_url or thumbnail)
        self.db.submissions.save_submission({**format_entry(dict(submission), self.db.submissions.columns),
                                             SubmissionsColumns.AUTHOR.name: submission.author.name,
                                             SubmissionsColumns.FAVORITE.name: {*favorites} if favorites else {},
                                             SubmissionsColumns.USERUPDATE.name: user_update},
                                            file, thumb, replace=replace)
        if self.save_comments:
            save_comments(self.db, submissions_table, submission.id, submission.comments, replace=replace)
        self.db.commit()
        self.bar_message(("#" * self.bar_width) if thumb else "ERROR", green if thumb else red, always=True)
        self.bar_close()
        self.added_submissions += [submission_id]
        self.file_errors += [] if file else [submission_id]
        self.thumbnail_errors += [] if thumb else [submission_id]
        return 0

    def download_user_folder(self, user: str, folder: Folder, downloader_entries: Callable[[str, P], tuple[list[T], P]],
                             page_start: P, entry_id_getter: Callable[[T], int | str], entry_formats: tuple[str, str],
                             contains: Callable[[T], dict | None],
                             modify_checks: list[tuple[Callable[[T, dict], bool], str]],
                             save: tuple[Callable[[T], int | None], str], stop: int = -1,
                             clear_last_found: bool = False, clear_found: bool = False,
                             ) -> tuple[int, tuple[list[int | str], list[int | str], list[int | str]]]:
        entries_added: list[int | str] = []
        entries_modified: list[int | str] = []
        entries_errors: list[int | str] = []
        page: P | None = page_start
        page_i: int = 0
        while page:
            page_i += 1
            page_width: int = len(str(page_i))
            folder_page_width: int = len(user) + 1 + len(folder.name) + 1 + page_width
            padding: int = (w - folder_page_width - self.bar_width - 2 - 1) if (w := terminal_width()) else 0
            echo(f"{yellow}{user}{reset}/{yellow}{folder.name}{reset} {page_i}" +
                 (" " * padding),
                 nl=self.output == OutputType.simple, color=self.color)
            self.bar()
            self.bar_message("DOWNLOAD")
            result, err = download_catch(downloader_entries, user, page)
            if err:
                self.user_errors += [user]
                self.err_to_bar(err)
                return err, (entries_added, entries_modified, entries_errors)
            self.bar_close("")
            self.clear_line()
            entries: list[T] = result[0]
            page = result[1]
            entries_width: int = len(str(len(entries)))
            for i, entry in enumerate(entries, 1):
                t_width: int = terminal_width()
                available_space: int = t_width - self.bar_width - 2 - 1 - 1
                entry_num: str = f"{page_i}/{i:0{entries_width}}"
                entry_id: str = clean_string(entry_formats[0].format(entry).strip())
                entry_title: str = clean_string(entry_formats[1].format(entry).strip())
                entry_outputs: list[str] = list(filter(bool, [entry_num, entry_id, entry_title]))
                padding = available_space - len(" ".join(entry_outputs))
                while entry_outputs and t_width and (padding := available_space - len(" ".join(entry_outputs))) < 0:
                    if (space_last := available_space - len(" ".join(entry_outputs[:-1]))) < 1:
                        entry_outputs.pop()
                    else:
                        entry_outputs[-1] = fit_string(entry_outputs[-1], space_last - 1)
                padding = 0 if padding < 0 else padding
                entry_outputs = [entry_outputs[0] if entry_outputs else "",
                                 (blue + entry_outputs[1] + reset) if entry_outputs[1:] else "",
                                 entry_outputs[2] if entry_outputs[2:] else ""]
                entry_output: str = " ".join(filter(bool, entry_outputs)) + " "
                echo(("\r" if self.output == OutputType.rich else "") + entry_output + (" " * padding),
                     nl=self.output == OutputType.simple, color=self.color)
                self.bar()
                self.bar_message("SEARCHING")
                if curr_entry := contains(entry):
                    self.bar_message("IN DB", green, always=True)
                    if self.dry_run:
                        stop -= 1
                        if clear_found or (clear_last_found and stop == 0):
                            self.bar_close("")
                            self.clear_line()
                    else:
                        modified: bool = False
                        for check, message in modify_checks:
                            if modified := check(entry, curr_entry):
                                self.db.commit()
                                self.bar_message(message or "UPDATED", green, always=True)
                                entries_modified.append(entry_id_getter(entry))
                                break
                        if not modified:
                            stop -= 1
                            if clear_found or (clear_last_found and stop == 0):
                                self.bar_close("")
                                self.clear_line()
                elif self.dry_run:
                    self.bar_message("SKIPPED", green)
                else:
                    err = save[0](entry) or 0
                    if not self.err_to_bar(err) and save[1]:
                        self.bar_message(save[1], green, always=True)
                    entries_added.append(entry_id_getter(entry))
                self.bar_close()
                if stop == 0:
                    page = None
                    break
            self.clear_line()
        return 0, (entries_added, entries_modified, entries_errors)

    def download_user_journals(self, user: str, stop: int = -1, clear_last_found: bool = False) -> int:
        def save(journal: JournalPartial) -> int:
            if self.save_comments:
                return self.download_journal(journal.id, True)
            else:
                self.db.journals.save_journal(
                    {**format_entry(dict(journal), self.db.journals.columns),
                     JournalsColumns.AUTHOR.name: journal.author.name,
                     JournalsColumns.USERUPDATE.value.name: True})
            return 0

        err, [entries_added, entries_modified, entries_errors] = self.download_user_folder(
            user=user, folder=Folder.journals, downloader_entries=self.api.journals, page_start=1,
            entry_id_getter=lambda j: j.id,
            entry_formats=("{0.id:010}", "{0.title}"),
            contains=lambda j: self.db.journals[j.id],
            modify_checks=[(lambda journal, _: self.db.journals.set_user_update(journal.id, True), "")],
            save=(save, "ADDED"),
            stop=stop, clear_last_found=clear_last_found
        )
        self.added_journals.extend(entries_added)
        self.modified_journals.extend(entries_modified)
        self.journal_errors.extend(entries_errors)
        return err

    def download_user_submissions(self, user: str, folder: Folder, stop: int = -1,
                                  clear_last_found: bool = False) -> int:
        downloader: _FolderDownloader = get_downloader(self.api, folder)
        page_start: int | str = "/" if folder == Folder.favorites else 1
        modify_checks: list[tuple[Callable[[SubmissionPartial, dict], bool], str]]

        if folder == Folder.favorites:
            modify_checks = [(lambda submission, _: self.db.submissions.add_favorite(submission.id, user),
                              "ADDED FAV")]
        else:
            modify_checks = [(lambda submission, _: (self.db.submissions.set_user_update(submission.id, True) +
                                                     self.db.submissions.set_folder(submission.id, folder.value)),
                              "UPDATED")]

        err, [_entries_added, entries_modified, _entries_errors] = self.download_user_folder(
            user=user, folder=folder, downloader_entries=downloader, page_start=page_start,
            entry_id_getter=lambda s: s.id,
            entry_formats=("{0.id:010}", "{0.title}"),
            contains=lambda s: self.db.submissions[s.id],
            modify_checks=modify_checks,
            save=(lambda sub_partial: self.download_submission(
                sub_partial.id, folder != Folder.favorites,
                [user] if folder == Folder.favorites else None,
                sub_partial.thumbnail_url), ""),
            stop=stop, clear_last_found=clear_last_found
        )
        self.modified_submissions.extend(entries_modified)
        return err

    def download_user_watchlist(self, user: str, watchlist: Folder, folders: list[str], clear_found: bool = False
                                ) -> int:
        downloader: Callable[[str, int], tuple[list[UserPartial], int]]

        if watchlist == Folder.watchlist_by:
            downloader = self.api.watchlist_by
        else:
            downloader = self.api.watchlist_to

        def check_folders(db: Database, watch: UserPartial, entry: dict[str, Any]) -> bool:
            if folders_ := [f for f in folders if f not in entry[UsersColumns.FOLDERS.name]]:
                for folder in folders_:
                    db.users.add_folder(watch.name_url, folder)
                return True
            return False

        err, [entries_added, entries_modified, _entries_errors] = self.download_user_folder(
            user=user, folder=watchlist, downloader_entries=downloader, page_start=1,
            entry_id_getter=lambda u: u.name_url,
            entry_formats=("{0.status}{0.name}", ""),
            contains=lambda u: self.db.users[u.name_url],
            modify_checks=[(lambda w, e: check_folders(self.db, w, e), "UPDATED")],
            save=(lambda watch: self.db.users.save_user(
                {UsersColumns.USERNAME.value.name: watch.name_url,
                 UsersColumns.FOLDERS.value.name: set(folders),
                 UsersColumns.ACTIVE.value.name: True,
                 UsersColumns.USERPAGE.value.name: ""}), "ADDED"),
            stop=-1, clear_found=clear_found
        )
        self.added_users.extend(entries_added)
        self.modified_users.extend(entries_modified)

        return err

    def download_user_page(self, username: str, clear_found: bool = False) -> int:
        padding: int = w - self.bar_width - 2 - 1 if (w := terminal_width()) else 0
        echo(f"{yellow}{username[:padding or None]:<{padding}}{reset}", nl=self.output == OutputType.simple,
             color=self.color)
        self.bar()
        if self.dry_run:
            self.bar_message("SKIPPED", green)
            self.bar_close("" if clear_found else "\n")
            self.clear_line()
            return 0
        self.bar_message("DOWNLOAD")
        user, err = download_catch(self.api.user, username)
        self.err_to_bar(err)
        if err:
            self.user_errors += [username]
            return err
        added: bool = (current := self.db.users[username][UsersColumns.USERPAGE.value.name]) == ""
        updated: bool = not added and user.profile != current
        if not added and not updated:
            self.bar_message("IN DB", green, always=True)
            self.bar_close("" if clear_found else "\n")
            self.clear_line()
            return 0
        self.db.users[username] = self.db.users[username] | {UsersColumns.USERPAGE.value.name: user.profile}
        self.added_userpages += [username] if added else []
        self.modified_userpages += [username] if updated else []
        self.bar_message("ADDED" if added else "UPDATED", green, always=True)
        return 0

    def download_me(self) -> tuple[str, int]:
        padding: int = w - self.bar_width - 2 - 1 if (w := terminal_width()) else 0
        echo(f"Downloading: {yellow}@me{reset}/{yellow}username{reset}", color=self.color)
        echo(f"{blue}{'@me':<{padding}}{reset}", nl=self.output == OutputType.simple,
             color=self.color)
        self.bar()
        self.bar_message("DOWNLOAD")
        user, err = download_catch(self.api.me)
        if self.err_to_bar(err) or not user:
            self.user_errors += ["@me"]
            return "", err
        echo(("\r" if self.output == OutputType.rich else "") +
             f"{blue}@me{reset} {fit_string(repr(user), padding - 4).ljust(padding - 4)}",
             nl=self.output == OutputType.simple, color=self.color)
        self.bar_close("")
        self.bar()
        self.bar_message("FOUND", green, always=True)
        self.bar_close()
        return user.name_url, err

    def _download_users(self, users_folders: Iterable[tuple[str, list[str]]], stop: int = -1):
        operation: str = "Downloading" if stop < 0 else "Updating"
        for user, folders in users_folders:
            user_added: bool = False
            user_downloaded: bool = False
            if not self.dry_run:
                if user_added := user not in self.db.users:
                    self.db.users.save_user({UsersColumns.USERNAME.value.name: user,
                                             UsersColumns.FOLDERS.value.name: {},
                                             UsersColumns.ACTIVE.value.name: True,
                                             UsersColumns.USERPAGE.value.name: ""})
                    self.db.commit()
                    self.added_users += [user]
                self.db.users.set_active(user, True)
            for folder in folders:
                echo(f"{operation}: {yellow}{user}{reset}/{yellow}{folder.split(':')[0]}{reset}", color=self.color)
                if not self.dry_run:
                    if folder.startswith(w := Folder.watchlist_by) and \
                            (wfs := [f for f in self.db.users[user][UsersColumns.FOLDERS.name] if f.startswith(w)]):
                        for wf in filter(lambda f: f != folder, wfs):
                            self.db.users.remove_folder(user, wf)
                            self.modified_users += [user]
                    elif folder.startswith(w := Folder.watchlist_to) and \
                            (wfs := [f for f in self.db.users[user][UsersColumns.FOLDERS.name] if f.startswith(w)]):
                        for wf in filter(lambda f: f != folder, wfs):
                            self.db.users.remove_folder(user, wf)
                        self.modified_users += [user]
                    added_folder: bool = self.db.users.add_folder(user, folder)
                    self.modified_users += [user] if not user_added and added_folder else []
                err: int
                if folder == Folder.userpage:
                    err = self.download_user_page(user, stop == 1)
                elif folder == Folder.journals:
                    err = self.download_user_journals(user, stop, stop == 1)
                elif folder in (Folder.gallery, Folder.scraps, Folder.favorites):
                    err = self.download_user_submissions(user, Folder[folder.lower()], stop, stop == 1)
                elif folder.startswith(Folder.watchlist_by.value):
                    err = self.download_user_watchlist(user, Folder.watchlist_by, folder.split(":")[1:], stop == 1)
                elif folder.startswith(Folder.watchlist_to.value):
                    err = self.download_user_watchlist(user, Folder.watchlist_to, folder.split(":")[1:], stop == 1)
                else:
                    raise Exception(f"Unknown folder {folder}")
                if not err:
                    user_downloaded = True
                elif not self.dry_run and err in (1, 2):
                    if user_added and not user_downloaded:
                        del self.db.users[user]
                        self.added_users.remove(user)
                    else:
                        self.db.users.set_active(user, False)
                        self.user_deactivated += [user]
                    self.db.commit()
                    break
                self.bar_close()
                self.db.commit()

    def download_users(self, users: list[str], folders: list[str]):
        if "@me" in users:
            if me := self.download_me()[0]:
                users[users.index("@me")] = me
            else:
                users.remove("@me")

        self._download_users([(u, folders) for u in users])

    def download_users_update(self, users: list[str], folders: list[str], stop: int, deactivated: bool, like: bool):
        if not like:
            for user in [u for u in users if u != "@me" and u not in self.db.users]:
                padding: int = terminal_width() - 1 - self.bar_width - 2
                echo(f"{green}{user:<{padding}}{reset}", nl=self.output == OutputType.simple, color=self.color)
                self.bar()
                self.bar_message("NOT IN DB", red, always=True)
                self.bar_close()

        if "@me" in users:
            if me := self.download_me()[0]:
                users[users.index("@me")] = me
            else:
                users.remove("@me")

        users_cursor: Iterable[dict]
        if like and users:
            users_cursor = self.db.users.select(Sb() | [Sb(UsersColumns.USERNAME.value.name) % u for u in users])
        elif users:
            users_cursor = self.db.users[users]
        else:
            users_cursor = self.db.users.select(order=[UsersColumns.USERNAME.value.name])
        users_folders: list[tuple[str, list[str]]]
        users_folders = [(u[UsersColumns.USERNAME.value.name], [*u[UsersColumns.FOLDERS.value.name]])
                         for u in users_cursor if u[UsersColumns.ACTIVE.value.name] or deactivated]

        users_folders = sorted(users_folders, key=lambda uf: users.index(uf[0]) if users and not like else uf[0])

        if folders:
            users_folders = [(u, sorted(filter(lambda f: f.split(":")[0] in folders, fs),
                                        key=lambda f: folders.index(f.split(":")[0])))
                             for u, fs in users_folders]
        else:
            users_folders = [(u, sorted(fs, key=lambda f: Folder.as_list().index(f.split(":")[0])))
                             for u, fs in users_folders]

        if not users_folders:
            return echo("No users to update")

        self._download_users(users_folders, stop)

    # noinspection DuplicatedCode
    def download_submissions(self, submission_ids: list[int], replace: bool = False):
        header_width: int = (len(str(len(submission_ids))) * 2) + 2
        for i, submission_id in enumerate(submission_ids, 1):
            echo(f"{i}/{len(submission_ids)}".ljust(header_width) + f"{blue}{submission_id:010}{reset} ",
                 nl=self.output == OutputType.simple, color=self.color)
            self.bar()
            self.bar_message("SEARCHING")
            if (entry := (self.db.submissions[submission_id] or {})) and not replace:
                self.bar_message("IN DB", green)
                self.bar_close()
                continue
            elif self.dry_run:
                self.bar_message("SKIPPED", green)
                self.bar_close()
                continue
            self.download_submission(submission_id,
                                     entry.get(SubmissionsColumns.USERUPDATE.value.name, False),
                                     entry.get(SubmissionsColumns.FAVORITE.value.name, {}),
                                     "", replace)

    # noinspection DuplicatedCode
    def download_journals(self, journal_ids: list[int], replace: bool = False):
        header_width: int = (len(str(len(journal_ids))) * 2) + 2
        for i, journal_id in enumerate(journal_ids, 1):
            echo(f"{i}/{len(journal_ids)}".ljust(header_width) + f"{blue}{journal_id:010}{reset} ",
                 nl=self.output == OutputType.simple, color=self.color)
            self.bar()
            self.bar_message("SEARCHING")
            if (entry := (self.db.journals[journal_id] or {})) and not replace:
                self.bar_message("IN DB", green)
                self.bar_close()
                continue
            elif self.dry_run:
                self.bar_message("SKIPPED", green)
                self.bar_close()
                continue
            journal, err = download_catch(self.api.journal, journal_id)
            if self.err_to_bar(err):
                self.journal_errors += [journal.id]
                continue
            if self.save_comments:
                self.download_journal(journal.id, entry.get(JournalsColumns.USERUPDATE.name, False), replace=replace)
            else:
                self.db.journals.save_journal({
                    **format_entry(dict(journal), self.db.journals.columns),
                    JournalsColumns.AUTHOR.name: journal.author.name,
                    (u := JournalsColumns.USERUPDATE.name): entry.get(u, False)
                }, replace=replace)
            self.added_journals += [journal.id]
            self.db.commit()
            self.bar_message("ADDED", green, always=True)
            self.bar_close()
