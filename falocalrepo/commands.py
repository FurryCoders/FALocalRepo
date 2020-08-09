from datetime import datetime
from os import get_terminal_size
from os.path import isdir
from shutil import move
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from faapi import FAAPI
from faapi import Sub

from .database import Connection
from .database import keys_submissions
from .database import select_all
from .download import submission_download
from .download import user_download
from .settings import setting_write


def files_folder_move(db: Connection, folder_old: str, folder_new: str):
    setting_write(db, "FILESFOLDER", folder_new)
    if isdir(folder_old):
        print("Moving files to new location... ", end="", flush=True)
        move(folder_old, folder_new)
        print("Done")


def users_download(api: FAAPI, db: Connection, users: List[str], folders: List[str]):
    for user, folder in ((u, f) for u in users for f in folders):
        print(f"Downloading: {user}/{folder}")
        tot, fail = user_download(api, db, user, folder)
        print("Submissions downloaded:", tot)
        print("Submissions failed:", fail)


def submissions_download(api: FAAPI, db: Connection, sub_ids: List[str]):
    if sub_ids_fail := list(filter(lambda i: not i.isdigit(), sub_ids)):
        print("The following ID's are not correct:", *sub_ids_fail)
    for sub_id in map(int, filter(lambda i: i.isdigit(), sub_ids)):
        print(f"Downloading {sub_id:010} ", end="", flush=True)
        submission_download(api, db, sub_id)


def users_update(api: FAAPI, db: Connection):
    users_folders: List[Tuple[str, str]] = select_all(db, "USERS", ["USERNAME", "FOLDERS"])
    tot: int = 0
    fail: int = 0
    for user, user_folders in users_folders:
        for folder in user_folders.split(","):
            print(f"Downloading: {user}/{folder}")
            tot_tmp, fail_tmp = user_download(api, db, user, folder, 1)
            tot += tot_tmp
            fail += fail_tmp
    print("Submissions downloaded:", tot)
    print("Submissions failed:", fail)
    setting_write(db, "LASTUPDATE", str(datetime.now().timestamp()))


def submission_make(id_: Union[int, str], author: str, title: str,
                    date: str, category: str, species: str,
                    gender: str, rating: str, tags: str = "",
                    description: str = "", file_url: str = "",
                    file_local_url: str = ""
                    ) -> Tuple[Sub, Optional[bytes]]:
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

    sub: Sub = Sub()
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


def submissions_search(db: Connection,
                       author: List[str] = None, title: List[str] = None, date: List[str] = None,
                       description: List[str] = None, tags: List[str] = None, category: List[str] = None,
                       species: List[str] = None, gender: List[str] = None, rating: List[str] = None
                       ) -> List[tuple]:
    author = [] if author is None else author
    title = [] if title is None else title
    date = [] if date is None else date
    description = [] if description is None else description
    tags = [] if tags is None else tags
    category = [] if category is None else category
    species = [] if species is None else species
    gender = [] if gender is None else gender
    rating = [] if rating is None else rating

    assert any((author, title, date, description, tags, category, species, gender, rating))

    wheres: List[str] = [
        " OR ".join(["UDATE like ?"] * len(date)),
        " OR ".join(["lower(RATING) like ?"] * len(rating)),
        " OR ".join(["lower(GENDER) like ?"] * len(gender)),
        " OR ".join(["lower(SPECIES) like ?"] * len(species)),
        " OR ".join(["lower(CATEGORY) like ?"] * len(category)),
        " OR ".join(["lower(AUTHOR) like ?"] * len(author)),
        " OR ".join(["lower(TITLE) like ?"] * len(title)),
        " OR ".join(["lower(TAGS) like ?"] * len(tags)),
        " OR ".join(["lower(DESCRIPTION) like ?"] * len(description))
    ]

    wheres_str = " AND ".join(map(lambda p: "(" + p + ")", filter(len, wheres)))

    return db.execute(
        f"""SELECT * FROM SUBMISSIONS WHERE {wheres_str}""",
        date + rating + gender + species + category + author + title + tags + description
    ).fetchall()


def submissions_print(subs: List[tuple], sort: bool = True):
    space_id: int = 10
    space_user: int = 10
    space_date: int = 10
    space_term: int = get_terminal_size()[0]

    index_id: int = keys_submissions.index("ID")
    index_user: int = keys_submissions.index("AUTHOR")
    index_date: int = keys_submissions.index("UDATE")
    index_title: int = keys_submissions.index("TITLE")

    if sort:
        subs.sort(key=lambda s: (s[index_user], s[index_date]))

    print(f"{'ID':^{space_id}} | {'User':^{space_user}} | {'Date':^{space_date}} | Title")
    for sub in subs:
        print(
            f"{str(sub[index_id])[:space_id].zfill(space_id)} | " +
            f"{sub[index_user][:space_user]:<{space_user}} | " +
            f"{sub[index_date][:space_date]:<{space_date}} | " +
            sub[index_title][:(space_term - space_id - space_user - space_date - 10)]
        )
