from typing import List

from faapi import FAAPI

from .commands import download_submissions
from .commands import download_users
from .commands import files_folder_move
from .commands import make_submission
from .commands import print_submissions
from .commands import search_submissions
from .commands import update_users
from .database import Connection
from .database import check_errors
from .download import load_cookies
from .download import submission_save
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
        "Manual Entry",
        "Check for Errors",
        "Exit",
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break
        elif choice == 1:
            print("Insert search parameters.\nLeave empty to skip.")
            author: str = input("Author     : ")
            title: str = input("Title      : ")
            date: str = input("Date       : ")
            tags: str = input("Tags       : ")
            description: str = input("Description: ")
            rating: str = input("Rating     : ")
            category: str = input("Category   : ")
            species: str = input("Species    : ")
            gender: str = input("Gender     : ")
            results: List[tuple] = search_submissions(
                db,
                authors=[author] if author else [],
                titles=[title] if title else [],
                dates=[date] if date else [],
                tags=tags.split(",") if tags else [],
                descriptions=[description] if description else [],
                ratings=[rating] if rating else [],
                categories=[category] if category else [],
                species=[species] if species else [],
                genders=[gender] if gender else []
            )
            print_submissions(results, sort=True)
        elif choice == 2:
            print("Insert submission details.\nTags need to be space-separated\n" +
                  "Description and Local file can be left empty.")
            id_: int = int(input("ID         : "))
            author: str = input("Author     : ")
            title: str = input("Title      : ")
            date: str = input("Date       : ")
            tags: List[str] = input("Tags       : ").split(" ")
            description: str = input("Description: ")
            rating: str = input("Rating     : ")
            category: str = input("Category   : ")
            species: str = input("Species    : ")
            gender: str = input("Gender     : ")
            file_url: str = input("Remote file: ")
            file_local_url: str = input("Local file : ")
            submission_save(db, *make_submission(
                id_=id_,
                author=author,
                title=title,
                date=date,
                tags=tags,
                description=description,
                rating=rating,
                category=category,
                species=species,
                gender=gender,
                file_url=file_url,
                file_local_url=file_local_url
            ))
        elif choice == 3:
            print("Checking submissions table for errors... ", end="", flush=True)
            results: List[tuple] = check_errors(db, "SUBMISSIONS")
            print("Done")
            if results:
                print_submissions(results)


def settings_menu(db: Connection):
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
            settings_menu(db)
