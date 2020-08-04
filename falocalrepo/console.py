from typing import List

from faapi import FAAPI

from .database import Connection


def main_console(workdir: str, api: FAAPI, db: Connection, args: List[str]):
    if not args:
        return
