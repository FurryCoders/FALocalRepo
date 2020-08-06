from typing import List

from faapi import FAAPI

from .commands import download_submissions
from .commands import download_users
from .commands import files_folder_move
from .commands import update_users
from .database import Connection
from .download import load_cookies
from .menu import menu
from .settings import cookies_read
from .settings import cookies_write
from .settings import setting_read


def download_menu(api: FAAPI, db: Connection):
    load_cookies(api, *cookies_read(db))

    menu_items: List[str] = [
        "Users",
        "Submissions",
        "Update",
        "Exit",
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break
        if choice == 1:
            print("Insert space-separated usernames.")
            users: List[str] = input("Users: ").split(" ")
            print("Insert space-separated folders (gallery, scraps or favorites).")
            folders: List[str] = input("Folders: ").lower().split(" ")
            download_users(api, db, users, folders)
        elif choice == 2:
            print("Insert space-separated submission ID's.\nLeave empty to cancel.")
            sub_ids: List[str] = input("ID: ").split()
            sub_ids = list(filter(len, sub_ids))
            download_submissions(api, db, sub_ids)
        elif choice == 3:
            update_users(api, db)


def database_menu(db: Connection):
    menu_items: List[str] = [
        "Search",
        "Manual Entry"
        "Check for Errors",
        "Exit",
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break
        else:
            raise NotImplemented(menu_items[choice])


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
        elif choice == 2:
            print("Insert new files folder.")
            print("Leave empty to keep previous value.\n")

            folder_old: str = setting_read(db, "FILESFOLDER")
            folder_new: str = input(f"[{folder_old}]\n:folder: ")

            if folder_new:
                files_folder_move(db, folder_old, folder_new)


def main_menu(db: Connection):
    api: FAAPI = FAAPI()

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
