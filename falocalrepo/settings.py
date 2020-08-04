from json import dumps as json_dumps
from json import loads as json_loads
from typing import Dict
from typing import Optional
from typing import Tuple

from .database import Connection
from .database import read
from .database import write


def setting_write(db: Connection, key: str, value: str, replace: bool = True):
    write(db, "SETTINGS", ["SETTING", "SVALUE"], [key, value], replace)
    db.commit()


def setting_read(db: Connection, key: str) -> Optional[str]:
    setting = read(db, "SETTINGS", ["SVALUE"], "SETTING", key)

    return None if not setting else setting[0][0]


def cookies_read(db: Connection) -> Tuple[str, str]:
    cookies: Dict[str, str] = json_loads(setting_read(db, "COOKIES"))
    return cookies.get("a", ""), cookies.get("b", "")


def cookies_write(db: Connection, a: str, b: str):
    setting_write(db, "COOKIES", json_dumps({"a": a, "b": b}))
