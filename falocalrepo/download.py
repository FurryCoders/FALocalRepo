from json import dumps as json_dumps
from json import loads as json_loads
from math import log10
from os import get_terminal_size
from time import sleep
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from faapi import FAAPI
from faapi import Journal
from faapi import Submission
from faapi import SubmissionPartial
from falocalrepo_database import FADatabase

from .commands import Bar
from .commands import clean_string
from .commands import clean_username


class UnknownFolder(Exception):
    pass


def read_cookies(db: FADatabase) -> List[Dict[str, str]]:
    return [{"name": n, "value": v} for n, v in json_loads(db.settings["COOKIES"]).items()]


def write_cookies(db: FADatabase, a: str, b: str):
    db.settings["COOKIES"] = json_dumps({"a": a, "b": b})
    db.commit()


def load_api(db: FADatabase) -> FAAPI:
    print((s := "Connecting... "), end="", flush=True)
    api: FAAPI = FAAPI(read_cookies(db))
    print("\r" + (" " * len(s)), end="\r", flush=True)

    if not api.connection_status:
        raise ConnectionError("FAAPI cannot connect to FA")

    return api


def download_items(db: FADatabase, item_ids: List[str], f: Callable[[FAAPI, FADatabase, int], Any]):
    if item_ids_fail := list(filter(lambda i: not i.isdigit(), item_ids)):
        print("The following ID's are not correct:", *item_ids_fail)
    item_ids = list(filter(lambda i: i.isdigit(), item_ids))
    api: Optional[FAAPI] = load_api(db) if item_ids else None
    for item_id in map(int, filter(lambda i: i.isdigit(), item_ids)):
        print(f"Downloading {item_id:010} ", end="", flush=True)
        f(api, db, item_id)


def download_submissions(db: FADatabase, sub_ids: List[str]):
    download_items(db, sub_ids, download_submission)


def download_submission(api: FAAPI, db: FADatabase, sub_id: int) -> bool:
    sub, _ = api.get_submission(sub_id, False)
    sub_file: bytes = bytes()

    try:
        sub_file = download_submission_file(api, sub.file_url)
    except KeyboardInterrupt:
        raise
    except (Exception, BaseException):
        pass

    if not sub.id:
        return False

    save_submission(db, sub, sub_file)

    return True


def download_submission_file(api: FAAPI, sub_file_url: str, speed: int = 100) -> Optional[bytes]:
    bar: Bar = Bar(10)

    try:
        if not (file_stream := api.session.get(sub_file_url, stream=True)).ok:
            file_stream.raise_for_status()

        size: int = int(file_stream.headers.get("Content-Length", 0))
        file_binary: Optional[bytes] = bytes()

        if not size:
            file_binary = file_stream.content
        else:
            for chunk in file_stream.iter_content(chunk_size=1024):
                file_binary += chunk
                bar.update(size, len(file_binary)) if size else None
                sleep(1 / speed) if speed > 0 else None

        bar.update(1, 1)

        file_stream.close()

        return file_binary
    except KeyboardInterrupt:
        print("\b\b  \b\b", end="")
        bar.delete()
        bar.__init__(bar.length)
        bar.message("INTERRUPT")
        raise
    except (Exception, BaseException):
        bar.message("FILE ERR")
        return None
    finally:
        bar.close()


def save_submission(db: FADatabase, sub: Submission, sub_file: Optional[bytes]):
    sub_dict: dict = dict(sub)
    sub_dict["FILELINK"] = sub_dict["file_url"]
    del sub_dict["file_url"]
    sub_dict["tags"] = ",".join(sorted(sub_dict["tags"], key=str.lower))
    db.submissions.save_submission(sub_dict, sub_file)
    db.commit()


def download_journals(db: FADatabase, jrn_ids: List[str]):
    download_items(db, jrn_ids, download_journal)


def download_journal(api: FAAPI, db: FADatabase, jrn_id: int):
    journal: Journal = api.get_journal(jrn_id)
    db.journals.save_journal(dict(journal))


