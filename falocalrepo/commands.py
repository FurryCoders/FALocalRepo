from os import get_terminal_size
from os.path import isdir
from re import findall
from re import sub as re_sub
from shutil import move
from typing import Optional
from typing import Union

from faapi import Journal
from faapi import Submission
from falocalrepo_database import FADatabaseTable
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


def move_files_folder(folder_old: str, folder_new: str):
    if isdir(folder_old):
        print("Moving files to new location... ", end="", flush=True)
        move(folder_old, folder_new)
        print("Done")


def make_journal(id_: Union[int, str], author: str,
                 title: str, date: str, content: str = ""
                 ) -> Journal:
    id_ = int(id_)
    assert id_ > 0, "id must be greater than 0"
    assert isinstance(author, str) and author, "author must be of type str and not empty"
    assert isinstance(title, str) and title, "title must be of type str and not empty"
    assert isinstance(date, str) and date, "date must be of type str and not empty"
    assert isinstance(content, str), "content must be of type str"

    journal = Journal()

    journal.id = id_
    journal.author = author
    journal.title = title
    journal.date = date
    journal.content = content
    journal.mentions = sorted(set(filter(bool, map(clean_username, findall(
        r'<a[^>]*href="(?:(?:https?://)?(?:www.)?furaffinity.net)?/user/([^/">]+)"',
        content)))))

    return journal


def make_submission(id_: Union[int, str], author: str, title: str,
                    date: str, category: str, species: str,
                    gender: str, rating: str, type_: str,
                    tags: str = "", description: str = "",
                    file_url: str = "", file_local_url: str = "",
                    folder: str = ""
                    ) -> tuple[Submission, Optional[bytes]]:
    id_ = int(id_)
    assert id_ > 0, "id must be greater than 0"
    assert isinstance(author, str) and author, "author must be of type str and not empty"
    assert isinstance(title, str) and title, "title must be of type str and not empty"
    assert isinstance(date, str) and date, "date must be of type str and not empty"
    assert isinstance(category, str) and category, "category must be of type str and not empty"
    assert isinstance(species, str) and species, "species must be of type str and not empty"
    assert isinstance(gender, str) and gender, "gender must be of type str and not empty"
    assert isinstance(rating, str) and rating, "rating must be of type str and not empty"
    assert isinstance(type_, str) and type_, "type must be of type str and not empty"
    assert type_ in ("image", "text", "music", "flash")
    assert isinstance(tags, str), "tags must be of type str"
    assert isinstance(description, str), "description must be of type str"
    assert isinstance(file_url, str), "file_url must be of type str"
    assert isinstance(file_local_url, str), "file_local_url must be of type str"
    assert isinstance(folder, str), "folder must be of type str"

    sub: Submission = Submission()
    sub_file: Optional[bytes] = None

    sub.id = id_
    sub.title = title
    sub.author = author
    sub.date = date
    sub.tags = sorted(filter(bool, map(str.strip, tags.split(","))))
    sub.category = category
    sub.species = species
    sub.gender = gender
    sub.rating = rating
    sub.type = type_
    sub.description = description
    sub.file_url = file_url
    sub.folder = folder
    sub.mentions = sorted(set(filter(bool, map(clean_username, findall(
        r'<a[^>]*href="(?:(?:https?://)?(?:www.)?furaffinity.net)?/user/([^/">]+)"',
        description)))))

    if file_local_url:
        with open(file_local_url, "rb") as f:
            sub_file = f.read()

    return sub, sub_file


def search(table: FADatabaseTable, parameters: dict[str, list[str]], columns: list[str] = None
           ) -> list[dict[str, Union[int, str]]]:
    parameters = {k.upper(): vs for k, vs in parameters.items()}
    query: dict[str, list[str]] = {k: vs for k, vs in parameters.items() if k in table.columns}
    if "AUTHOR" in query:
        query["REPLACE(AUTHOR, '_', '')"] = list(map(lambda u: clean_username(u, "%_"), query["AUTHOR"]))
        del query["AUTHOR"]
    if "USERNAME" in query:
        query["USERNAME"] = list(map(lambda u: clean_username(u, "%_"), query["USERNAME"]))
    if "ID" in query:
        query["ID"] = list(map(lambda i: i.lstrip("0") if isinstance(i, str) else i, query["ID"]))
    return list(table.cursor_to_dict(
        table.select(
            query,
            columns=columns,
            like=True,
            order=parameters.get("order", [table.column_id]),
            limit=int(parameters.get("limit", 0)),
            offset=int(parameters.get("offset", 0))
        ),
        columns=columns))


def print_items(items: list[dict[str, Union[int, str]]]):
    space_term: int

    try:
        space_term = get_terminal_size()[0]
    except IOError:
        space_term = 10000

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


def print_users(users: list[dict[str, str]]):
    space_term: int = 10000
    try:
        space_term = get_terminal_size()[0]
    except IOError:
        pass

    space_name: int = max([len(u["USERNAME"]) for u in users]) if users else 10
    space_folders: int = max([len(u["FOLDERS"]) * 2 for u in users]) if users else 7
    space_name = 8 if space_name < 8 else space_name
    space_folders = 7 if space_folders < 7 else space_folders
    space_name = space_name if (sn := space_term - space_folders - 3) > space_name else sn

    print(f"{'Username':^{space_name}} | {'Folders':^{space_folders}}")
    for user in sorted(users, key=lambda usr: usr["USERNAME"].lower()):
        folders_min: str = " ".join(sorted((f[:2] if f.startswith("!") else f[0]) for f in user["FOLDERS"]))
        print(f"{user['USERNAME'][:space_name]:<{space_name}} | {folders_min:^{space_folders}}")
