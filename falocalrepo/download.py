from datetime import datetime
from math import log10
from os import get_terminal_size
from os import makedirs
from os.path import join as path_join
from re import sub as re_sub
from time import sleep
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from faapi import FAAPI
from faapi import Journal
from faapi import Sub
from faapi import SubPartial
from filetype import guess_extension

from .database import Connection
from .database import insert
from .database import keys_journals
from .database import keys_submissions
from .database import keys_users
from .database import select
from .database import select_all
from .database import tiered_path
from .database import update
from .settings import setting_read
from .settings import setting_write


class UnknownFolder(Exception):
    pass


def cookies_load(api: FAAPI, cookie_a: str, cookie_b: str):
    api.load_cookies([
        {"name": "a", "value": cookie_a},
        {"name": "b", "value": cookie_b},
    ])


def user_clean_name(user: str) -> str:
    return str(re_sub(r"[^a-zA-Z0-9\-.~,]", "", user.lower().strip()))


def clean_title(title: str) -> str:
    return str(re_sub(r"[^\x20-\x7E]", "", title.strip()))


def user_check(db: Connection, user: str, field: str, value: str) -> bool:
    field_value: List[str] = select(db, "USERS", [field], "USERNAME", user).fetchone()[0].split(",")

    return value in filter(len, field_value)


def user_add(db: Connection, user: str, field: str, add_value: str):
    field_old: List[str] = select(db, "USERS", [field], "USERNAME", user).fetchone()[0].split(",")
    field_old = list(filter(len, field_old))

    if add_value in field_old:
        return

    update(db, "USERS", [field], [",".join(field_old + [add_value])], "USERNAME", user)

    db.commit()


def user_new(db: Connection, user: str):
    insert(db, "USERS", keys_users, [user] + [""] * (len(keys_users) - 1), replace=False)
    db.commit()


def submission_check(db: Connection, sub_id: int) -> bool:
    return bool(select(db, "SUBMISSIONS", ["ID"], "ID", sub_id).fetchone())


def submission_save(db: Connection, sub: Sub, sub_file: Optional[bytes]):
    sub_ext: str = ""

    if sub_file:
        if (sub_ext_tmp := guess_extension(sub_file)) is None:
            sub_filename = sub.file_url.split("/")[-1]
            if "." in sub_filename:
                sub_ext_tmp = sub.file_url.split(".")[-1]
        elif str(sub_ext_tmp) == "zip":
            sub_filename = sub.file_url.split("/")[-1]
            if "." in sub_filename:
                sub_ext_tmp = sub.file_url.split(".")[-1]
            else:
                sub_ext_tmp = None

        sub_ext = "" if sub_ext_tmp is None else f".{str(sub_ext_tmp)}"
        sub_folder: str = path_join(setting_read(db, "FILESFOLDER"), tiered_path(sub.id))

        makedirs(sub_folder, exist_ok=True)

        with open(path_join(sub_folder, "submission" + sub_ext), "wb") as f:
            f.write(sub_file)

    insert(db, "SUBMISSIONS",
           keys_submissions,
           [sub.id, sub.author, sub.title,
            sub.date, sub.description, ",".join(sorted(sub.tags, key=str.lower)),
            sub.category, sub.species, sub.gender,
            sub.rating, sub.file_url, sub_ext.lstrip("."),
            sub_file is not None],
           replace=True)

    db.commit()


def submission_download_file(api: FAAPI, sub_file_url: str, speed: int = 100) -> Optional[bytes]:
    bar_length: int = 10
    bar_pos: int = 0
    print("[" + (" " * bar_length) + "]", end=("\b" * bar_length) + "\b", flush=True)

    try:
        if not (file_stream := api.session.get(sub_file_url, stream=True)).ok:
            file_stream.raise_for_status()

        size: int = int(file_stream.headers.get("Content-Length", 0))
        file_binary = bytes()

        for chunk in file_stream.iter_content(chunk_size=1024):
            file_binary += chunk
            if size and len(file_binary) > (size / bar_length) * (bar_pos + 1):
                bar_pos += 1
                print("#", end="", flush=True)
            sleep(1 / speed) if speed > 0 else None

        print(("\b \b" * bar_pos) + "#" * bar_length, end="", flush=True)

        file_stream.close()

        return file_binary
    except KeyboardInterrupt:
        print("\b\b  \b\b", end="")
        print(("\b \b" * bar_pos) + f"{'CANCELLED':^{bar_length}}", end="", flush=True)
        raise
    except (Exception, BaseException):
        print(("\b \b" * bar_pos) + f"{'FILE ERR':^{bar_length}}", end="", flush=True)
        return None


