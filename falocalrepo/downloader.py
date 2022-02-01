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
from faapi import FAAPI
from faapi import SubmissionPartial
from faapi.exceptions import DisabledAccount
from faapi.exceptions import NotFound
from faapi.exceptions import NoticeMessage
from faapi.exceptions import ServerError
from falocalrepo_database import Column
from falocalrepo_database import Database
from falocalrepo_database.tables import JournalsColumns
from falocalrepo_database.tables import SubmissionsColumns
from falocalrepo_database.tables import UsersColumns
from requests import RequestException
from requests import Response

from .console.colors import *
from .console.util import clean_string

_FolderDownloader = Callable[[str, int | str], tuple[list[SubmissionPartial], str | int]]

T = TypeVar("T")


class OutputType(str, Enum):
    rich = auto()
    simple = auto()


class Folder(str, Enum):
    gallery = "gallery"
    scraps = "scraps"
    favorites = "favorites"
    journals = "journals"
    userpage = "userpage"

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


class Downloader:
    def __init__(self, db: Database, api: FAAPI, *, color: bool = True, dry_run: bool = False):
        self.db: Database = db
        self.output: OutputType = OutputType.rich if terminal_width() > 0 else OutputType.simple
        self.color: bool = color
        self.dry_run: bool = dry_run
        self.api: FAAPI = api
        self.bar_width: int = 10
        self._bar: Bar | None = None

        self.added_users: list[int | str] = []
        self.added_submissions: list[int | str] = []
        self.added_journals: list[int | str] = []
        self.modified_users: list[int | str] = []
        self.modified_submissions: list[int | str] = []
        self.modified_journals: list[int | str] = []
        self.user_errors: list[str] = []
        self.user_deactivated: list[str] = []
        self.submission_errors: list[int] = []
        self.file_errors: list[int] = []
        self.thumbnail_errors: list[int] = []
        self.journal_errors: list[int] = []

    # noinspection DuplicatedCode
    def report(self):
        items: list[tuple[str, int]] = [
            ("Added users", len(set(self.added_users))),
            ("Added submissions", len(set(self.added_submissions))),
            ("Added journals", len(set(self.added_journals))),
            ("Modified users", len(self.modified_users)),
            ("Modified submissions", len(self.modified_submissions)),
            ("Modified journals", len(self.modified_journals)),
            ("Users deactivated", len(self.user_deactivated)),
            ("User errors", len(self.user_errors)),
            ("Submission errors", len(self.submission_errors)),
            ("File errors", len(self.file_errors)),
            ("Thumbnail errors", len(self.thumbnail_errors)),
            ("Journal Errors", len(self.journal_errors)),
        ]
        if items := list(filter(itemgetter(1), items)):
            name_padding: int = max(map(len, map(itemgetter(0), items or [""])))
            for name, value in items:
                echo(f"{blue}{name:<{name_padding}}{reset}: {yellow}{value}{reset}", color=self.color)

    def verbose_report(self, file: TextIO | None = None):
        if file:
            dump({"users": {
                "added": sort_set(self.added_users),
                "modified": sort_set(self.modified_users),
                "errors": sort_set(self.user_errors),
                "deactivated": sort_set(self.user_deactivated),
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
        if self.output == OutputType.simple:
            return
        self.bar().update(total, level)

    def bar_message(self, message: str, color: str = "", *, always: bool = False):
        if self.output == OutputType.simple:
            if always:
                echo(message)
            return
        self.bar().message(message, color)

    def bar_close(self, end: str = "\n"):
        if self._bar is None or self.output == OutputType.simple:
            return
        self.bar().close(end)
        self._bar = None

    def bar_clear(self):
        if self._bar is None or self.output == OutputType.simple:
            return
        self.bar().clear()

    def bar_delete(self):
        if self._bar is None or self.output == OutputType.simple:
            return
        self.bar().delete()

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

    def download_submission(self, submission_id: int, user_update: int, favorites: Iterable[str] | None,
                            thumbnail: str, replace: bool = False) -> int:
        self.bar_clear()
        self.bar_message("DOWNLOAD")
        result, err = download_catch(self.api.submission, submission_id)
        if self.err_to_bar(err):
            self.submission_errors += [submission_id]
            return err
        submission, _ = result
        self.bar_clear()
        self.bar_close("\b")
        self.bar(7)
        file: bytes | None = self.download_bytes(submission.file_url)
        self.bar_message(("#" * self.bar_width) if file else "ERROR", green if file else red, always=True)
        self.bar_close("]")
        self.bar(1)
        thumb: bytes | None = self.download_bytes(submission.thumbnail_url or thumbnail)
        self.db.submissions.save_submission({**format_entry(dict(submission), self.db.submissions.columns),
                                             "author": submission.author.name,
                                             SubmissionsColumns.FAVORITE.value.name: {*favorites} if favorites else {},
                                             SubmissionsColumns.USERUPDATE.value.name: int(user_update)},
                                            file, thumb, replace=replace)
        self.db.commit()
        self.bar_message(("#" * self.bar_width) if thumb else "ERROR", green if thumb else red, always=True)
        self.bar_close()
        self.added_submissions += [submission_id]
        self.file_errors += [] if file else [submission_id]
        self.thumbnail_errors += [] if thumb else [submission_id]
        return 0

    # noinspection DuplicatedCode
    def download_user_journals(self, user: str, stop: int = -1, clear_last_found: bool = False) -> int:
        page: int = 1
        while page:
            page_width: int = len(str(page))
            page_id_width: int = page_width + 4 + 10
            folder_page_width: int = len(user) + 1 + len(Folder.journals.name) + 1 + page_width
            padding: int = (w - folder_page_width - self.bar_width - 2 - 1) if (w := terminal_width()) else 0
            echo(f"{yellow}{user}{reset}/{yellow}{Folder.journals.name}{reset} {page}" + (" " * padding),
                 nl=self.output == OutputType.simple, color=self.color)
            self.bar()
            self.bar_message("DOWNLOAD")
            result, err = download_catch(self.api.journals, user, page)
            if err:
                self.user_errors += [user]
                self.err_to_bar(err)
                return err
            self.bar_close("")
            self.clear_line()
            journals, next_page = result
            for i, journal in enumerate(journals, 1):
                title_width: int = w - page_id_width - 1 - self.bar_width - 2 - 1 - 1 if (w := terminal_width()) else 0
                echo(("\r" * (self.output == OutputType.rich)) + f"{page}/{i:02} {blue}{journal.id:010}{reset} " +
                     fit_string(clean_string(journal.title), title_width).ljust(title_width) + " ",
                     nl=self.output == OutputType.simple, color=self.color)
                self.bar()
                self.bar_message("SEARCHING")
                if journal.id in self.db.journals:
                    self.bar_message("IN DB", green, always=True)
                    if self.dry_run:
                        stop -= 1
                        if clear_last_found:
                            self.bar_close("")
                            self.clear_line()
                        else:
                            self.bar_close()
                    elif self.db.journals.set_user_update(journal.id, 1):
                        self.db.commit()
                        self.bar_message("UPDATED", green, always=True)
                        self.modified_journals += [journal.id]
                    else:
                        stop -= 1
                        if clear_last_found:
                            self.bar_close("")
                            self.clear_line()
                        else:
                            self.bar_close()
                elif self.dry_run:
                    self.bar_message("SKIPPED", green)
                    self.bar_close()
                else:
                    self.db.journals.save_journal({
                        **format_entry(dict(journal) | {"author": journal.author.name}, self.db.journals.columns),
                        JournalsColumns.USERUPDATE.value.name: 1,
                    })
                    self.db.commit()
                    self.bar_message("#" * self.bar_width, green)
                    self.bar_close()
                    self.added_journals += [journal.id]
                if stop == 0:
                    return 0
            page = next_page

    # noinspection DuplicatedCode
    def download_user_submissions_folder(self, user: str, folder: Folder, stop: int = -1,
                                         clear_last_found: bool = False) -> int:
        page: int = 0
        next_page: int | str = "/" if folder == Folder.favorites else 1
        downloader: _FolderDownloader = get_downloader(self.api, folder)
        while next_page:
            page += 1
            page_width: int = len(str(page))
            page_id_width: int = page_width + 4 + 10
            folder_page_width: int = len(user) + 1 + len(folder.name) + 1 + page_width
            padding: int = (w - folder_page_width - self.bar_width - 2 - 1) if (w := terminal_width()) else 0
            echo(f"{yellow}{user}{reset}/{yellow}{folder.name}{reset} {page}" + (" " * padding),
                 nl=self.output == OutputType.simple, color=self.color)
            self.bar()
            self.bar_message("DOWNLOAD")
            result, err = download_catch(downloader, user, next_page)
            if err:
                self.user_errors += [user]
                self.err_to_bar(err)
                return err
            self.bar_close("")
            self.clear_line()
            submissions, next_page = result
            for i, sub_partial in enumerate(submissions, 1):
                title_width: int = w - page_id_width - 1 - self.bar_width - 2 - 1 - 1 if (w := terminal_width()) else 0
                echo(('\r' * (self.output == OutputType.rich)) + f"{page}/{i:02} {blue}{sub_partial.id:010}{reset} " +
                     fit_string(clean_string(sub_partial.title), title_width).ljust(title_width) + " ",
                     nl=self.output == OutputType.simple, color=self.color)
                self.bar()
                self.bar_message("SEARCHING")
                if sub_partial.id in self.db.submissions:
                    self.bar_message("IN DB", green, always=True)
                    if self.dry_run:
                        stop -= 1
                        if clear_last_found and stop == 0:
                            self.bar_close("")
                            self.clear_line()
                        else:
                            self.bar_close()
                    elif folder != Folder.favorites and self.db.submissions.set_user_update(sub_partial.id, 1):
                        self.db.commit()
                        self.bar_message("UPDATED", green, always=True)
                        self.modified_submissions += [sub_partial.id]
                        self.bar_close()
                    elif folder == Folder.favorites and self.db.submissions.add_favorite(sub_partial.id, user):
                        self.db.commit()
                        self.bar_message("ADDED FAV", green, always=True)
                        self.modified_submissions += [sub_partial.id]
                        self.bar_close()
                    else:
                        stop -= 1
                        if clear_last_found and stop == 0:
                            self.bar_close("")
                            self.clear_line()
                        else:
                            self.bar_close()
                elif self.dry_run:
                    self.bar_message("SKIPPED", green)
                    self.bar_close()
                else:
                    self.download_submission(sub_partial.id, int(folder != Folder.favorites),
                                             [user] if folder == Folder.favorites else None, sub_partial.thumbnail_url)
                if stop == 0:
                    return 0
            self.clear_line()

    def download_user_page(self, username: str, clear_found: bool = False) -> int:
        padding: int = w - self.bar_width - 2 - 1 if (w := terminal_width()) else 0
        echo(f"{yellow}{username[:padding or None]:<{padding}}{reset}", nl=self.output == OutputType.simple)
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
        self.added_users += [username] if added else []
        self.modified_users += [username] if updated else []
        self.bar_message("ADDED" if added else "UPDATED", green, always=True)
        return 0

    def _download_users(self, users_folders: Iterable[tuple[str, list[str]]], stop: int = -1):
        operation: str = "Downloading" if stop < 0 else "Updating"
        for user, folders in users_folders:
            for folder in folders:
                echo(f"{operation}: {yellow}{user}{reset}/{yellow}{folder}{reset}", color=self.color)
                user_added: bool = False
                if not self.dry_run:
                    if user_added := user not in self.db.users:
                        self.db.users.save_user({UsersColumns.USERNAME.value.name: user,
                                                 UsersColumns.FOLDERS.value.name: {},
                                                 UsersColumns.USERPAGE.value.name: ""})
                        self.db.commit()
                        self.added_users += [user]
                    self.db.users.activate(user)
                    self.db.users.add_folder(user, folder)
                err: int
                if folder == Folder.userpage:
                    err = self.download_user_page(user, stop == 1)
                elif folder == Folder.journals:
                    err = self.download_user_journals(user, stop, stop == 1)
                else:
                    err = self.download_user_submissions_folder(user, Folder[folder.lower()], stop, stop == 1)
                if err in (1, 2):
                    if self.dry_run:
                        pass
                    elif user_added:
                        del self.db.users[user]
                        self.added_users.remove(user)
                    elif err == 2:
                        self.db.users.deactivate(user)
                        self.user_deactivated += [user]
                    self.db.commit()
                    break
                self.bar_close()
                self.db.commit()

    def download_users(self, users: list[str], folders: list[str]):
        self._download_users([(u, folders) for u in users])

    def download_users_update(self, users: list[str], folders: list[str], stop: int, deactivated: bool):
        users_cursor: Iterable[dict] = self.db.users[users] if users else self.db.users.select(
            order=[UsersColumns.USERNAME.value.name])
        users_folders: Iterable[tuple[str, list[str]]]
        users_folders = ((u[UsersColumns.USERNAME.value.name],
                          [f for f in u[UsersColumns.FOLDERS.value.name]])
                         for u in users_cursor)

        users_folders = sorted(users_folders, key=lambda uf: users.index(uf[0]) if users else uf[0])

        if deactivated:
            users_folders = ((u, [*map(lambda f: f.strip("!"), fs)]) for u, fs in users_folders)
        else:
            users_folders = ((u, fs) for u, fs in users_folders if not any("!" in f for f in fs))

        if folders:
            users_folders = ((u, sorted(filter(folders.__contains__, fs), key=folders.index))
                             for u, fs in users_folders)
        else:
            users_folders = ((u, sorted(fs, key=Folder.as_list().index)) for u, fs in users_folders)

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
                                     entry.get(SubmissionsColumns.USERUPDATE.value.name, 0),
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
            self.db.journals.save_journal({
                **format_entry(dict(journal), self.db.journals.columns),
                "author": journal.author.name,
                (u := JournalsColumns.USERUPDATE.value.name): entry.get(u, 0)
            }, replace=replace)
            self.added_journals += [journal.id]
            self.db.commit()
            self.bar_message("#" * self.bar_width, green, always=True)
            self.bar_close()
