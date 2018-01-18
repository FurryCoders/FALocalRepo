# FALocalRepo
Pure Python program to download any user's gallery/scraps/favorites and more from FurAffinity forum in an easily handled database.

**Warning**: A cookie file named FA.cookies in json format is needed.<br>
**Warning**: On windows safe exit and automated filetype management do NOT work

## Usage
Use the provided binaries or build your own (build instructions at the end)

1. `Insert username: `<br>
First field is reserved for users. To download or sync a specific user/s insert the username/s (url or userpage name are both valid)

2. `Insert sections: `<br>
Second field is reserved for sections. These can be:
    * g - Gallery
    * s - Scraps
    * f - Favorites
    * e - Extras partial<br>
    Searches submissions that contain ':iconusername:' OR ':usernameicon:' in the description AND NOT from username gallery/scraps
    * E - Extras full<br>
    Like partial but also searches for 'username' in the descriptions

    Sections can be omitted if 'Update' option is used

3. `Insert options: `<br>
Last field is reserved for options. These can be:
    * Y - Sync<br>
    Stops download when a submission already present in the user database entry is encountered
    * U - Update<br>
    Reads usernames from the database and downloads new submissions in the respective sections. This option can be used without specifying users or sections, if either is specified then the update will be limited to those user/s and/or section/s.
    * F - Force<br>
    Prevents update and sync from stopping download at the first already present submission. Download stops at the first downloaded submission from page 3 included
    * A - All<br>
    Like 'F' but it will prevent interrupting download for the whole section (this means **ALL** pages from each user will be checked, only use for a limited ammount of users)

After inserting the necessary usernames/sections/options (and making sure their combination is valid) the program will:
1. Check connection to FA website
2. Build a Session object and add the provided cookies
3. Check validity of cookies and bypass cloudflare

If all these steps are completed without errors then the program will proceed to download the targets. As a bonus feature the program will also handle filetypes to make sure the submission files have the correct extension.

If you run the program on Unix systems then you can use CTRL-C to safely interrupt the program. It will complete the submission download in progress and exit at the first safe point, this works in all parts of the program, download, sync and update.

If you run the program on Windows systems however safe exit will **NOT** work. This is caused byt the completely different way in which Windows handles signals, specifically SIGINT, interrupt signal sent by CTRL-C and used by this program. The functions are built to be realtively safe in how they handles database updates and downloads but it is suggested not to interrupt any operation to avoid errors. Automatic filetypes handling will not work either, instead the program will use the submission file link to determine the correct extension but this can cause problems, especially with image files as often they are incorrectly handled by FA. A future update will include a fix for this issue as well as a tool to check downloaded submission files and their filetypes.

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

The following modules are needed only on Unix for the time being:
* [python-magic](http://github.com/ahupp/python-magic)

The following modules are used but available by default:
* [json](https://docs.python.org/3/library/json.html)
* [os](https://docs.python.org/3.1/library/os.html)
* [re](https://docs.python.org/3.1/library/re.html)
* [sqlite3](https://docs.python.org/3.1/library/sqlite3.html)
* [sys](https://docs.python.org/3.1/library/sys.html)
* [time](https://docs.python.org/3.1/library/time.html)

Once these modules are installed (suggest using `pip`) then the program can be run through the Python 3.x interpreter or built using `pyinstaller` or any other software.
