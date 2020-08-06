from shutil import move
from typing import List
from typing import Tuple

from faapi import FAAPI

from .database import Connection
from .database import select_all
from .download import load_cookies
from .download import submission_download
from .download import user_download
from .menu import menu
from .settings import cookies_read
from .settings import cookies_write
from .settings import setting_read
from .settings import setting_write


def download_menu(api: FAAPI, db: Connection):
    dl_menu: List[str] = [
        "Users",
        "Submissions",
        "Update",
        "Exit",
    ]

    while choice := menu(dl_menu):
        if choice == len(dl_menu):
            break
        if choice == 1:
            print("Insert space-separated usernames.")
            users: List[str] = input("Users: ").split(" ")
            print("Insert space-separated folders (gallery, scraps or favorites).")
            folders: List[str] = input("Folders: ").lower().split(" ")
            for user, folder in ((u, f) for u in users for f in folders):
                print(f"Downloading: {user}/{folder}")
                tot, fail = user_download(api, db, user, folder)
                print("Submissions downloaded:", tot)
                print("Submissions failed:", fail)
        elif choice == 2:
            print("Insert space-separated submission ID's.\nLeave empty to cancel.")
            sub_ids: List[str] = input("ID: ").split()
            sub_ids = list(filter(len, sub_ids))
            if sub_ids_fail := list(filter(lambda i: not i.isdigit(), sub_ids)):
                print("The following ID's are not correct:", *sub_ids_fail)
            for sub_id in map(int, filter(lambda i: i.isdigit(), sub_ids)):
                print(f"Downloading {sub_id:010} ", end="", flush=True)
                submission_download(api, db, sub_id)
        elif choice == 3:
            users_folders: List[Tuple[str, str]] = select_all(db, "USERS", ["USERNAME", "FOLDERS"])
            for user, user_folders in users_folders:
                for folder in user_folders.split(","):
                    print(f"Downloading: {user}/{folder}")
                    tot, fail = user_download(api, db, user, folder)
                    print("Submissions downloaded:", tot)
                    print("Submissions failed:", fail)


def database_menu(db: Connection):
    db_menu: List[str] = [
        "Search",
        "Manual Entry"
        "Check for Errors",
        "Exit",
    ]

    while choice := menu(db_menu):
        if choice == len(db_menu):
            break
        else:
            raise NotImplemented(db_menu[choice])


def settings_menu(api: FAAPI, db: Connection):
    menu_items: List[str] = [
        "Cookies",
        "Files Folder",
        "Exit",
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break
        elif choice == 1:
            print("Insert new values for cookies 'a' and 'b'.")
            print("Leave empty to keep previous value.\n")

            cookie_a_old, cookie_b_old = cookies_read(db)

            cookie_a: str = input(f"[{cookie_a_old}]\na: ")
            cookie_b: str = input(f"[{cookie_b_old}]\nb: ")

            if cookie_a or cookie_b:
                cookies_write(db, cookie_a, cookie_b)
                load_cookies(api, cookie_a, cookie_b)
        elif choice == 2:
            print("Insert new files folder.")
            print("Leave empty to keep previous value.\n")

            folder_old: str = setting_read(db, "FILESFOLDER")
            folder: str = input(f"[{folder_old}]\n:folder: ")

            if folder:
                setting_write(db, "FILESFOLDER", folder)
                print("Moving files to new location... ", end="", flush=True)
                move(folder_old, folder)
                print("Done")


def main_menu(db: Connection):
    api: FAAPI = FAAPI()
    load_cookies(api, *cookies_read(db))

    menu_items: List[str] = [
        "Download",
        "Database",
        "Settings",
        "Exit"
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break
        elif choice == 1:
            download_menu(api, db)
        elif choice == 2:
            database_menu(db)
        elif choice == 3:
            settings_menu(api, db)
