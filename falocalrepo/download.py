from json import dumps as json_dumps
from json import loads as json_loads
from math import log10
from os import get_terminal_size
from time import sleep
from typing import Any
from typing import Callable
from typing import Optional
from typing import Union

from faapi import DisabledAccount
from faapi import FAAPI
from faapi import Journal
from faapi import NoticeMessage
from faapi import ParsingError
from faapi import Submission
from faapi import SubmissionPartial
from falocalrepo_database import FADatabase
from urllib3.exceptions import IncompleteRead

from .commands import Bar
from .commands import clean_string
from .commands import clean_username


class UnknownFolder(Exception):
    pass


def read_cookies(db: FADatabase) -> list[dict[str, str]]:
    return [{"name": n, "value": v} for n, v in json_loads(db.settings["COOKIES"]).items()]


def write_cookies(db: FADatabase, **cookies):
    db.settings["COOKIES"] = json_dumps(cookies)
    db.commit()


def load_api(db: FADatabase) -> FAAPI:
    print((s := "Connecting... "), end="", flush=True)
    api: FAAPI = FAAPI(read_cookies(db))
    print("\r" + (" " * len(s)), end="\r", flush=True)

    if not api.connection_status:
        raise ConnectionError("FAAPI cannot connect to FA")

    return api


def download_items(db: FADatabase, item_ids: list[str], f: Callable[[FAAPI, FADatabase, int], Any]):
    if item_ids_fail := list(filter(lambda i: not i.isdigit(), item_ids)):
        print("The following ID's are not correct:", *item_ids_fail)
    item_ids = list(filter(lambda i: i.isdigit(), item_ids))
    api: Optional[FAAPI] = load_api(db) if item_ids else None
    for item_id in map(int, filter(lambda i: i.isdigit(), item_ids)):
        print(f"Downloading {item_id:010} ", end="", flush=True)
        f(api, db, item_id)


def save_submission(db: FADatabase, sub: Submission, sub_file: Optional[bytes], sub_thumb: Optional[bytes],
                    user_update: bool = False):
    db.submissions.save_submission({**dict(sub), "USERUPDATE": int(user_update)}, sub_file, sub_thumb)
    db.commit()


def download_submission_file(api: FAAPI, sub_file_url: str, *, speed: int = 100, bar: int = 10) -> Optional[bytes]:
    if not sub_file_url:
        return None

    bar: Bar = Bar(bar)
    file_binary: Optional[bytes] = bytes()

    try:
        with api.session.get(sub_file_url, stream=True) as file_stream:
            file_stream.raise_for_status()
            size: int = int(file_stream.headers.get("Content-Length", 0))
            if not size:
                file_binary = file_stream.content
            else:
                for chunk in file_stream.iter_content(chunk_size=1024):
                    file_binary += chunk
                    bar.update(size, len(file_binary)) if size else None
                    sleep(1 / speed) if speed > 0 else None

            if size and (l := len(file_binary)) != size:
                raise IncompleteRead(l, size - l)

            bar.update(1, 1)
    except KeyboardInterrupt:
        print("\b\b  \b\b", end="")
        bar.delete()
        bar.__init__(bar.length)
        bar.message("STOP")
        raise
    except (Exception, BaseException):
        bar.message("ERROR")
        file_binary = None
    finally:
        bar.close("]")

    return file_binary


def download_submission(api: FAAPI, db: FADatabase, submission: Union[int, SubmissionPartial], user_update: bool = False
                        ) -> bool:
    try:
        sub_id: int = submission.id if isinstance(submission, SubmissionPartial) else submission
        if sub_id in db.submissions:
            Bar(length=10, message="IS IN DB").close("]")
            return True
        sub: Submission = api.get_submission(sub_id, False)[0]
        if isinstance(submission, SubmissionPartial):
            sub.thumbnail_url = sub.thumbnail_url or submission.thumbnail_url
        save_submission(db, sub,
                        download_submission_file(api, sub.file_url, bar=7 if sub.thumbnail_url else 10),
                        download_submission_file(api, sub.thumbnail_url, speed=0, bar=1),
                        user_update)
        return True
    except ParsingError:
        return False
    finally:
        print()


def download_submissions(db: FADatabase, sub_ids: list[str]):
    download_items(db, sub_ids, download_submission)


def save_journal(db: FADatabase, journal: Journal, user_update: bool = False):
    db.journals.save_journal({**dict(journal), "USERUPDATE": int(user_update)})
    db.commit()


def download_journal(api: FAAPI, db: FADatabase, jrn_id: int):
    if jrn_id in db.journals:
        Bar(length=10, message="IS IN DB").close()
        return True
    journal: Journal = api.get_journal(jrn_id)
    save_journal(db, journal)


def download_journals(db: FADatabase, jrn_ids: list[str]):
    download_items(db, jrn_ids, download_journal)


