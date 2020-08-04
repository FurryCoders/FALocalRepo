from json import dumps as json_dumps
from os import makedirs
from os.path import join as path_join

from faapi import FAAPI
from faapi import Sub
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
    sub, sub_file = api.get_sub(sub_id, True)

    if not sub.id:
        return False

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

    return True
