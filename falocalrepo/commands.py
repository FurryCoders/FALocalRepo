from os import get_terminal_size
from os.path import isdir
from shutil import move
from typing import List
from typing import Optional
from typing import Tuple

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


def download_users(api: FAAPI, db: Connection, users: List[str], folders: List[str]):
    for user, folder in ((u, f) for u in users for f in folders):
        print(f"Downloading: {user}/{folder}")
        tot, fail = user_download(api, db, user, folder)
        print("Submissions downloaded:", tot)
        print("Submissions failed:", fail)


def download_submissions(api: FAAPI, db: Connection, sub_ids: List[str]):
    if sub_ids_fail := list(filter(lambda i: not i.isdigit(), sub_ids)):
        print("The following ID's are not correct:", *sub_ids_fail)
    for sub_id in map(int, filter(lambda i: i.isdigit(), sub_ids)):
        print(f"Downloading {sub_id:010} ", end="", flush=True)
        submission_download(api, db, sub_id)


def update_users(api: FAAPI, db: Connection):
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


def make_submission(id_: int, author: str, title: str,
                    date: str, tags: List[str], category: str,
                    species: str, gender: str, rating: str,
                    description: str, file_url: str,
                    file_local_url: str = ""
                    ) -> Tuple[Sub, Optional[bytes]]:
    assert isinstance(id_, int) and id_ > 0
    assert isinstance(author, str) and author
    assert isinstance(title, str) and title
    assert isinstance(date, str) and date
    assert isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)
    assert isinstance(category, str) and category
    assert isinstance(species, str) and species
    assert isinstance(gender, str) and gender
    assert isinstance(rating, str) and rating
    assert isinstance(description, str)
    assert isinstance(file_url, str)
    assert isinstance(file_local_url, str)

    sub: Sub = Sub()
    sub_file: Optional[bytes] = None

    sub.id = id_
    sub.title = title
    sub.author = author
    sub.date = date
    sub.tags = tags
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


def search_submissions(db: Connection,
                       authors: List[str] = None, titles: List[str] = None, dates: List[str] = None,
                       descriptions: List[str] = None, tags: List[str] = None, categories: List[str] = None,
                       species: List[str] = None, genders: List[str] = None, ratings: List[str] = None
                       ) -> List[tuple]:
    authors = [] if authors is None else authors
    titles = [] if titles is None else titles
    dates = [] if dates is None else dates
    descriptions = [] if descriptions is None else descriptions
    tags = [] if tags is None else tags
    categories = [] if categories is None else categories
    species = [] if species is None else species
    genders = [] if genders is None else genders
    ratings = [] if ratings is None else ratings

    assert any((authors, titles, dates, descriptions, tags, categories, species, genders, ratings))

    wheres: List[str] = [
        " OR ".join(["UDATE = ?"] * len(dates)),
        " OR ".join(["lower(RATING) like ?"] * len(ratings)),
        " OR ".join(["lower(GENDER) like ?"] * len(genders)),
        " OR ".join(["lower(SPECIES) like ?"] * len(species)),
        " OR ".join(["lower(CATEGORY) like ?"] * len(categories)),
        " OR ".join(["lower(AUTHOR) like ?"] * len(authors)),
        " OR ".join(["lower(TITLE) like ?"] * len(titles)),
        " OR ".join(["lower(TAGS) like ?"] * len(tags)),
        " OR ".join(["lower(DESCRIPTION) like ?"] * len(descriptions))
    ]

    wheres_str = " AND ".join(map(lambda p: "(" + p + ")", filter(len, wheres)))

    return db.execute(
        f"""SELECT * FROM SUBMISSIONS WHERE {wheres_str}""",
        dates + ratings + genders + species + categories + authors + titles + tags
    ).fetchall()


def print_submissions(subs: List[tuple], sort: bool = True):
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
