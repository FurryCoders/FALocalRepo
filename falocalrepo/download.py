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
from faapi import Sub
from faapi import SubPartial
from filetype import guess_extension

from .database import Connection
from .database import insert
from .database import keys_submissions
from .database import keys_users
from .database import select
from .database import tiered_path
from .database import update
from .settings import setting_read


def cookies_load(api: FAAPI, cookie_a: str, cookie_b: str):
    api.load_cookies([
        {"name": "a", "value": cookie_a},
        {"name": "b", "value": cookie_b},
    ])


def user_clean_name(user: str) -> str:
    return str(re_sub(r"[^a-zA-Z0-9\-.~,]", "", user.lower().strip()))


def user_check(db: Connection, user: str, field: str, value: str) -> bool:
    field_value: List[str] = select(db, "USERS", [field], "USERNAME", user)[0][0].split(",")

    return value in filter(len, field_value)


def user_add(db: Connection, user: str, field: str, add_value: str):
    field_old: List[str] = select(db, "USERS", [field], "USERNAME", user)[0][0].split(",")
    field_old = list(filter(len, field_old))

    if add_value in field_old:
        return

    update(db, "USERS", [field], [",".join(field_old + [add_value])], "USERNAME", user)

    db.commit()


def user_new(db: Connection, user: str):
    insert(db, "USERS", keys_users, [user] + [""] * (len(keys_users) - 1), replace=False)
    db.commit()


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

    if not sub.id:
        return False

    submission_save(db, sub, sub_file)

    return True


def user_download(api: FAAPI, db: Connection, user: str, folder: str, stop: int = 0) -> Tuple[int, int]:
    subs_total: int = 0
    subs_failed: int = 0
    page: Union[int, str] = 1
    page_n: int = 0
    user = user_clean_name(user)
    space_term: int = get_terminal_size()[0]
    space_title: int = space_term - 14 - 17
    found_subs: int = 0

    downloader: Callable[[str, Union[str, int]], Tuple[List[SubPartial], Union[int, str]]] = lambda *x: ([], 0)
    if folder == "gallery":
        downloader = api.gallery
    elif folder == "scraps":
        downloader = api.scraps
    elif folder == "favorites":
        page = "next"
        downloader = api.favorites

    user_new(db, user)
    user_add(db, user, "FOLDERS", folder.lower())

    while page:
        page_n += 1
        print(f"{page_n:02d}    {user[:37]} ...", end="", flush=True)
        user_subs, page = downloader(user, page)
        if not user_subs:
            print("\r" + (" " * 31), end="\r", flush=True)
        for i, sub in enumerate(user_subs, 1):
            print(f"\r{page_n:02d}/{i:02d} {sub.id:010d} {sub.title[:space_title]:<{space_title}} ", end="",
                  flush=True)
            if not sub.id:
                subs_failed += 1
                print(f"[{'ID ERROR':^10}]")
            elif user_check(db, user, folder.upper(), str(sub.id).zfill(10)):
                print(f"[{'FOUND':^10}]")
                if stop and (found_subs := found_subs + 1) >= stop:
                    return subs_total, subs_failed
            elif submission_download(api, db, sub.id):
                user_add(db, user, folder.upper(), str(sub.id).zfill(10))
                subs_total += 1
                print()

    return subs_total, subs_failed