def submission_download(api: FAAPI, db: Connection, sub_id: int) -> bool:
    sub, _ = api.get_sub(sub_id, False)
    sub_file: bytes = bytes()

    try:
        sub_file = submission_download_file(api, sub.file_url)
    except KeyboardInterrupt:
        raise
    except (Exception, BaseException):
        pass
    finally:
        print()

    if not sub.id:
        return False

    submission_save(db, sub, sub_file)

    return True


def journal_check(db: Connection, journal_id: int) -> bool:
    return bool(select(db, "JOURNALS", ["ID"], "ID", journal_id).fetchone())


def journal_save(db: Connection, journal: Journal):
    insert(db, "JOURNALS", keys_journals,
           [journal.id, journal.author, journal.title, journal.date, journal.content])


def users_download(api: FAAPI, db: Connection, users: List[str], folders: List[str]):
    for user, folder in ((u, f) for u in users for f in folders):
        print(f"Downloading: {user}/{folder}")
        tot, fail = user_download(api, db, user, folder)
        print("Items downloaded:", tot)
        print("Items failed:", fail) if fail else None


def users_update(api: FAAPI, db: Connection, users: List[str] = None, folders: List[str] = None, stop: int = 1):
    tot: int = 0
    fail: int = 0
    for user, user_folders in select_all(db, "USERS", ["USERNAME", "FOLDERS"]):
        if users and user not in users:
            continue
        for folder in user_folders.split(","):
            if folders and folder not in folders:
                continue
            if folder.lower().startswith("mentions"):
                print(f"Unsupported: {user}/{folder}")
                continue
            print(f"Downloading: {user}/{folder}")
            tot_tmp, fail_tmp = user_download(api, db, user, folder, stop)
            tot += tot_tmp
            fail += fail_tmp
    print("Items downloaded:", tot)
    print("Items failed:", fail) if fail else None
    setting_write(db, "LASTUPDATE", str(datetime.now().timestamp()))


def user_download(api: FAAPI, db: Connection, user: str, folder: str, stop: int = 0) -> Tuple[int, int]:
    items_total: int = 0
    items_failed: int = 0
    items_type: str = "sub"
    page: Union[int, str] = 1
    page_n: int = 0
    user = user_clean_name(user)
    space_term: int = get_terminal_size()[0]
    found_subs: int = 0

    downloader: Callable[
        [str, Union[str, int]],
        Tuple[Union[List[SubPartial], List[Journal]], Union[int, str]]
    ] = lambda *x: ([], 0)
    if folder.endswith("!"):
        print(f"{folder} disabled")
        return 0, 0
    elif folder == "gallery":
        downloader = api.gallery
    elif folder == "scraps":
        downloader = api.scraps
    elif folder == "favorites":
        page = "next"
        downloader = api.favorites
    elif folder == "journals":
        items_type = "journal"
        downloader = api.journals
    else:
        UnknownFolder(folder)

    user_new(db, user)
    user_add(db, user, "FOLDERS", folder.lower())

    while page:
        page_n += 1
        space_title: int = space_term - 29 - (int(log10(page_n)) + 1)
        print(f"{page_n}    {user[:space_title]} ...", end="", flush=True)
        items, page = downloader(user, page)
        if not items:
            print("\r" + (" " * 31), end="\r", flush=True)
        for i, item in enumerate(items, 1):
            print(
                f"\r{page_n}/{i:02d} {item.id:010d} " +
                f"{clean_title(item.title)[:space_title]:<{space_title}} ",
                end="",
                flush=True
            )
            if not item.id:
                items_failed += 1
                print(f"[{'ID ERROR':^10}]")
            elif user_check(db, user, folder.upper(), str(item.id).zfill(10)):
                print(f"[{'FOUND':^10}]")
                if stop and (found_subs := found_subs + 1) >= stop:
                    return items_total, items_failed
            elif items_type == "sub" and submission_check(db, item.id):
                print(f"[{'FOUND':^10}]")
                user_add(db, user, folder.upper(), str(item.id).zfill(10))
            elif items_type == "sub" and submission_download(api, db, item.id):
                user_add(db, user, folder.upper(), str(item.id).zfill(10))
                items_total += 1
            elif items_type == "journal" and journal_check(db, item.id):
                print(f"[{'FOUND':^10}]")
                user_add(db, user, folder.upper(), str(item.id).zfill(10))
            elif items_type == "journal":
                print(f"[{'#' * 10}]")
                journal_save(db, item)
                user_add(db, user, folder.upper(), str(item.id).zfill(10))
                items_total += 1

    return items_total, items_failed