def download_users_update(db: FADatabase, users: list[str], folders: list[str], stop: int = 1,
                          deactivated: bool = False):
    api: Optional[FAAPI] = None
    tot, fail = 0, 0

    users = list(map(clean_username, users))
    users = sorted(set(users), key=users.index)
    users_db: list[dict] = sorted(
        filter(lambda u: not users or u["USERNAME"] in users, db.users),
        key=lambda u: users.index(u["USERNAME"]) if users else u["USERNAME"])

    for user, user_folders in ((u["USERNAME"], u["FOLDERS"]) for u in users_db):
        if not (user_folders := [f for f in folders if f in user_folders] if folders else user_folders):
            continue
        elif not deactivated and any(folder.startswith("!") for folder in user_folders):
            print(f"User {user} deactivated")
            continue
        try:
            api = load_api(db) if api is None else api
            for folder in user_folders:
                print(f"Updating: {user}/{folder}")
                tot_, fail_ = download_user(api, db, user, folder.strip("!"), stop)
                tot += tot_
                fail += fail_
        except UnknownFolder as err:
            print(f"Unknown folder: {err.args[0]}")
            raise
        except DisabledAccount:
            print(f"User {user} deactivated")
            db.users.deactivate_user(user)
            db.commit()
        except NoticeMessage:
            print(f"User {user} not found")
        except ParsingError as err:
            print(f"User {user} error: {repr(err)}")
            continue

    print("Items downloaded:", tot)
    print("Items failed:", fail) if fail else None


def download_users(db: FADatabase, users: list[str], folders: list[str]):
    api: Optional[FAAPI] = None
    users = list(map(clean_username, users))
    for user in sorted(set(users), key=users.index):
        user_is_new: bool = user not in db.users
        try:
            api = load_api(db) if api is None else api
            for folder in folders:
                print(f"Downloading: {user}/{folder}")
                tot, fail = download_user(api, db, user, folder)
                print("Items downloaded:", tot)
                print("Items failed:", fail) if fail else None
        except UnknownFolder as err:
            print(f"Unknown folder: {err.args[0]}")
            raise
        except DisabledAccount:
            print(f"User {user} disabled")
            db.users.deactivate_user(user)
            db.commit()
        except NoticeMessage:
            print(f"User {user} not found")
            if user_is_new:
                del db.users[user]
                db.commit()
        except ParsingError as err:
            print(f"User {user} error: {repr(err)}")


def download_user(api: FAAPI, db: FADatabase, user: str, folder: str, stop: int = 0) -> tuple[int, int]:
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

    download: Callable[[str, Union[str, int]], tuple[list[Union[SubmissionPartial, Journal]], Union[int, str]]]
    exists: Callable[[int], Optional[dict]]

    if folder.startswith("!"):
        print(f"{user}/{folder} deactivated")
        return 0, 0
    elif folder in ("gallery", "list-gallery"):
        download = api.gallery
        exists = db.submissions.__getitem__
    elif folder in ("scraps", "list-scraps"):
        download = api.scraps
        exists = db.submissions.__getitem__
    elif folder in ("favorites", "list-favorites"):
        page = "next"
        download = api.favorites
        exists = db.submissions.__getitem__
    elif folder in ("journals", "list-journals"):
        download = api.journals
        exists = db.journals.__getitem__
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
        try:
            items, page = download(user, page)
        except (Exception, BaseException):
            raise
        finally:
            print("\r" + (" " * (space_term - 1)), end="\r", flush=True)
        for i, item in enumerate(items, 1):
            sub_string: str = f"{page_n}/{i:02d} {item.id:010d} {clean_string(item.title)}"
            print(f"{sub_string[:space_line]:<{space_line}} ", end="", flush=True)
            bar: Bar = Bar(space_bar)
            if not item.id:
                items_failed += 1
                bar.message("ID ERROR")
                bar.close()
                continue
            bar.message("SEARCH DB")
            if item_ := exists(item.id):
                if folder == "favorites":
                    found_items += not db.submissions.add_favorite(item.id, user)
                elif folder in ("gallery", "scraps"):
                    db.submissions.update({"USERUPDATE": 1}, item.id) if not item_["USERUPDATE"] else None
                    found_items += not db.submissions.set_folder(item.id, folder) and item_["USERUPDATE"]
                elif folder == "journals":
                    db.journals.update({"USERUPDATE": 1}, item.id) if not item_["USERUPDATE"] else None
                    found_items += item_["USERUPDATE"]
                db.commit()
                bar.message("IS IN DB")
                if stop and found_items >= stop:
                    print("\r" + (" " * (space_term - 1)), end="\r", flush=True) if stop < 2 else bar.close()
                    page = 0
                    break
                bar.close()
            elif skip:
                bar.message("SKIPPED")
                bar.close()
            elif isinstance(item, SubmissionPartial):
                bar.delete()
                if download_submission(api, db, item, folder != "favorites"):
                    if folder == "favorites":
                        db.submissions.add_favorite(item.id, user)
                        db.commit()
                    items_total += 1
            elif isinstance(item, Journal):
                save_journal(db, item, folder == "journals")
                bar.update(1, 1)
                bar.close()
                items_total += 1

    return items_total, items_failed
