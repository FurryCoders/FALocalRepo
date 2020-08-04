from json import dumps as json_dumps
from json import loads as json_loads
from typing import Dict

from .database import Connection
from .database import setting_read
from .database import setting_write


def change_cookies(db: Connection) -> Dict[str, str]:
    print("Insert new values for cookies 'a' and 'b'.")
    print("Leave empty to keep previous value.\n")

    cookies: Dict[str, str] = json_loads(setting_read(db, "COOKIES"))

    cookie_a_old: str = cookies.get('a', '')
    cookie_b_old: str = cookies.get('b', '')

    cookie_a_new: str = input(f"[{cookie_a_old}]\na: ")
    cookie_b_new: str = input(f"[{cookie_b_old}]\nb: ")

    cookies["a"] = cookie_a_new if cookie_a_new else cookie_a_old
    cookies["b"] = cookie_b_new if cookie_b_new else cookie_b_old

    if cookie_a_new or cookie_b_new:
        setting_write(db, "COOKIES", json_dumps(cookies))

    return cookies
