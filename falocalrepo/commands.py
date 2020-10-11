from os import get_terminal_size
from os.path import isdir
from shutil import move
from sqlite3 import Connection
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from faapi import Journal
from faapi import Submission
from falocalrepo_database import write_setting
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
        if (diff_level := new_level - self.level) < 0:
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


def move_files_folder(db: Connection, folder_old: str, folder_new: str):
    write_setting(db, "FILESFOLDER", folder_new)
    if isdir(folder_old):
        print("Moving files to new location... ", end="", flush=True)
        move(folder_old, folder_new)
        print("Done")


def make_journal(id_: Union[int, str], author: str,
                 title: str, date: str, content: str = ""
                 ) -> Journal:
    assert isinstance(id_, int) or (isinstance(id_, str) and id_.isdigit())
    assert int(id_) > 0
    assert isinstance(author, str) and author
    assert isinstance(title, str) and title
    assert isinstance(date, str) and date
    assert isinstance(content, str)

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
    assert isinstance(id_, int) or (isinstance(id_, str) and id_.isdigit())
    assert int(id_) > 0
    assert isinstance(author, str) and author
    assert isinstance(title, str) and title
    assert isinstance(date, str) and date
    assert isinstance(category, str) and category
    assert isinstance(species, str) and species
    assert isinstance(gender, str) and gender
    assert isinstance(rating, str) and rating
    assert isinstance(tags, str)
    assert isinstance(description, str)
    assert isinstance(file_url, str)
    assert isinstance(file_local_url, str)

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


def print_items(subs: List[tuple], indexes: Dict[str, int]):
    space_id: int = 10
    space_user: int = 10
    space_date: int = 10
    space_term: int = 10000
    try:
        space_term = get_terminal_size()[0]
    except IOError:
        pass

    index_id: int = indexes["ID"]
    index_user: int = indexes["AUTHOR"]
    index_date: int = indexes["UDATE"]
    index_title: int = indexes["TITLE"]

    print(f"{'ID':^{space_id}} | {'User':^{space_user}} | {'Date':^{space_date}} | Title")
    for sub in subs:
        print(
            f"{str(sub[index_id])[:space_id].zfill(space_id)} | " +
            f"{sub[index_user][:space_user]:<{space_user}} | " +
            f"{sub[index_date][:space_date]:<{space_date}} | " +
            sub[index_title][:(space_term - space_id - space_user - space_date - 10)]
        )


def print_users(users: List[tuple], indexes: Dict[str, int]):
    space_name: int = 15
    space_folders: int = 10
    space_folder: int = 10

    index_name: int = indexes["USERNAME"]
    index_folders: int = indexes["FOLDERS"]
    index_gallery: int = indexes["GALLERY"]
    index_scraps: int = indexes["SCRAPS"]
    index_favorites: int = indexes["FAVORITES"]
    index_mentions: int = indexes["MENTIONS"]

    users.sort(key=lambda usr: usr[index_name])

    print(
        f"{'Username':^{space_name}} | {'Folders':^{space_folders}}" +
        f" | {'Gallery':^{space_folder}} | {'Scraps':^{space_folder}}" +
        f" | {'Favorites':^{space_folder}} | {'Mentions':^{space_folder}}"
    )
    for user in users:
        folders: str = ",".join(set(map(lambda f: f[0], user[index_folders].split(","))))
        gallery: int = len(user[index_gallery].split(",")) if user[index_gallery] else 0
        scraps: int = len(user[index_scraps].split(",")) if user[index_scraps] else 0
        favorites: int = len(user[index_favorites].split(",")) if user[index_favorites] else 0
        mentions: int = len(user[index_mentions].split(",")) if user[index_mentions] else 0
        print(
            f"{user[index_name][:space_name]:<{space_name}} | {folders:^{space_folder}}" +
            f" | {str(gallery):^{space_folder}} | {str(scraps):^{space_folder}}" +
            f" | {str(favorites):^{space_folder}} | {str(mentions):^{space_folder}}"
        )
