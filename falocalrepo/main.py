from datetime import datetime
from os import getcwd
from os.path import abspath
from os.path import join as path_join
from typing import Dict
from typing import List

from faapi import FAAPI

from .database import Connection
from .database import connect_database
from .database import make_database
from .database import setting_write
from .menu import menu
from .settings import change_cookies


def download_menu(api: FAAPI, db: Connection):
    dl_menu: List[str] = [
        "Exit",
    ]

    while choice := menu(dl_menu):
        if choice == len(dl_menu):
            break


def database_menu(db: Connection):
    db_menu: List[str] = [
        "Exit",
    ]

    while choice := menu(db_menu):
        if choice == len(db_menu):
            break


def settings_menu(api: FAAPI, db: Connection):
    menu_items: List[str] = [
        "Cookies",
        "Exit",
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break
        elif choice == 1:
            cookies_new: Dict[str, str] = change_cookies(db)
            api.load_cookies([{"name": k, "value": v} for k, v in cookies_new.items()])


def main_menu(workdir: str, api: FAAPI, db: Connection):
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


def main():
    # Get current work directory
    workdir: str = abspath(getcwd())

    # Initialise api and database
    api: FAAPI = FAAPI()
    db: Connection = connect_database(path_join(workdir, "FA.db"))

    # Prepare database
    make_database(db)
    setting_write(db, "LASTSTART", str(datetime.now().timestamp()))

    # Run main program
    main_menu(workdir, api, db)
