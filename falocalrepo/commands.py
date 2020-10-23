from math import ceil
from math import log10
from os import get_terminal_size
from os.path import isdir
from shutil import move
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from faapi import Journal
from faapi import Submission
from falocalrepo_database import FADatabaseTable
from requests import get as req_get


class Bar:
    def __init__(self, length: int = 0):
        self.length: int = length
        self.level: int = 0

        print(f"[{' ' * self.length}]", end="\b" * (self.length + 1), flush=True)

    def clear(self):
        print("\b \b" * self.level, end="", flush=True)
        self.level = 0

    def delete(self):
        self.clear()
        print("\b" + (" " * (self.length + 2)), end="\b" * (self.length + 2), flush=True)

    @staticmethod
    def close():
        print()

    def update(self, total: int, current: int):
        if (new_level := int((current / total) * self.length)) == self.level:
            return
        elif (diff_level := new_level - self.level) < 0:
            print("\b \b" * diff_level, end="", flush=True)
        else:
            print("#" * diff_level, end="", flush=True)
        self.level = new_level

    def message(self, message: str):
        self.clear()
        print(f"{message[:self.length]:^{self.length}}", end="", flush=True)


def latest_version(package: str) -> str:
    try:
        res = req_get(f"https://pypi.org/pypi/{package}/json")
        if not res.ok:
            return ""
        else:
            return res.json()["info"]["version"]
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

    journal.id = int(id_)
    journal.author = author
    journal.title = title
    journal.date = date
    journal.content = content

    return journal


def make_submission(id_: Union[int, str], author: str, title: str,
                    date: str, category: str, species: str,
                    gender: str, rating: str, tags: str = "",
                    description: str = "", file_url: str = "",
                    file_local_url: str = ""
                    ) -> Tuple[Submission, Optional[bytes]]:
    id_ = int(id_)
    assert id_ > 0, "id must be greater than 0"
    assert isinstance(author, str) and author, "author must be of type str and not empty"
    assert isinstance(title, str) and title, "title must be of type str and not empty"
    assert isinstance(date, str) and date, "date must be of type str and not empty"
    assert isinstance(category, str) and category, "category must be of type str and not empty"
    assert isinstance(species, str) and species, "species must be of type str and not empty"
    assert isinstance(gender, str) and gender, "gender must be of type str and not empty"
    assert isinstance(rating, str) and rating, "rating must be of type str and not empty"
    assert isinstance(tags, str), "tags must be of type str"
    assert isinstance(description, str), "description must be of type str"
    assert isinstance(file_url, str), "file_url must be of type str"
    assert isinstance(file_local_url, str), "file_local_url must be of type str"

    sub: Submission = Submission()
    sub_file: Optional[bytes] = None

    sub.id = int(id_)
    sub.title = title
    sub.author = author
    sub.date = date
    sub.tags = list(filter(bool, map(str.strip, tags.split(","))))
    sub.category = category
    sub.species = species
    sub.gender = gender
    sub.rating = rating
    sub.description = description
    sub.file_url = file_url

    if file_local_url:
        with open(file_local_url, "rb") as f:
            sub_file = f.read()

    return sub, sub_file


def search(table: FADatabaseTable, parameters: Dict[str, List[str]]):
    parameters = {k.lower(): vs for k, vs in parameters.items()}
    query: Dict[str, List[str]] = {k: vs for k, vs in parameters.items() if k not in map(str.lower, table.columns)}
    results: List[Dict[str, Union[int, str]]] = list(table.cursor_to_dict(table.select(
        query,
        order=parameters.get("order", None),
        limit=parameters.get("limit", None),
        offset=parameters.get("offset", None)
    )))
    if table.table.lower() == "users":
        print_users(results)
    else:
        print_items(results)
    print(f"Found {len(results)} results")


def print_items(subs: List[Dict[str, Union[int, str]]]):
    space_id: int = 10
    space_user: int = 10
    space_date: int = 10
    space_term: int = 10000
    try:
        space_term = get_terminal_size()[0]
    except IOError:
        pass

    print(f"{'ID':^{space_id}} | {'User':^{space_user}} | {'Date':^{space_date}} | Title")
    for sub in subs:
        print(
            f"{str(sub['ID'])[:space_id].zfill(space_id)} | " +
            f"{sub['AUTHOR'][:space_user]:<{space_user}} | " +
            f"{sub['DATE'][:space_date]:<{space_date}} | " +
            sub['TITLE'][:(space_term - space_id - space_user - space_date - 10)]
        )


def print_users(users: List[Dict[str, str]]):
    space_folders: int = 7
    space_folder: int = 9
    space_term: int = 10000
    try:
        space_term = get_terminal_size()[0]
    except IOError:
        pass
    space_name: int = space_term - (space_folders + 3) - ((space_folder + 3) * 4) - 1

    users_fmt: List[tuple] = [
        (
            user["USERNAME"],
            f.split(",") if (f := user["FOLDERS"]) else 0,
            len(f.split(",")) if (f := user["GALLERY"]) else 0,
            len(f.split(",")) if (f := user["SCRAPS"]) else 0,
            len(f.split(",")) if (f := user["FAVORITES"]) else 0,
            len(f.split(",")) if (f := user["MENTIONS"]) else 0
        )
        for user in users
    ]

    users_fmt.sort(key=lambda usr: usr[0])

    space_name_max: int = max([len(user[0]) for user in users_fmt])
    space_name = space_name_max if space_name > space_name_max else space_name
    len_gallery_max: int = int(max([ceil(log10(user[2])) if user[2] else 0 for user in users_fmt]))
    len_scraps_max: int = int(max([ceil(log10(user[3])) if user[3] else 0 for user in users_fmt]))
    len_favorites_max: int = int(max([ceil(log10(user[4])) if user[4] else 0 for user in users_fmt]))
    len_mentions_max: int = int(max([ceil(log10(user[5])) if user[5] else 0 for user in users_fmt]))

    print(
        f"{'Username':^{space_name}} | {'Folders':^{space_folders}}" +
        f" | {'Gallery':^{space_folder}} | {'Scraps':^{space_folder}}" +
        f" | {'Favorites':^{space_folder}} | {'Mentions':^{space_folder}}"
    )
    for user, folders, gallery, scraps, favorites, mentions in users_fmt:
        folders_min: str = ",".join(set(map(lambda f: f[0], folders)))
        print(
            f"{user[:space_name]:<{space_name}} | {folders_min:^{space_folders}}" +
            f" | {f'{gallery:>{len_gallery_max}}':^{space_folder}}" +
            f" | {f'{scraps:>{len_scraps_max}}':^{space_folder}}" +
            f" | {f'{favorites:>{len_favorites_max}}':^{space_folder}}" +
            f" | {f'{mentions:>{len_mentions_max}}':^{space_folder}}"
        )
