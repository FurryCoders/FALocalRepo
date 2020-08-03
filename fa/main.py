from typing import Dict
from typing import List

from faapi import FAAPI

from .menu import menu


def main(workdir: str, cookies: List[Dict[str, str]]):
    # Initialise api
    api: FAAPI = FAAPI(cookies)

    main_menu: List[str] = [
        "Download",
        "Database",
        "Settings",
        "Exit"
    ]

    while choice := menu(main_menu):
        if choice >= len(main_menu) - 1:
            break
