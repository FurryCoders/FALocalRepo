from os import getcwd
from os.path import abspath
from os.path import join as path_join
from typing import List

from faapi import FAAPI

from .database import Connection
from .database import connect_database
from .menu import menu


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


def settings_menu(db: Connection):
    menu_items: List[str] = [
        "Exit",
    ]

    while choice := menu(menu_items):
        if choice == len(menu_items):
            break


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


def main(workdir: str = abspath(getcwd())):
    # Initialise api and database
    api: FAAPI = FAAPI()
    db: Connection = connect_database(path_join(workdir, "FA.db"))

    main_menu(workdir, api, db)
