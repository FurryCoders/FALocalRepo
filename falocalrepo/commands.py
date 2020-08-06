from os.path import isdir
from shutil import move
from typing import List
from typing import Tuple

from faapi import FAAPI

from .database import Connection
from .database import select_all
from .download import submission_download
from .download import user_download
from .settings import setting_write


def files_folder_move(db: Connection, folder_old: str, folder_new: str):
    setting_write(db, "FILESFOLDER", folder_new)
    if isdir(folder_old):
        print("Moving files to new location... ", end="", flush=True)
        move(folder_old, folder_new)
        print("Done")


def download_users(api: FAAPI, db: Connection, users: List[str], folders: List[str]):
    for user, folder in ((u, f) for u in users for f in folders):
        print(f"Downloading: {user}/{folder}")
        tot, fail = user_download(api, db, user, folder)
        print("Submissions downloaded:", tot)
        print("Submissions failed:", fail)


def download_submissions(api: FAAPI, db: Connection, sub_ids: List[str]):
    if sub_ids_fail := list(filter(lambda i: not i.isdigit(), sub_ids)):
        print("The following ID's are not correct:", *sub_ids_fail)
    for sub_id in map(int, filter(lambda i: i.isdigit(), sub_ids)):
        print(f"Downloading {sub_id:010} ", end="", flush=True)
        submission_download(api, db, sub_id)


def update_users(api: FAAPI, db: Connection):
    users_folders: List[Tuple[str, str]] = select_all(db, "USERS", ["USERNAME", "FOLDERS"])
    for user, user_folders in users_folders:
        for folder in user_folders.split(","):
            print(f"Downloading: {user}/{folder}")
            tot, fail = user_download(api, db, user, folder)
            print("Submissions downloaded:", tot)
            print("Submissions failed:", fail)
