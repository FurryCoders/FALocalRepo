from typing import Dict
from typing import List

from faapi import FAAPI

from .database import Connection
from .database import connect_database
from .menu import menu


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
