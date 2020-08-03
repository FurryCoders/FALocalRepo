# FALocalRepo
Pure Python program to download any user's gallery/scraps/favorites and more from FurAffinity forum in an easily handled database.

**Warning:** New version under development in pre-alpha stage. Current version 2.11.2 does not work.

**Warning**: A cookie file named FA.cookies.json in json format is needed.<br>
**Warning**: You need to set the theme to 'beta' on FurAffinity<br>
**Warning**: On Windows safe interruption does NOT work prior to version 2.10<br>
**Warning**: On Unix system the provided binaries require installing the pypi modules used in this software (See `Build instructions`)

## Introduction
This program was born with the desire to provide a relatively easy-to-use method for FA users to download submissions that they care about from the forum. At the moment its a little more than a text interface in a terminal window with only basic search functionality, a GUI will be hopefully added in the near future.

## Contents
1. [Usage](#usage)
    1. [Download & Update](#download--update)
    2. [Search](#search)
    3. [Repair database](#repair-database)
    4. [Interrupt](#interrupt)
2. [Database](#database)
3. [Upgrade](#upgrading-from-earlier-versions)
4. [Cookies](#cookies)
5. [Build instructions](#build-instructions)
6. [Troubleshooting & Logging](#troubleshooting--logging)
    1. [Opening Issues](#opening-issues)
7. [Appendix](#appendix)

## Usage
Use the provided binaries or build your own (build instructions at the end) and run from the command line on Linux or double click on Windows.<br>
`[FA|FA.exe] [options]`

Options:
* `--raise`<br>
Allow exceptions to raise without special handling, useful for troubleshooting
* `--log`<br>
Log major program operations to a file named 'FA.log'
* `--logv`<br>
Log all operations (including sub-steps)

To always use specific options please consult a guide on how to modify default arguments for your operative system.

<br>
When the program starts a simple menu will appear, type the indicated number or key to select an option, there is no need to press ENTER.

### Download & Update
This menu allows to download a user gallery, scraps, favorites, extras or to update specific users and/or sections for the database.

When a submission is downloaded all its informations (except for the comments and user-made folders) are downloaded into a database located in the same folder the program is launched in. The file (artwork, story, audio, etc...) is saved inside a folder named 'FA.files' which contains all submissions in a tiered structure based on their ID (e.g submission '3704554' will be saved in the folder 'FA.files/0/3/704/0003704554'). Backup .txt and .html files are also saved with the file, they contain the basic informations and the description and are there for safety (in case the database is accidentally deleted). For a guide on the database structure see `Database` below.

1. `Username: `<br>
First field is reserved for users. To download or sync a specific user/s insert the username/s (url or userpage name are both valid). Usernames can be separated with spaces or commas.

2. `Sections: `<br>
Second field is reserved for sections. These can be:
    * `g` - Gallery
    * `s` - Scraps
    * `f` - Favorites
    * `e` - Extras partial<br>
    Searches submissions that contain ':iconusername:' OR ':usernameicon:' in the description and are not from the user's gallery/scraps.
    * `E` - Extras full<br>
    Like partial but also searches for 'username' in the description, keywords and title.

    Sections can be omitted if 'update' option is used.

3. `Options: `<br>
Last field is reserved for options. These can be:
    * `sync`<br>
    Stops download when a submission already present in the user database entry is encountered.
    * `update`<br>
    Reads usernames from the database and downloads new submissions in the respective sections. This option can be used without specifying users or sections, if either is specified then the update will be limited to those user/s and/or section/s.
    * `forceN`<br>
    Prevents update and sync from stopping the download at the first already present submission. Download stops at the first downloaded submission from page N+1. Example: 'force4' will download the first 4 pages with no interruption and will allow the download to stop from page 5.
    * `all`<br>
    Like 'force' but it will prevent interrupting the download for the whole section (this means **ALL** pages from each user will be checked, only use for a limited amount of users).
    * `slow`<br>
    Use lowest possible download speed and make sure each submission doesn't take less than 1.5 seconds.
    * `noindex`<br>
    Do not update indexes after completing the download.
    * `dbonly`<br>
    Do not save any file during download/update, save submissions only in the database.
    * `quit`<br>
    Quits the program when the current operation is completed.

    Note: options can be inserted with or without spaces between them.

4. After inserting the necessary usernames/sections/options (and making sure their combination is valid) the program will:
    1. Check connection to FA website
    2. Build a Session object and add the provided cookies
    3. Check validity of cookies and bypass cloudflare

    If all these steps are completed without errors then the program will proceed to download the targets. As a bonus feature the program will also handle filetypes to make sure the submission files have the correct extension.<br>
    If the the program cannot verify the cookies and connect to the forum then it will abort the download and check the cookies for some common errors.

    The program throttles download speed down to 100KB/sec to avoid taxing the forum's servers with a huge number of requests and downloads close to each other.

### Search
This menu allows to search in the database using one or more among user (with or w/o sections), title, tags, category, species, gender and rating.<br>

1. `User`<br>
Search users. Multiple users can be matched.

    * `Section`<br>
    If a user is selected the search can be restricted to a specific section/s using g, s, f, e.

2. `Title`<br>
Search titles.

3. `Description`<br>
Search inside submissions' descriptions.

3. `Tags`<br>
Tags are sorted automatically before search.

4. `Category` \*<br>
Matches the category of submissions, like 'Artwork', 'Story', etc...

5. `Species` \*<br>
Search species, like 'Vulpine', 'Feline', etc...

6. `Gender` \*<br>
Gender can be 'Male', 'Female', 'Any'.

7. `Rating` \*<br>
The rating can be 'general', 'mature' or 'adult'.

8. `Options`<br>
There are two possible options:
    * `regex`<br>
    Use regular expressions to search the database. Full regex syntax is supported in all fields.
    * `case`<br>
    Turn on case sensitivity on ALL fields. This works in both normal and regex mode.
    * `web`<br>
    Search on the website directly. Only user, title, tags, description and rating will be used.

If indexes aren't up to date, and web option wasn't used, they will be updated.

Results are ordered by username and date.<br>
When turned on case sensitivity will be enabled for all fields, this means that, for example, 'tiger' won't match anything as the species is saved as 'Tiger' on FA.<br>
If no results can be found in the local database the program will prompt to run the search on the website instead.

\* *As shown on the submission page on the main site.*

### Repair database
Selecting this entry will open the database repair menu. There are 6 possible choices.
1. `Submissions`<br>
This will start the analysis and repair of the SUBMISSIONS table.
    1. `ID`<br>
    Missing IDs will be flagged.<br>
    This error type doesn't have a fix yet as there is no clear way to identify the submission on FA. However the program cannot create this type of error.
    2. `Fields`<br>
    If the id passes the check then the other fields in the submission entry will be searched for misplaced empty strings, incorrect value types and incorrect location.<br>
    The program will try and fix the errors in-place, replacing NULL values with empty strings. If the automatic fixes are successful then the submission will be checked for missing files, if any is missing then the submission will be passed to the next step. However if the automatic fixes do not work then the corrupted entry will be erased from the database, the files (if any present) deleted and the submission downloaded again, thus also fixing eventual missing files.
    3. `Files`<br>
    If the previous checks have passed then the program will check that all submission files are present.<br>
    The program will simply erase the submission folder to remove any stray file (if any is present) and then download them again.

    Indexes will be redone and database optimized with sqlite `VACUUM` function.

2. `Submission files`<br>
This will start the analysis of the submission table in search of submissions whose `FILENAME` column was set to 0 (i.e. an error during the download or in the file itself) and whose `SERVER` column is not 0 (i.e. that are still present on the main website as far the database knows).<br>
This missing submission files will be downloaded from scratch again.

3. `Users`<br>
    1. `Empty users`<br>
    Users with no folders and no submissions saved will be deleted.
    3. `Repeating users`<br>
    Users with multiple entries.<br>
    All the entries will be merged, the copies deleted and a new entry created. This new entry will be checked for incorrect `FOLDERS` and empty sections.
    3. `Names`<br>
    Usernames with capital letters or underscores will be updated to lowercase and the underscores removed.
    4. `Full names`<br>
    Full usernames that do not match with their url version will be collected from the submissions database or the website. If both fail they will be substituted with the url version.
    5. `No folders`<br>
    Users whose folders entry is empty or missing sections with saved submissions (See `Database`&rarr;`USERS`&rarr;`FOLDERS`) will be updated with said sections (e.g. user 'tiger' has submissions saved in the `GALLERY` and `FAVORITES` sections but the `FOLDERS` column only contains 'g' so 'g' will be added to `FOLDERS`).
    6. `Empty sections`<br>
    Users with folders but no submissions saved (e.g. `FOLDERS` contains `s` but the `SCRAPS` column is empty) will be redownloaded from FA (submissions already present in the database won't be downloaded again but simply added to the user's database entry).

    Indexes will be redone and database optimized with sqlite `VACUUM` function.

4. `Infos`<br>
    1. `Repeated entries`<br>
    Repeated entries will be deleted.
    2. `Version error`<br>
    If the database version is missing or incorrect it will be fixed.
    3. `Database name`<br>
    If the database name is not set to '' it will be fixed.
    4. `Numbers errors`<br>
    Missing or incorrect totals will be fixed.
    5. `Update & Download time`<br>
    Missing or incorrect epoch and duration of last update and download will be reset to 0.
    5. `Index flag`<br>
    Missing or not 0/1 `INDEX` flag value.

    Indexes will be redone and database optimized with sqlite `VACUUM` function.

4. `All`<br>
Submissions, submission files, users and infos will all be checked and the database re-indexed and optimized.

5. `Analyze`<br>
Search for errors in all three tables but do not repair them.

6. `Index`<br>
Indexes will be updated.

7. `Optimize`<br>
Database will be optimized with sqlite `VACUUM` function.

### Interrupt
While the program is running you can use CTRL-C to interrupt the current operation safely. If a download is in progress it will complete the current submission and exit at the first safe point. Safe interrupt works in all sections of the program.<br>
If you're using a version of the program lower than 2.10 safe interruption won't work on Windows systems.

## Database
The database (named 'FA.db') contains three tables:
1. `INFOS`<br>
    * `DBNAME`<br>
    Database custom name, unused at the moment.
    * `VERSION`<br>
    Database version, this can differ from the program version.
    * `USERN`<br>
    Number of users in `USERS` table.
    * `SUBN`<br>
    Number of submissions in the `SUBMISSIONS` table.
    * `LASTUP`<br>
    Time when the last update was started (epoch time, in seconds).
    * `LASTUPT`<br>
    Duration of last update (in seconds).
    * `LASTDL`<br>
    Time when the last download was started (epoch time).
    * `LASTDLT`<br>
    Duration of last download (in seconds).
    * `INDEX`<br>
    Boolean value indicating whether indexes were updated after the last download/update.

2. `USERS`<br>
The USERS table contains a list of all the users that have been download with the program. Each entry contains the following:
    * `USER`<br>
    The url username of the user (no caps and no underscores).
    * `USERFULL`<br>
    The full username as chosen by the user (with caps and underscores if present).
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
    * `DESCRIPTION`<br>
    Description in html format.
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
* `2.3` &rarr; `2.6`<br>
Two columns in the `USERS` will be renamed (`NAME`&rarr;`USER` and `NAMEFULL`&rarr;`USERFULL`) and descriptions will be moved inside the database. It is recommended to run `Repair` (See `Usage`&rarr;`Repair database` for details) with a version lower than 2.6 to make sure all description files are present. When the upgrade is completed indexes will be created for all fields.<br>
Size of the database will increase by about 2,8KB per submission (averaged on a database of over 234k submissions which increased by about 653MB).<br>
The older version of the database will be saved as 'FA.v2_3.db'
* `2.6` &rarr; `2.7`<br>
Entry `INDEX` will be added to `INFOS` table.
This upgrade cannot be interrupted and resumed later, however it is very fast being mostly a copy-paste.

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
This program is written with Python 3.x, Python 2.x will **NOT** work.

To run and/or build the program you will need the following pypi modules:
* [requests](https://github.com/requests/requests)
* [cfscrape](https://github.com/Anorov/cloudflare-scrape)
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
* [lxml](https://github.com/lxml/lxml/)
* [filetype](https://github.com/h2non/filetype.py)

The following non-pypi modules (already included in this repo as submodules):
* [PythonRead](https://gitlab.com/MatteoCampinoti94/PythonRead)
* [SignalBlock](https://gitlab.com/MatteoCampinoti94/PythonSignalBlocking-CrossPlatform)

The following modules are used but available by default:
* [json](https://docs.python.org/3/library/json.html)
* [os](https://docs.python.org/3.1/library/os.html)
* [re](https://docs.python.org/3.1/library/re.html)
* [signal](https://docs.python.org/3.1/library/signal.html) (only for Unix)
* [sqlite3](https://docs.python.org/3.1/library/sqlite3.html)
* [sys](https://docs.python.org/3.1/library/sys.html)
* [time](https://docs.python.org/3.1/library/time.html)

Once these modules are installed (suggest using `pip`) then the program can be run through the Python 3.x interpreter or built using `pyinstaller` or any other software.

## Troubleshooting & Logging
The program is set up so that any unforeseen error interrupts the program after displaying the error details. To get extra information the program can be run with the `--raise` argument which will allow exceptions to raise normally.

To get details of all operations the program can be run with '--log' or '--logv' arguments, warning and errors are saved regardless of the settings. Details will be saved in a file named 'FA.log' with the format: "`YYYY-MM-DD hh:mm:ss.ssssss | LOG TYPE [N|V|W] | OPERATION -> detail`". Using '--log' will only log major passages; '--logv' will log all operations to file.

### Opening issues
Before opening an issue please run the program with '--raise' and '--logv' arguments and copy the resulting log and exception/s details printed on screen.

## Appendix
### Unverified commits
All commits before the 27th of January 2018 show as unverified because I accidentally revoked my old GPG key before adding a new one. They have all been added by me and can vouch for their authenticity.<br>
Some commits before e76e993b show as unverified, these were done with GitHub's editor and thus their GPG signature cannot be verified by GitLab.
Commits 96143db5-7d40880b (09-10/07/2018) are unverified because of an error with the GPG key.

### Early releases
Release binaries before and including v2.10.2 can be found on GitHub -> [Releases](https://github.com/MatteoCampinoti94/FALocalRepo/releases)
