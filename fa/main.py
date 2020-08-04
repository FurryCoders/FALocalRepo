from typing import Dict
from typing import List

from faapi import FAAPI

from .database import Connection
from .database import connect_database
from .menu import menu


def download(api: FAAPI, db: Connection):
    dl_menu: List[str] = [
        "Exit",
    ]

    while choice := menu(dl_menu):
        if choice == len(dl_menu):
            break


def database(db: Connection):
    db_menu: List[str] = [
        "Exit",
    ]

    while choice := menu(db_menu):
        if choice == len(db_menu):
            break


def settings(db: Connection):
    s_menu: List[str] = [
        "Exit",
    ]

    while choice := menu(s_menu):
        if choice == len(s_menu):
            break


def main(workdir: str, cookies: List[Dict[str, str]]):
    # Initialise api and database
    api: FAAPI = FAAPI(cookies)
    db: Connection = connect_database("FA.db")

    main_menu: List[str] = [
        "Download",
        "Database",
        "Settings",
        "Exit"
    ]

    while choice := menu(main_menu):
        if choice == len(main_menu):
            break
        elif choice == 1:
            download(api, db)
        elif choice == 2:
            database(db)
        elif choice == 3:
            settings(db)
