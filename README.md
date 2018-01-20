# FALocalRepo
Pure Python program to download any user's gallery/scraps/favorites and more from FurAffinity forum in an easily handled database.

**Warning**: A cookie file named FA.cookies in json format is needed.<br>
**Warning**: On windows safe exit does NOT work

## Usage
Use the provided binaries or build your own (build instructions at the end)

When the program starts a simple menu will appear, type the indicated number or key to select an option, there is no need to press ENTER.

1. `Download & Update`<br>
This menu allows to download a user gallery, scraps, favorites, extras or to update specific users and/or sections for the database.

    1. `Username: `<br>
    First field is reserved for users. To download or sync a specific user/s insert the username/s (url or userpage name are both valid)

    2. `Sections: `<br>
    Second field is reserved for sections. These can be:
        * g - Gallery
        * s - Scraps
        * f - Favorites
        * e - Extras partial<br>
        Searches submissions that contain ':iconusername:' OR ':usernameicon:' in the description AND NOT from username gallery/scraps
        * E - Extras full<br>
        Like partial but also searches for 'username' in the descriptions

        Sections can be omitted if 'Update' option is used

    3. `Options: `<br>
    Last field is reserved for options. These can be:
        * Y - Sync<br>
        Stops download when a submission already present in the user database entry is encountered
        * U - Update<br>
        Reads usernames from the database and downloads new submissions in the respective sections. This option can be used without specifying users or sections, if either is specified then the update will be limited to those user/s and/or section/s.
        * F - Force<br>
        Prevents update and sync from stopping the download at the first already present submission. Download stops at the first downloaded submission from page 3 included
        * A - All<br>
        Like 'F' but it will prevent interrupting the download for the whole section (this means **ALL** pages from each user will be checked, only use for a limited ammount of users)

    4. After inserting the necessary usernames/sections/options (and making sure their combination is valid) the program will:
        1. Check connection to FA website
        2. Build a Session object and add the provided cookies
        3. Check validity of cookies and bypass cloudflare

        If all these steps are completed without errors then the program will proceed to download the targets. As a bonus feature the program will also handle filetypes to make sure the submission files have the correct extension.

        The program also throttles download speed down to 100KB/sec to avoid taxing the forum's servers with a huge number of requests and downloads close to each other.

2. `Search`<br>
This menu allows to search in the database using one or more among author, title and tags.<br>
All search fields support regex, that means that for example to find 'dragon' you can either use 'dragon' or a section of it like 'dra', or something like `dr.\*n` (match 'dr' then any number '\*' of characters '.' followed by 'n'). More informations on regex syntax on [Wikipedia](https://en.wikipedia.org/wiki/Regular_expression) while a more complete reference can be found on [www.regular-expressions.info](https://www.regular-expressions.info/refquick.html). Even though regex is supported it is not necessary, without regex syntax the search function will still match any field that contains the text inserted.

    1. `Author`<br>
    Author name is matched with regex support

    2. `Title`<br>
    Title is matched using regex, like the title

    3. `Tags`<br>
    Tags are matched using regex as well, but with added support for negative matches. For example to search all submissions whose tags contain 'forest' but not 'autumn' you would type 'forest !autumn'. This is done surrounding tags to be included with `(?:.)*` and the tags to be excluded are enclosed in `(?!((?:.)*`tag`))`.<br>
    All regex syntax used under the hood is handled automatically and there is no need to use it though it is still supported, so for example you can include tags with `(forest|foliage)` ('forest' of 'foliage') and exclude them too: `!(autumn|winter)` (exlude 'autumn' and 'winter'). However using regex in tags is not recommended unless you know how to use it properly as it can lead to missing results: the tags are saved in alphanumerical order in the database and while the program orders the user-inserted tags (both the ones to include and the ones to exclude) before searching for them it cannot order them if regex is not used correctly. For example a search for `forest.*\W.*autumn` will not yield any results because 'autumn' never follows 'forest' in the database and the program cannot separate the two since it's a single string.

If you run the program on Unix systems then you can use CTRL-C to safely interrupt the program. It will complete the submission download in progress and exit at the first safe point, this works in all parts of the program, download, sync and update.<br>
If you run the program on Windows systems however safe exit will **NOT** work. This is caused byt the completely different way in which Windows handles signals, specifically SIGINT, interrupt signal sent by CTRL-C and used by this program. The functions are built to be realtively safe in how they handles database updates and downloads but it is suggested not to interrupt any operation to avoid errors.

## Cookies
The program needs to use cookies from a login session to successfully connect to FA. These cookies need to be in json format and can be easily extracted from Firefox/Chrome/Opera/Vivaldi/etc... using extensions or  manually. The value must be written in a file named FA.cookies<br>
What follows is an example cookie (not working).
```json
[
  {
    "domain": ".furaffinity.net",
    "expirationDate": 1511387940,
    "hostOnly": false,
    "httpOnly": false,
    "name": "__asc",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "kee3gpzjurkaq9fbyrubhys7epk",
    "id": 1
  },
]
```
The following cookie names are needed in order to successfully connect:
* \_\_asc
* \_\_auc
* \_\_cfduid
* \_\_gads
* \_\_qca
* a
* b
* n
* s
* \_adb

## Build & Run without binaries
This program is coded with Python 3.x in mind, Python 2.x will **NOT** work.

To run and/or build the program you will need the following pypi modules:
* [requests](https://github.com/requests/requests)
* [cfscrape](https://github.com/Anorov/cloudflare-scrape)
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
* [lxml](https://github.com/lxml/lxml/)
* [filetype](https://github.com/h2non/filetype.py)

And the following non-pypi modules:
* [python-read](https://github.com/MatteoCampinoti94/python-read)

The following modules are used but available by default:
* [json](https://docs.python.org/3/library/json.html)
* [os](https://docs.python.org/3.1/library/os.html)
* [re](https://docs.python.org/3.1/library/re.html)
* [signal](https://docs.python.org/3.1/library/signal.html) (only for Unix)
* [sqlite3](https://docs.python.org/3.1/library/sqlite3.html)
* [sys](https://docs.python.org/3.1/library/sys.html)
* [time](https://docs.python.org/3.1/library/time.html)

Once these modules are installed (suggest using `pip`) then the program can be run through the Python 3.x interpreter or built using `pyinstaller` or any other software.
