import requests, bs4
import re
import os, sys
import time
import filetype
import codecs
import FA_tools as fatl
import FA_var as favar
from FA_db import sub_exists, sub_read, sub_ins

months = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12",
}


def get_page(ID):
    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get page")
    url = "https://www.furaffinity.net/view/" + ID
    page = favar.variables.Session.get(url)
    page = bs4.BeautifulSoup(page.text, "lxml")

    if not page.find("div", "submission-artist-container"):
        fatl.log.verbose(
            f'DOWNLOAD SUBMISSION -> ID:{ID} get page error "submission-artist-container"'
        )
        page = None
    elif not page.find("h2", "submission-title-header"):
        fatl.log.verbose(
            f'DOWNLOAD SUBMISSION -> ID:{ID} get page error "submission-title-header"'
        )
        page = None
    elif not page.find("meta", {"name": "twitter:data1"}):
        fatl.log.verbose(
            f'DOWNLOAD SUBMISSION -> ID:{ID} get page error "twitter:data1"'
        )
        page = None
    elif not page.find("div", "sidebar-section-no-bottom"):
        fatl.log.verbose(
            f'DOWNLOAD SUBMISSION -> ID:{ID} get page error "sidebar-section-no-bottom"'
        )
        page = None

    return page


def get_info(page, ID):
    data = []

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get author")
    author = page.find("div", "submission-artist-container")
    author = author.find("h2").string
    data.append(author)

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get title")
    title = page.find("h2", "submission-title-header")
    title = title.string
    if title == None:
        title = ""
    data.append(title)

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get date")
    date_r = page.find("meta", {"name": "twitter:data1"})
    date_r = date_r.get("content").replace(",", "")
    date_r = date_r.split(" ")
    date = [date_r[2], "", date_r[1].rjust(2, "0")]
    date[1] = months.get(date_r[0])
    data.append("-".join(date))

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get keywords")
    keyw = []
    for k in page.find_all("span", "tags"):
        keyw.append(k.string)
    keyw = keyw[0 : int(len(keyw) / 2)]
    keyw.sort(key=str.lower)
    data.append(" ".join(keyw))

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get category, species, gender")
    extras_raw = [
        str(e) for e in page.find("div", "sidebar-section-no-bottom").find_all("div")
    ]

    extras = {}
    for e in extras_raw:
        e_typ = re.sub(":</strong>.*", "", e)
        e_typ = re.sub(".*<strong>", "", e_typ)
        e_typ = e_typ.lower()

        e_val = re.sub(".*</strong>( )*", "", e)
        e_val = re.sub("</div>.*", "", e_val)

        extras[e_typ] = e_val.replace("&gt;", ">")
    data += [
        extras.get("category", "All > All"),
        extras.get("species", "Unspecified / Any"),
        extras.get("gender", "Any"),
    ]

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get rating")
    rating = page.find("meta", {"name": "twitter:data2"})
    rating = rating.get("content").lower()
    data.append(rating)

    return data


def get_link(page, ID):
    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get link")
    link = page.find("a", "button download-logged-in")
    link = "https:" + link.get("href")

    return link


def get_desc(page, ID):
    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get description")
    desc = page.find("div", "submission-description-container")
    desc = str(desc)
    desc = desc.split("</div>", 1)[-1]
    desc = desc.rsplit("</div>", 1)[0]
    desc = desc.strip()

    return desc


def get_file(link, folder, ID, quiet, speed):
    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} get file")
    if os.path.isfile(folder + "/submission.temp"):
        os.remove(folder + "/submission.temp")

    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} remote file check & size")
    if not quiet:
        print("[Sizing Sub]", end="", flush=True)
    try:
        sub = requests.get(link, stream=True)
    except:
        if not quiet:
            print(("\b" * 11) + "File Error", end="", flush=True)
        fatl.log.normal(f"DOWNLOAD SUBMISSION -> ID:{ID} remote file fail")
        return False

    if not quiet:
        print("\b" + "\b \b" * 10, end="", flush=True)

    size = requests.head(link)
    size = size.headers
    if "Content-Length" in size.keys():
        size = size["Content-Length"]
        size = int(size)
    else:
        if not quiet:
            print("Size Error", end="", flush=True)
        size = 0

    with open(folder + "/submission.temp", "wb") as f:
        fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} remote file download")
        chunks = 0
        bar = 1
        for chunk in sub.iter_content(chunk_size=1024):
            if not quiet and size and (chunks * 1024) >= bar * (size / 10.0):
                print("=", end="", flush=True)
                bar += 1
            if chunk:
                f.write(chunk)
                chunks += 1
            if speed < 2:
                time.sleep(0.01)
        if not quiet and size:
            print("=" * (10 - bar + 1), end="", flush=True)

    if not quiet:
        print(("\b \b" * 10) + "Saving Sub", end="", flush=True)

    if not os.path.isfile(folder + "/submission.temp"):
        fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} remote file download error")
        return False

    ext = filetype.guess_extension(folder + "/submission.temp")
    if ext == None:
        ext = link.split(".")[-1]
        if ext == link.split("/")[-1]:
            ext = None
    elif ext == "zip":
        ext = link.split(".")[-1]
        if ext == link.split("/")[-1]:
            ext = None
    fatl.log.verbose(f"DOWNLOAD SUBMISSION -> ID:{ID} downloaded file extension:{ext}")
    if os.path.isfile(folder + "/submission." + str(ext)):
        os.remove(folder + "/submission." + str(ext))
    os.rename(folder + "/submission.temp", folder + "/submission." + str(ext))

    if ext:
        return "submission." + str(ext)
    else:
        return False


