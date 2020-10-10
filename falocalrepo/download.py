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

from .commands import Bar


class UnknownFolder(Exception):
    pass


def load_cookies(api: FAAPI, cookie_a: str, cookie_b: str):
    api.load_cookies([
        {"name": "a", "value": cookie_a},
        {"name": "b", "value": cookie_b},
    ])


def read_cookies(db: Connection) -> Tuple[str, str]:
    cookies: Dict[str, str] = json_loads(read_setting(db, "COOKIES"))
    return cookies.get("a", ""), cookies.get("b", "")


def write_cookies(db: Connection, a: str, b: str):
    write_setting(db, "COOKIES", json_dumps({"a": a, "b": b}))


def clean_username(username: str) -> str:
    return str(re_sub(r"[^a-zA-Z0-9\-.~,]", "", username.lower().strip()))


def clean_string(title: str) -> str:
    return str(re_sub(r"[^\x20-\x7E]", "", title.strip()))


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

    if not sub.id:
        return False

    save_submission(db, dict(sub), sub_file)

    return True


def download_submission_file(api: FAAPI, sub_file_url: str, speed: int = 100) -> Optional[bytes]:
    bar: Bar = Bar(10)

    try:
        if not (file_stream := api.session.get(sub_file_url, stream=True)).ok:
            file_stream.raise_for_status()

        size: int = int(file_stream.headers.get("Content-Length", 0))
        file_binary = bytes()

        for chunk in file_stream.iter_content(chunk_size=1024):
            file_binary += chunk
            bar.update(size, len(file_binary)) if size else None
            sleep(1 / speed) if speed > 0 else None

        bar.update(1, 1)

        file_stream.close()

        return file_binary
    except KeyboardInterrupt:
        print("\b\b  \b\b", end="")
        bar.message("INTERRUPT")
        raise
    except (Exception, BaseException):
        bar.message("FILE ERR")
        return None
    finally:
        bar.close()


def download_journals(api: FAAPI, db: Connection, jrn_ids: List[str]):
    if sub_ids_fail := list(filter(lambda i: not i.isdigit(), jrn_ids)):
        print("The following ID's are not correct:", *sub_ids_fail)
    for sub_id in map(int, filter(lambda i: i.isdigit(), jrn_ids)):
        print(f"Downloading {sub_id:010} ", end="", flush=True)
        download_journal(api, db, sub_id)


def download_journal(api: FAAPI, db: Connection, jrn_id: int):
    journal: Journal = api.get_journal(jrn_id)
    save_journal(db, dict(journal))


def download_users_update(api: FAAPI, db: Connection, users: List[str], folders: List[str], stop: int = 1):
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
    page: Union[int, str] = 1
    page_n: int = 0
    user = clean_username(user)
    space_term: int = get_terminal_size()[0]
    found_items: int = 0

    download: Callable[[str, Union[str, int]], Tuple[List[Union[SubmissionPartial, Journal]], Union[int, str]]]
    exists: Callable[[Connection, int], bool]

    if folder.startswith("!"):
        print(f"{folder} disabled")
        return 0, 0
    elif folder.startswith("mentions"):
        print(f"Unsupported: {user}/{folder}")
        return 0, 0
    elif folder == "gallery":
        download = api.gallery
        exists = exist_submission
    elif folder == "scraps":
        download = api.scraps
        exists = exist_submission
    elif folder == "favorites":
        page = "next"
        download = api.favorites
        exists = exist_submission
    elif folder == "journals":
        download = api.journals
        exists = exist_journal
    else:
        raise UnknownFolder(folder)

    new_user(db, user)
    edit_user_field_add(db, user, "FOLDERS", [folder.lower()])

    while page:
        page_n += 1
        space_title: int = space_term - 29 - int(log10(page_n)) - 1
        print(f"{page_n}    {user[:space_title]} ...", end="", flush=True)
        items, page = download(user, page)
        if not items:
            print("\r" + (" " * (space_term - 1)), end="\r", flush=True)
        for i, item in enumerate(items, 1):
            print(
                f"\r{page_n}/{i:02d} {item.id:010d} {clean_string(item.title)[:space_title]:<{space_title}} ",
                end="",
                flush=True
            )
            bar: Bar = Bar(10)
            if not item.id:
                items_failed += 1
                bar.message("ID ERROR")
                bar.close()
            elif exist_user_field_value(db, user, folder.upper(), str(item.id).zfill(10)):
                bar.message("IS IN DB")
                bar.close()
                if stop and (found_items := found_items + 1) >= stop:
                    return items_total, items_failed
            elif exists(db, item.id):
                bar.message("IS IN DB")
                bar.close()
                edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
            elif isinstance(item, SubmissionPartial):
                bar.delete()
                if download_submission(api, db, item.id):
                    edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
                    items_total += 1
            elif isinstance(item, Journal):
                save_journal(db, dict(item))
                bar.update(1, 1)
                bar.close()
                edit_user_field_add(db, user, folder.upper(), [str(item.id).zfill(10)])
                items_total += 1

    return items_total, items_failed
