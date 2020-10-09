from datetime import datetime
from json import dumps as json_dumps
from json import loads as json_loads
from math import log10
from os import get_terminal_size
from re import sub as re_sub
from sqlite3 import Connection
from time import sleep
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from faapi import FAAPI
from faapi import Journal
from faapi import SubmissionPartial
from falocalrepo_database import edit_user_field_add
from falocalrepo_database import edit_user_field_remove
from falocalrepo_database import exist_journal
from falocalrepo_database import exist_submission
from falocalrepo_database import exist_user_field_value
from falocalrepo_database import new_user
from falocalrepo_database import read_setting
from falocalrepo_database import save_journal
from falocalrepo_database import save_submission
from falocalrepo_database import select_all
from falocalrepo_database import write_setting


class UnknownFolder(Exception):
    pass


def cookies_load(api: FAAPI, cookie_a: str, cookie_b: str):
    api.load_cookies([
        {"name": "a", "value": cookie_a},
        {"name": "b", "value": cookie_b},
    ])


def cookies_read(db: Connection) -> Tuple[str, str]:
    cookies: Dict[str, str] = json_loads(read_setting(db, "COOKIES"))
    return cookies.get("a", ""), cookies.get("b", "")


def cookies_write(db: Connection, a: str, b: str):
    write_setting(db, "COOKIES", json_dumps({"a": a, "b": b}))


def clean_username(username: str) -> str:
    return str(re_sub(r"[^a-zA-Z0-9\-.~,]", "", username.lower().strip()))


def clean_string(title: str) -> str:
    return str(re_sub(r"[^\x20-\x7E]", "", title.strip()))


def download_submission_file(api: FAAPI, sub_file_url: str, speed: int = 100) -> Optional[bytes]:
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


def download_submissions(api: FAAPI, db: Connection, sub_ids: List[str]):
    if sub_ids_fail := list(filter(lambda i: not i.isdigit(), sub_ids)):
        print("The following ID's are not correct:", *sub_ids_fail)
    for sub_id in map(int, filter(lambda i: i.isdigit(), sub_ids)):
        print(f"Downloading {sub_id:010} ", end="", flush=True)
        download_submission(api, db, sub_id)


def download_submission(api: FAAPI, db: Connection, sub_id: int) -> bool:
    sub, _ = api.get_sub(sub_id, False)
    sub_file: bytes = bytes()

    try:
        sub_file = download_submission_file(api, sub.file_url)
    except KeyboardInterrupt:
        raise
    except (Exception, BaseException):
        pass
    finally:
        print()

    if not sub.id:
        return False

    save_submission(db, dict(sub), sub_file)

    return True


def download_journals(api: FAAPI, db: Connection, jrn_ids: List[str]):
    if sub_ids_fail := list(filter(lambda i: not i.isdigit(), jrn_ids)):
        print("The following ID's are not correct:", *sub_ids_fail)
    for sub_id in map(int, filter(lambda i: i.isdigit(), jrn_ids)):
        print(f"Downloading {sub_id:010} ", end="", flush=True)
        download_journal(api, db, sub_id)


def download_journal(api: FAAPI, db: Connection, jrn_id: int):
    journal: Journal = api.get_journal(jrn_id)
    save_journal(db, dict(journal))


def download_users_update(api: FAAPI, db: Connection, users: List[str] = None, folders: List[str] = None, stop: int = 1):
    tot: int = 0
    fail: int = 0
    for user, user_folders in select_all(db, "USERS", ["USERNAME", "FOLDERS"]):
        if users and user not in users:
            continue
        elif any(folder.startswith("!") for folder in user_folders.split(",")):
            print(f"User {user} disabled")
            continue
        elif (user_exists := api.user_exists(user)) != 0:
            if user_exists == 1:
                print(f"User {user} disabled")
                edit_user_field_remove(db, user, "FOLDERS", ["gallery", "scraps", "journals"])
                edit_user_field_add(db, user, "FOLDERS", ["!gallery", "!scraps", "!journals"])
            elif user_exists == 2:
                print(f"User {user} not found")
            else:
                print(f"User {user} error {user_exists}")
            continue
        for folder in user_folders.split(","):
            if folders and folder not in folders:
                continue
            print(f"Downloading: {user}/{folder}")
            tot_tmp, fail_tmp = download_user(api, db, user, folder, stop)
            tot += tot_tmp
            fail += fail_tmp
    print("Items downloaded:", tot)
    print("Items failed:", fail) if fail else None
    write_setting(db, "LASTUPDATE", str(datetime.now().timestamp()))


def download_users(api: FAAPI, db: Connection, users: List[str], folders: List[str]):
    for user, folder in ((u, f) for u in users for f in folders):
        print(f"Downloading: {user}/{folder}")
        if (user_exists := api.user_exists(user)) != 0:
            if user_exists == 1:
                print(f"User {user} disabled")
            elif user_exists == 2:
                print(f"User {user} not found")
            else:
                print(f"User {user} error {user_exists}")
            continue
        tot, fail = download_user(api, db, user, folder)
        print("Items downloaded:", tot)
        print("Items failed:", fail) if fail else None


def download_user(api: FAAPI, db: Connection, user: str, folder: str, stop: int = 0) -> Tuple[int, int]:
    items_total: int = 0
    items_failed: int = 0
    items_type: str = "sub"
    page: Union[int, str] = 1
    page_n: int = 0
    user = clean_username(user)
    space_term: int = get_terminal_size()[0]
    found_subs: int = 0

    downloader: Callable[
        [str, Union[str, int]],
        Tuple[Union[List[SubmissionPartial], List[Journal]], Union[int, str]]
    ]
    if folder.endswith("!"):
        print(f"{folder} disabled")
        return 0, 0
    elif folder.startswith("mentions"):
        print(f"Unsupported: {user}/{folder}")
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
        raise UnknownFolder(folder)

    new_user(db, user)
    edit_user_field_add(db, user, "FOLDERS", [folder.lower()])

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
                f"{clean_string(item.title)[:space_title]:<{space_title}} ",
                end="",
                flush=True
            )
            if not item.id:
                items_failed += 1
                print(f"[{'ID ERROR':^10}]")
            elif exist_user_field_value(db, user, folder.upper(), str(item.id).zfill(10)):
                print(f"[{'FOUND':^10}]")
                if stop and (found_subs := found_subs + 1) >= stop:
                    return items_total, items_failed
            elif items_type == "sub" and exist_submission(db, item.id):
                print(f"[{'FOUND':^10}]")
                edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
            elif items_type == "sub" and download_submission(api, db, item.id):
                edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
                items_total += 1
            elif items_type == "journal" and exist_journal(db, item.id):
                print(f"[{'FOUND':^10}]")
                edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
            elif items_type == "journal":
                print(f"[{'#' * 10}]")
                save_journal(db, dict(item))
                edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
                items_total += 1

    return items_total, items_failed
