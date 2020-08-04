from sqlite3 import Connection
from sqlite3 import connect as sqlite3_connect
from typing import List


def connect_database(db_name: str) -> Connection:
    return sqlite3_connect(db_name)


def write(db: Connection, table: str, keys: List[str], values: List[str], replace: bool = True):
    db.execute(
        f"""INSERT OR {"REPLACE" if replace else "IGNORE"} INTO {table}
        ({",".join(keys)})
        VALUES ({",".join(["?"] * len(values))})""",
        values
    )


def read(db: Connection, table: str, select: List[str], key: str, key_value: str) -> List[tuple]:
    return db.execute(
        f'''SELECT ({",".join(select)}) FROM {table} WHERE {key} = ?''',
        (key_value,)
    ).fetchall()
