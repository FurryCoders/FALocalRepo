# FALocalRepo
Pure Python program to download any user's gallery/scraps/favorites and more from FurAffinity forum in an easily handled database.

**Warning**: A cookie file named FA.cookies.json in json format is needed.<br>
**Warning**: You need to set the theme to 'beta' on FurAffinity<br>
**Warning**: On windows safe exit does NOT work

## Introduction
This program was born with the desire to provide a relatively easy-to-use method for FA users to download submissions that they care about from the forum. At the moment its a little more than a text interface in a terminal window with only basic search functionality, a GUI will be hopefully added in the near future.

When a submission is downloaded all its informations (except for the comments and user-made folders) are downloaded into a database located in the same folder the program is launched in. The file (artwork, story, audio, etc...) and the description are instead saved in separate files inside a folder named 'FA.files' which contains all submissions in a tiered structure based on their ID (e.g submission '3704554' will be saved in the folder 'FA.files/0/3/704/0003704554'). A backup informations txt is also saved with the description and file, it contains the basic informations and is there for safety (in case the database is accidentally deleted). For a guide on the database structure see `Database` below.

## Contents
1. [Usage](#usage)
    1. [Download](#download-update)
    2. [Search](#search)
    3. [Repair database](#repair-database)
2. [Database](#database)
3. [Upgrade](#upgrading-from-earlier-versions)
4. [Cookies](#cookies)
5. [Build instructions](#build-instructions)
6. [Appendix](#appendix)

## Usage
Use the provided binaries or build your own (build instructions at the end).

When the program starts a simple menu will appear, type the indicated number or key to select an option, there is no need to press ENTER.

### Download & Update
This menu allows to download a user gallery, scraps, favorites, extras or to update specific users and/or sections for the database.

1. `Username: `<br>
First field is reserved for users. To download or sync a specific user/s insert the username/s (url or userpage name are both valid). Usernames can be separated with spaces or commas.

2. `Sections: `<br>
Second field is reserved for sections. These can be:
    * g - Gallery
    * s - Scraps
    * f - Favorites
    * e - Extras partial<br>
    Searches submissions that contain ':iconusername:' OR ':usernameicon:' in the description AND NOT from username gallery/scraps.
    * E - Extras full<br>
    Like partial but also searches for 'username' in the descriptions.

    Sections can be omitted if 'update' option is used.

3. `Options: `<br>
Last field is reserved for options. These can be:
    * sync<br>
    Stops download when a submission already present in the user database entry is encountered.
    * update<br>
    Reads usernames from the database and downloads new submissions in the respective sections. This option can be used without specifying users or sections, if either is specified then the update will be limited to those user/s and/or section/s.
    * forceN<br>
    Prevents update and sync from stopping the download at the first already present submission. Download stops at the first downloaded submission from page N+1. Example: 'force4' will download the first 4 pages with no interruption and will allow the download to stop from page 5.
    * all<br>
    Like 'force' but it will prevent interrupting the download for the whole section (this means **ALL** pages from each user will be checked, only use for a limited amount of users).
    * quit<br>
    Quits the program when the current operation is completed.

    Note: options can be inserted with or without spaces between them.

4. After inserting the necessary usernames/sections/options (and making sure their combination is valid) the program will:
    1. Check connection to FA website
    2. Build a Session object and add the provided cookies
    3. Check validity of cookies and bypass cloudflare

    If all these steps are completed without errors then the program will proceed to download the targets. As a bonus feature the program will also handle filetypes to make sure the submission files have the correct extension.<br>
    If the the program cannot verify the cookies and connect to the forum then it will abort the download and check the cookies for some common errors.

    The program also throttles download speed down to 100KB/sec to avoid taxing the forum's servers with a huge number of requests and downloads close to each other.

### Search
This menu allows to search in the database using one or more among user (with or w/o sections), title, tags, category, species, gender and rating.<br>

1. `User`<br>
Search users. Multiple users can be matched.

    * `Section`<br>
    If a user is selected the search can be restricted to a specific section/s using g, s, f, e.

2. `Title`<br>
Search titles.

3. `Tags`<br>
Tags are sorted automatically before search.&#10013;

4. `Category`<br>
Matches the category of submissions, like 'Artwork', 'Story', etc...\*&#10013;

5. `Species`<br>
Search species, like 'Vulpine', 'Feline', etc...\*&#10013;

6. `Gender`<br>
Gender can be 'Male', 'Female', 'Any'.\*&#10013;

7. `Rating`<br>
The rating can be 'general', 'mature' or 'adult'.\*&#10013;

8. `Options`<br>
There are two possible options:
    * `regex`<br>
    Use regular expressions to search the database. Full regex syntax is supported in all fields.

    * `web`<br>
    Search on the website directly. Only user, title, tags and rating will be used.

Results are ordered by username and date.<br>
If no results can be found in the local database the program will prompt to run the search on the website instead.

\*As shown on the submission page on the main site.*<br>
&#10013;*Fields matched without case sensitivity*

### Repair database
Selecting this entry will start the automatic database repair functions. These are divided into three steps:
1. `Database analysis`<br>
The program will analyze all submissions and users entries in the database for different types of errors:
    1. `ID`<br>
    Missing IDs will be flagged.
    2. `Fields`<br>
    If the id passes the check then the other fields in the submission entry will be searched for misplaced empty strings, incorrect value types and incorrect location.
    3. `Files`<br>
    If the previous checks have passed then the program will check that all submission files are present.
    1. `Empty users`<br>
    Users with no folders and no submissions saved.
    3. `Repeating users`<br>
    User with multiple entries.
    3. `Names`<br>
    Usernames with capital letters or underscores.
    4. `Full names`<br>
    Full usernames that do not match with their url version.
    5. `No folders`<br>
    Users whose folders entry is empty or missing sections with saved submissions (See `Database`&rarr;`USERS`&rarr;`FOLDERS`).
    6. `Empty sections`<br>
    Users with folders but no submissions saved (e.g. `FOLDERS` contains `s` but the `SCRAPS` column is empty)

Analysis of submissions and/or users database can be skipped with CTRL-C on Unix systems

2. `Database repair`<br>
If errors where found then the program will try to fix them accordingly:
    1. `ID`<br>
    This error type doesn't have a fix yet as there is no clear way to identify the submission on FA. However the program cannot create this type of error.
    2. `Fields`<br>
    The program will try and fix the errors in-place, replacing NULL values with empty strings. If the automatic fixes are successful then the submission will be checked for missing files, if any is missing then the submission will be passed to the next step. However if the automatic fixes do not work then the corrupted entry will be erased from the database, the files (if any present) deleted and the submission downloaded again, thus also fixing eventual missing files.
    3. `Files`<br>
    The program will simply erase the submission folder to remove any stray file (if any is present) and then download them again.

    4. `Empty users`<br>
    Empty user entries will be deleted
    5. `Repeating users`<br>
    Multiple entries of the same user will all be merged, the copies deleted and a new entry created. This new entry will be checked for incorrect `FOLDERS` and empty sections.
    6. `Names`<br>
    Usernames will be updated to remove capital letters and underscores.
    7. `Full names`<br>
    Full usernames that do not match the url version will be collected from the submissions database or the website. If both fail they will be substituted with the url version.
    8. `No folders`<br>
    Users whose `FOLDERS` column is missing sections containing submissions will be updated with said sections (e.g. user 'tiger' has submissions saved in the `GALLERY` and `FAVORITES` sections but the `FOLDERS` column only contains 'g' so 'g' will be added to `FOLDERS`).
    9. `Empty sections`<br>
    If a user's `FOLDERS` contains one or more sections empty of submissions (e.g. user 'mouse' has 'g' in their `FOLDERS` but the `GALLERY` column is empty) these will be redownloaded from FA (submissions already present in the database won't be downloaded again but simply added to the user's database entry).

3. `Optimizing`<br>
After all errors (if any are found) are fixed then the program will use the sqlite `VACUUM` function to optimize the database and clean it up.

If you run the program on Unix systems then you can use CTRL-C to interrupt the current operation safely. If a download is in progress it will complete the current operation and exit at the first safe point. Safe interrupt works in all sections of the program.<br>
If you run the program on Windows systems however safe exit will **NOT** work. This is caused by the the completely different way in which Windows handles signals, specifically SIGINT, the interrupt signal sent by CTRL-C and used by this program. The functions are built to be relatively safe in how they handle database and download operations but it is suggested not to interrupt the program to avoid errors.

## Database
The database (named 'FA.db') contains three tables:
1. `INFOS`<br>
This table contains general informations about the database, some of which are not in use at the moment. There is an entry for the database version (see 'Upgrading from earlier versions' below), one for the custom name of the database (not implemented yet), one for the number of users, one for the number of submissions, one specifying the time the last updates and downloads where started and how long they took.

2. `USERS`<br>
The USERS table contains a list of all the users that have been download with the program. Each entry contains the following:
    * `NAME`<br>
    The url username of the user (no caps and no underscores).
    * `NAMEFULL`<br>
    The full username as choosen by the user (with caps and underscores if present).
    * `FOLDERS`<br>
    The sections downloaded for that specific user. A '!' beside a section means that the user was disabled, it is used as a flag for the program.*&#42;*
    * `GALLERY`, `SCRAPS`, `FAVORITES`, `EXTRAS`<br>
    These contain a list of the submissions IDs downloaded for each section.*&#42;*

    *&#42; For a guide on what each section means see `Usage`&rarr;`Sections`*


3. `SUBMISSIONS`<br>
The last table is a list of all the single submissions downloaded by the program. Each entry has 14 different values:
    * `ID`<br>
    The id of the submission
    * `AUTHOR`, `AUTHORURL`<br>
    The author username in normal format and url format (e.g. 'Flying_Tiger' and 'flyingtiger')
    * `TITLE`<br>
    The title
    * `UDATE`<br>
    Upload date
    * `TAGS`<br>
    The submission's keywords sorted alphanumerically
    * `CATEGORY`, `SPECIES`, `GENDER`, `RATING`<br>
    The category, species, gender and rating as listed on the submission's page on the forum
    * `FILELINK`, `FILENAME`<br>
    The link to the submission file on the forum and the name of the downloaded file (all files are named 'submission' + their proper extension) (an empty or 0 value means the file has an error on the forum and has not been downloaded)
    * `LOCATION`<br>
    The location in the current folder of the submission's file, description and backup informations file.
    * `SERVER`<br>
    This last field is defaulted to 1 and only updated to 0 if the program checks the submission on the forum and finds it missing (because the uploaded has either disabled or deleted it)

The database is built using sqlite so it can be easily opened and searched with a vast number of third-party programs. A good one is 'DB Browser for SQLite' (http://sqlitebrowser.org/) which is open source, cross-platform and has a project page here on GitHub.

## Upgrading from earlier versions
When the program is started it will check the database for its version. If the database version is lower than the program then it will update it depending on the difference between the two.
* `0.x` to `1.x` &rarr; `2.x`<br>
New informations handled by version 2 and onward will be downloaded and added to the database, these include submission category, rating, gender and species. Depending on the size of the database to be updated this process may take a long time.<br>
The older version of the database will be saved as 'FA.v1.db'
* `2.0` to `2.2` &rarr; `2.3`<br>
Full versions of users' nicknames will be collected from the submissions database or the website. If both fail the url version will be used instead.<br>
The older version of the database will be saved as 'FA.v2.db'

At each update step the program will save a backup copy of the database.

Update can be interrupted and resumed later without losing progress.

**Warning**: The update cannot be skipped, to keep using a specific version of the database you need to download the release relative to that version

## Cookies
The program needs to use cookies from a login session to successfully connect to FA. These cookies need to be in json format and can be easily extracted from Firefox/Chrome/Opera/Vivaldi/etc... using extensions or  manually. The value must be written in a file named FA.cookies.json<br>
(The value is fake)
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
* \_adb

Only 'name' and 'value' are needed for each cookie so the file can also be composed by entries like this:
```json
[
  {
    "name": "__asc",
    "value": "kee3gpzjurkaq9fbyrubhys7epk",
  },
]
```

## Build Instructions
This program is coded with Python 3.x in mind, Python 2.x will **NOT** work.

To run and/or build the program you will need the following pypi modules:
* [requests](https://github.com/requests/requests)
* [cfscrape](https://github.com/Anorov/cloudflare-scrape)
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
* [lxml](https://github.com/lxml/lxml/)
* [filetype](https://github.com/h2non/filetype.py)

And the following non-pypi modules:
* [PythonRead](https://github.com/MatteoCampinoti94/PythonRead) (Already included in this repo as a submodule)

The following modules are used but available by default:
* [json](https://docs.python.org/3/library/json.html)
* [os](https://docs.python.org/3.1/library/os.html)
* [re](https://docs.python.org/3.1/library/re.html)
* [signal](https://docs.python.org/3.1/library/signal.html) (only for Unix)
* [sqlite3](https://docs.python.org/3.1/library/sqlite3.html)
* [sys](https://docs.python.org/3.1/library/sys.html)
* [time](https://docs.python.org/3.1/library/time.html)

Once these modules are installed (suggest using `pip`) then the program can be run through the Python 3.x interpreter or built using `pyinstaller` or any other software.

## Appendix
### Unverified commits
All commits before the 27th of January 2018 show as unverified because I accidentally revoked my old gpg key before adding a new one. They have all been added by me and can vouch for their authenticity.
