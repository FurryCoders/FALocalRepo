from json import dumps as json_dumps
from os.path import join as path_join

from faapi import FAAPI
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

    sub_folder: str = tiered_path(sub.id)
    sub_ext: str = "" if sub_ext_tmp is None else f".{str(sub_ext_tmp)}"
    sub_file_path: str = path_join(setting_read(db, "FILESFOLDER"), sub_folder, "submission" + sub_ext)

    write(db, "SUBMISSIONS",
          keys_submissions,
          [sub.id, sub.author, sub.title,
           sub.date, sub.description, json_dumps(sub.tags),
           sub.category, sub.species, sub.gender,
           sub.rating, sub.file_url, "submission" + sub_ext,
           sub_folder],
          replace=True)

    db.commit()

    with open(sub_file_path, "wb") as f:
        f.write(sub_file)

    return True