def str_clean(string):
    if string == None or string == "":
        return ""
    return re.sub("[^\x00-\x7F]", "", string)


def dl_sub(ID, quiet, check, speed, db_only, overwrite=False):
    fatl.log.normal(f"DOWNLOAD SUBMISSION -> ID:{ID}")
    if check and sub_exists(ID):
        fatl.log.normal(f"DOWNLOAD SUBMISSION -> ID:{ID} found in SUBMISSIONS database")
        if not quiet:
            if sys.platform in ("win32", "cygwin"):
                cols = os.get_terminal_size()[0] - 44
            else:
                cols = os.get_terminal_size()[0] - 43
            if cols < 0:
                cols = 0
            title = str_clean(sub_read(ID, "title"))[0:cols]
            print("[Repository]" + (" " + title) * bool(title))
        return 2

    if not quiet:
        print("[Get Infos ]", end="", flush=True)

    folder = f"{favar.variables.files_folder}/{fatl.tiers(ID)}/{ID:0>10}"
    page = get_page(ID)
    if page == None:
        if not quiet:
            print("\b" * 11 + "Page Error")
        return 3
    data = get_info(page, ID)
    link = get_link(page, ID)
    desc = get_desc(page, ID)

    if not quiet:
        if sys.platform in ("win32", "cygwin"):
            cols = os.get_terminal_size()[0] - 44
        else:
            cols = os.get_terminal_size()[0] - 43
        if cols < 0:
            cols = 0
        title = str_clean(data[1])[0:cols]
        print(
            (" " + title + ("\b" * (len(title) + bool(cols - len(title)))))
            * bool(title),
            end="\b" * 12,
            flush=True,
        )
        if sys.platform in ("win32", "cygwin") and cols and cols == len(title):
            print("\b", end="", flush=True)

    if not db_only:
        fatl.log.verbose(f'DOWNLOAD SUBMISSION -> ID:{ID} create folder "{folder}"')
        os.makedirs(folder, exist_ok=True)
        subf = get_file(link, folder, ID, quiet, speed)
    else:
        if not quiet:
            print("[          ]", end="\b", flush=True)
        subf = 0

    if not quiet:
        print("\b" * 10 + "Saving DB ", end="", flush=True)

    if not db_only:
        fatl.log.verbose(
            f"DOWNLOAD SUBMISSION -> ID:{ID} save description and informations"
        )
        with codecs.open(folder + "/description.html", encoding="utf-8", mode="w") as f:
            f.write(desc)

        with open(folder + "/info.txt", "w") as f:
            f.write(f"Author: {data[0]}\n")
            f.write(f"Title: {data[1]}\n")
            f.write(f"Upload date: {data[2]}\n")
            f.write(f"Keywords: {data[3]}\n")
            f.write(f"ID: {ID}\n")
            f.write(f"File: {link}\n")

    sub_info = (
        ID,  # ID
        data[0],  # authorurl
        data[0].lower().replace("_", ""),  # author
        data[1],  # title
        data[2],  # udate
        desc,  # description
        data[3],  # tags
        data[4],  # category
        data[5],  # species
        data[6],  # gender
        data[7],  # rating
        link,  # filelink
        subf,  # filename
        folder.split("/", 1)[-1],  # location
        1,  # server
    )
    sub_ins(sub_info, overwrite)

    if subf == False:
        if not quiet:
            print(("\b" * 10) + "File Error")
        return 1
    else:
        if not quiet:
            print(("\b" * 10) + "Downloaded")
        return 0
