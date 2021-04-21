from os import get_terminal_size
from re import findall
from re import sub as re_sub

from falocalrepo_database import FADatabase
from falocalrepo_database import FADatabaseTable
from falocalrepo_database.database import Entry
from falocalrepo_database.database import guess_extension
from requests import get as req_get


class Bar:
    def __init__(self, length: int = 0, *, message: str = ""):
        self.length: int = length
        self.level: int = 0
        self.message_: str = ""

        print(f"[{' ' * self.length}]", end="\b" * (self.length + 1), flush=True)

        self.message(message) if message else None

    def clear(self):
        print("\b \b" * self.level, end="", flush=True)
        self.level = 0
        self.message_ = ""

    def delete(self):
        self.clear()
        print("\b" + (" " * (self.length + 2)), end="\b" * (self.length + 2), flush=True)

    @staticmethod
    def close(end: str = "\n"):
        print(end=end, flush=True)

    def update(self, total: int, current: int):
        self.clear() if self.message_ else None

        if (new_level := int((current / total) * self.length)) == self.level:
            return

        print(("\b \b" * -(diff_level := new_level - self.level)) + ("#" * diff_level), end="", flush=True)

        self.level = new_level

    def message(self, message: str):
        self.clear()
        self.level = len(message := f"{(message[:self.length]):^{self.length}}")
        print(message, end="", flush=True)
        self.message_: str = message


def clean_username(username: str, exclude: str = "") -> str:
    return str(re_sub(rf"[^a-zA-Z0-9\-.~{exclude}]", "", username.lower().strip()))


def clean_string(title: str) -> str:
    return str(re_sub(r"[^\x20-\x7E]", "", title.strip()))


def latest_version(package: str) -> str:
    try:
        res = req_get(f"https://pypi.org/pypi/{package}/json")
        return "" if not res.ok else res.json()["info"]["version"]
    except (Exception, BaseException):
        return ""


def make_journal(db: FADatabase, data: Entry):
    data = {k.lower(): v for k, v in data.items()}
    data = {**{k.lower(): v for k, v in (db.submissions[int(data["id"])] or {}).items()}, **data}
    assert isinstance(data.get("mentions", []), list), "mentions field needs to be of type list"

    data["id"] = int(data["id"])
    data["mentions"] = sorted(set(filter(bool, map(
        clean_username,
        data.get("mentions", findall(
            r'<a[^>]*href="(?:(?:https?://)?(?:www.)?furaffinity.net)?/user/([^/">]+)/?"',
            str(data["content"])))))))

    db.journals.save_journal(data)


def make_submission(db: FADatabase, data: Entry, file: str = None, thumb: str = None):
    data = {k.lower(): v for k, v in data.items()}
    data = {**{k.lower(): v for k, v in (db.submissions[int(data["id"])] or {}).items()}, **data}
    assert isinstance(data.get("tags", []), list), "tags field needs to be of type list"
    assert isinstance(data.get("mentions", []), list), "mentions field needs to be of type list"
    assert isinstance(data.get("favorite", []), list), "mentions field needs to be of type list"

    data["id"] = int(data["id"])
    data["tags"] = list(filter(bool, map(str.strip, data.get("tags", []))))
    data["favorite"] = list(filter(bool, map(clean_username, data.get("favorite", []))))
    data["mentions"] = sorted(set(filter(bool, map(
        clean_username,
        data.get("mentions", findall(
            r'<a[^>]*href="(?:(?:https?://)?(?:www.)?furaffinity.net)?/user/([^/">]+)/?"',
            str(data["description"])))))))
    data["userupdate"] = int(data.get("userupdate", 0))

    sub_file, sub_thumb = db.submissions.get_submission_files(data["id"])
    sub_file = open(file, "rb").read() if file else sub_file
    sub_thumb = open(thumb, "rb").read() if thumb else sub_thumb
    assert sub_thumb is None or guess_extension(sub_thumb) == "jpg", "Thumbnail must be in JPEG format"

    db.submissions.save_submission(data, sub_file, sub_thumb)


def make_user(db: FADatabase, data: Entry):
    data = {k.lower(): v for k, v in data.items()}
    assert isinstance(data.get("folders", []), list), "folders field needs to be of type list"

    username: str = db.users.new_user(data["username"])
    if data.get("folders", None):
        for f in (old := set(db.users[username]["FOLDERS"])) - (new := set(map(str.lower, data["folders"]))):
            db.users.remove_user_folder(username, f)
        for f in new - old:
            db.users.add_user_folder(username, f)
    db.commit()


def search(table: FADatabaseTable, parameters: dict[str, list[str]], columns: list[str] = None) -> list[Entry]:
    parameters = {k.upper(): vs for k, vs in parameters.items()}
    query: dict[str, list[str]] = {k: vs for k, vs in parameters.items() if k in table.columns}
    if "AUTHOR" in query:
        query["REPLACE(AUTHOR, '_', '')"] = list(map(lambda u: clean_username(u, "%_"), query["AUTHOR"]))
        del query["AUTHOR"]
    if "USERNAME" in query:
        query["USERNAME"] = list(map(lambda u: clean_username(u, "%_"), query["USERNAME"]))
    if "ID" in query:
        query["ID"] = list(map(lambda i: i.lstrip("0") if isinstance(i, str) else i, query["ID"]))
    return list(table.select(
        query,
        columns=columns,
        like=True,
        order=parameters.get("order", [table.column_id]),
        limit=int(parameters.get("limit", 0)),
        offset=int(parameters.get("offset", 0))
    ))


def print_items(items: list[Entry]):
    try:
        space_term: int = get_terminal_size()[0]
    except IOError:
        space_term: int = 10000

    space_id: int = 10
    space_user: int = max([len(item["AUTHOR"]) for item in items] + [10])
    space_date: int = 10

    print(f"{'ID':^{space_id}} | {'User':^{space_user}} | {'Date':^{space_date}} | Title")
    for item in items:
        print(
            f"{str(item['ID']).zfill(space_id)} | " +
            f"{item['AUTHOR']:<{space_user}} | " +
            f"{item['DATE']} | " +
            item['TITLE'][:(space_term - space_id - space_user - space_date - 10)]
        )


def print_users(users: list[Entry]):
    try:
        space_term: int = get_terminal_size()[0]
    except IOError:
        space_term: int = 10000

    space_name: int = max([len(u["USERNAME"]) for u in users]) if users else 10
    space_folders: int = max([len(u["FOLDERS"]) * 2 for u in users]) if users else 7
    space_name = 8 if space_name < 8 else space_name
    space_folders = 7 if space_folders < 7 else space_folders
    space_name = space_name if (sn := space_term - space_folders - 3) > space_name else sn

    print(f"{'Username':^{space_name}} | {'Folders':^{space_folders}}")
    for user in sorted(users, key=lambda usr: usr["USERNAME"].lower()):
        folders_min: str = " ".join(sorted((f[:2] if f.startswith("!") else f[0]) for f in user["FOLDERS"]))
        print(f"{user['USERNAME'][:space_name]:<{space_name}} | {folders_min:^{space_folders}}")
