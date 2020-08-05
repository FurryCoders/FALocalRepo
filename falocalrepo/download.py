from json import dumps as json_dumps
from os import makedirs
from os.path import join as path_join
from typing import Callable
from typing import List
from typing import Tuple
from typing import Union

from faapi import FAAPI
from faapi import Sub
from faapi import SubPartial
from filetype import guess_extension

from .database import Connection
from .database import keys_submissions
from .database import tiered_path
from .database import write
from .settings import setting_read


def load_cookies(api: FAAPI, cookie_a: str, cookie_b: str):
    api.load_cookies([
        {"name": "a", "value": cookie_a},
        {"name": "b", "value": cookie_b},
    ])


def submission_save(db: Connection, sub: Sub, sub_ext: str):
    write(db, "SUBMISSIONS",
          keys_submissions,
          [sub.id, sub.author, sub.title,
           sub.date, sub.description, json_dumps(sub.tags),
           sub.category, sub.species, sub.gender,
           sub.rating, sub.file_url, sub_ext],
          replace=True)

    db.commit()


def submission_download(api: FAAPI, db: Connection, sub_id: int) -> bool:
    sub, _ = api.get_sub(sub_id, False)
    sub_file: bytes = bytes()

    try:
        sub_file = api.get_sub_file(sub)
    except KeyboardInterrupt:
        raise
    except (Exception, BaseException):
        pass

    if not sub.id:
        return False

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

        sub_ext: str = "" if sub_ext_tmp is None else f".{str(sub_ext_tmp)}"
        sub_folder: str = path_join(setting_read(db, "FILESFOLDER"), tiered_path(sub.id))

        submission_save(db, sub, sub_ext.strip("."))

        makedirs(sub_folder, exist_ok=True)

        with open(path_join(sub_folder, "submission" + sub_ext), "wb") as f:
            f.write(sub_file)
    else:
        submission_save(db, sub, sub.file_url.split(".")[-1] if "." in sub.file_url.split("/")[-1] else "")

    return True


def user_download(api: FAAPI, db: Connection, user: str, folder: str) -> Tuple[int, int]:
    subs_total: int = 0
    subs_failed: int = 0
    page: Union[int, str] = 1
    page_n: int = 0

    downloader: Callable[[str, Union[str, int]], Tuple[List[SubPartial], Union[int, str]]] = lambda *x: ([], 0)
    if folder == "gallery":
        downloader = api.gallery
    elif folder == "scraps":
        downloader = api.scraps
    elif folder == "favorites":
        page = "next"
        downloader = api.favorites

    while page:
        page_n += 1
        user_subs, page = downloader(user, page)
        for i, sub in enumerate(user_subs, 1):
            if not sub.id:
                subs_failed += 1
            elif submission_download(api, db, sub.id):
                subs_total += 1

    return subs_total, subs_failed