def download_users_update(db: FADatabase, users: List[str], folders: List[str], stop: int = 1):
    tot: int = 0
    fail: int = 0
    api: Optional[FAAPI] = None
    for user, user_folders_str in db.users.select(columns=["USERNAME", "FOLDERS"], order=["USERNAME"]):
        user_folders: List[str] = sorted(user_folders_str.split(","))
        if users and user not in users:
            continue
        elif folders and not any(f in folders for f in user_folders):
            continue
        elif any(folder.startswith("!") for folder in user_folders):
            print(f"User {user} disabled")
            continue

        api = load_api(db) if api is None else api
        if (user_exists := api.user_exists(user)) != 0:
            if user_exists == 1:
                print(f"User {user} disabled")
                db.users.disable_user(user)
                db.commit()
            elif user_exists == 2:
                print(f"User {user} not found")
            else:
                print(f"User {user} error {user_exists}")
            continue
        user_folders = [f for f in folders if f in user_folders] if folders else user_folders
        if not user_folders:
            print(f"User {user} no folders selected")
        for folder in user_folders:
            print(f"Downloading: {user}/{folder}")
            tot_tmp, fail_tmp = download_user(api, db, user, folder, stop)
            tot += tot_tmp
            fail += fail_tmp
    print("Items downloaded:", tot)
    print("Items failed:", fail) if fail else None


def download_users(db: FADatabase, users: List[str], folders: List[str]):
    api: Optional[FAAPI] = None
    for user, folder in ((u, f) for u in users for f in folders):
        api = load_api(db) if api is None else api
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


def download_user(api: FAAPI, db: FADatabase, user: str, folder: str, stop: int = 0) -> Tuple[int, int]:
    items_total: int = 0
    items_failed: int = 0
    page: Union[int, str] = 1
    page_n: int = 0
    user = clean_username(user)
    space_bar: int = 10
    space_term: int = get_terminal_size()[0]
    space_line: int = space_term - (space_bar + 2 + 2)
    found_items: int = 0
    skip: bool = False

    download: Callable[[str, Union[str, int]], Tuple[List[Union[SubmissionPartial, Journal]], Union[int, str]]]
    exists: Callable[[int], bool]

    if folder.startswith("!"):
        print(f"{user}/{folder} disabled")
        return 0, 0
    elif folder in ("mentions", "mentions_all", "list-mentions", "list-mentions_all"):
        print(f"Unsupported: {user}/{folder}")
        return 0, 0
    elif folder in ("gallery", "list-gallery"):
        download = api.gallery
        exists = db.submissions.__contains__
    elif folder in ("scraps", "list-scraps"):
        download = api.scraps
        exists = db.submissions.__contains__
    elif folder in ("favorites", "list-favorites"):
        page = "next"
        download = api.favorites
        exists = db.submissions.__contains__
    elif folder in ("journals", "list-journals"):
        download = api.journals
        exists = db.journals.__contains__
    else:
        raise UnknownFolder(folder)

    if folder.startswith("list-"):
        skip = True
        folder = folder[5:]  # remove list- prefix
    else:
        db.users.new_user(user)
        db.users.add_user_folder(user, folder)
        db.commit()

    while page:
        page_n += 1
        print(f"{page_n}    {user[:space_term - int(log10(page_n)) - 8 - 1]} ...", end="", flush=True)
        items, page = download(user, page)
        print("\r" + (" " * (space_term - 1)), end="\r", flush=True)
        for i, item in enumerate(items, 1):
            sub_string: str = f"{page_n}/{i:02d} {item.id:010d} {clean_string(item.title)}"
            print(f"{sub_string[:space_line]:<{space_line}} ", end="", flush=True)
            bar: Bar = Bar(space_bar)
            if not item.id:
                items_failed += 1
                bar.message("ID ERROR")
                bar.close()
            elif str(item.id).zfill(10) in db.users[user][folder.upper()]:
                if stop and (found_items := found_items + 1) >= stop:
                    print("\r" + (" " * (space_term - 1)), end="\r", flush=True)
                    return items_total, items_failed
                bar.message("IS IN DB")
                bar.close()
            elif exists(item.id):
                bar.message("IS IN DB")
                db.users.add_item(user, folder, str(item.id).zfill(10))
                db.commit()
                bar.close()
            elif skip:
                bar.message("SKIPPED")
                bar.close()
            elif isinstance(item, SubmissionPartial):
                bar.delete()
                if download_submission(api, db, item.id):
                    db.users.add_submission(user, folder, item.id)
                    db.commit()
                    items_total += 1
            elif isinstance(item, Journal):
                db.journals.save_journal(dict(item))
                db.users.add_journal(user, item.id)
                db.commit()
                bar.update(1, 1)
                bar.close()
                items_total += 1

    return items_total, items_failed
