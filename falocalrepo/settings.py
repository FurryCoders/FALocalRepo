from json import dumps as json_dumps
from json import loads as json_loads
from typing import Dict
from typing import Tuple

from .database import Connection
from .database import setting_read
from .database import setting_write


def cookies_load(db: Connection) -> Tuple[str, str]:
    cookies: Dict[str, str] = json_loads(setting_read(db, "COOKIES"))
    return cookies.get("a", ""), cookies.get("b", "")


def cookies_change(db: Connection, a: str, b: str):
    setting_write(db, "COOKIES", json_dumps({"a": a, "b": b}))
