# FALocalRepo

[![version_pypi](https://img.shields.io/pypi/v/falocalrepo?logo=pypi)](https://pypi.org/project/falocalrepo/)
[![version_gitlab](https://img.shields.io/badge/dynamic/json?logo=gitlab&color=orange&label=gitlab&query=%24%5B%3A1%5D.name&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2Fmatteocampinoti94%252Ffalocalrepo%2Frepository%2Ftags)](https://gitlab.com/MatteoCampinoti94/FALocalRepo)
[![version_python](https://img.shields.io/pypi/pyversions/falocalrepo?logo=Python)](https://www.python.org)

[![issues_gitlab](https://img.shields.io/badge/dynamic/json?logo=gitlab&color=orange&label=issues&suffix=%20open&query=%24.length&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2Fmatteocampinoti94%252Ffalocalrepo%2Fissues%3Fstate%3Dopened)](https://gitlab.com/MatteoCampinoti94/FALocalRepo/issues)
[![issues_github](https://img.shields.io/github/issues/matteocampinoti94/falocalrepo?logo=github&color=blue)](https://github.com/MatteoCampinoti94/FALocalRepo/issues)

Pure Python program to download any user's gallery/scraps/favorites from the FurAffinity forum in an easily handled database.

## Introduction

This program was born with the desire to provide a relatively easy-to-use method for FA users to download submissions that they care about from the forum.

The data is stored into a SQLite database, and the submissions files are saved in a tiered tree structure based on their ID's. Using SQLite instead of a client-server database makes the program to be extremely portable, only needing a working Python 3.8+ installation to work, and allows the downloaded data to be moved and backed up by simply moving/copying the database file and submission files folder.

All download operations are performed through the custom FurAffinity scraping library [faapi](https://pypi.org/project/faapi/). To ensure proper crawling behavior the library strictly follows FurAffinity's [robots.txt](https://www.furaffinity.net/robots.txt) in regard to allowed paths and crawl delay. Furthermore, submission files downloads are throttled to 100 KB/s to ensure the program won't use too much bandwidth.

The database and file-storage functions are handled independently by the [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) package which performs all transactions, queries, and file operations.

The [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) package is used to provide the server functionalities of the program.

## Contents

1. [Installation and Update](#installation-and-update)
1. [Cookies](#cookies)
1. [Usage](#usage)
    1. [Environmental Variables](#environmental-variables)
    1. [Help](#help)
    1. [Init](#init)
    1. [Configuration](#configuration)
    1. [Download](#download)
    1. [Database](#database)
1. [Database](#database-1)
    1. [Settings](#settings)
    1. [Users](#users)
    1. [Submissions](#submissions)
    1. [Journals](#journals)
1. [Submission Files](#submission-files)
1. [Upgrading Database](#upgrading-database)
1. [Contributing](#contributing)
1. [Issues](#issues)
1. [Appendix](#appendix)

## Installation and Update

To install the program it is sufficient to use Python pip and get the package `falocalrepo`.

```shell
python3 -m pip install falocalrepo
```

Python 3.8 or above is needed to run this program, all other dependencies are handled by pip during installation. For information on how to install Python on your computer, refer to the official website [Python.org](https://www.python.org/).

To upgrade the `falocalrepo` and its dependencies, use pip to upgrade all three components.

```shell
python3 -m pip install --upgrade falocalrepo faapi falocalrepo-database falocalrepo-server
```

To check for updates use the `--updates` option when launching the program. A message will be if there is an update available for any component.

The program needs cookies from a logged-in FurAffinity session to download protected pages. Without the cookies the program can still download publicly available pages, but others will return empty. See [#Cookies](#cookies) for more details on which cookies to use.

**Warning**: FurAffinity theme template must be set to "modern". Can be changed at [furaffinity.net/controls/settings/](https://www.furaffinity.net/controls/settings/).

## Cookies

The scraping library used by this program needs two specific cookies from a logged-in FurAffinity session. These are cookie `a` and cookie `b`.

As of 2020-08-09 these take the form of hexadecimal strings like `356f5962-5a60-0922-1c11-65003b703038`.

The easiest way to obtain these cookies is by using a browser extension to extract your cookies and then search for `a` and `b`.<br>
Alternatively, the storage inspection tool of a desktop browser can also be used. For example on Mozilla's Firefox this can be opened with the &#8679;F9 shortcut.

To set the cookies use the `config cookies` command. See [#Configuration](#configuration) for more details.

## Usage

> **How to Read Usage Instructions**
> * `command` a static command keyword
> * `<arg>` `<param>` `<value>` an argument, parameter, value, etc... that must be provided to a command
> * `[<arg>]` an optional argument that can be omitted
> * `<arg1> | <arg2>` mutually exclusive arguments, only use one

To run the program, simply call `falocalrepo` in your shell after installation.

Running without arguments will prompt a help message with all the available options and commands.

The usage pattern for the program is as follows:

```
falocalrepo [-h | -v | -d | -s | -u] [<command> [<operation>] [<arg1> ... <argN>]]
```

Available options are:

* `-h, --help` show help message
* `-v, --version` show program version
* `-d, --database` show database version
* `-s, --server` show server version
* `-u, --updates` check for updates on PyPi

Available commands are:

* `help` display the manual of a command
* `init` create the database and exit
* `config` manage settings
* `download` perform downloads
* `database` operate on the database

_Note:_ all the commands except `help` will create and initialise the database if it is not present in the folder

_Note:_ only one instance of the program is allowed at any given time

When the database is first initialised, it defaults the submissions files folder to `FA.files`. This value can be changed using the [`config` command](#configuration).

Cookies need to be set manually with the config command before the program will be able to access protected pages.

### Environmental Variables

`falocalrepo` supports the following environmental variables:

* `FALOCALREPO_DATABASE` sets a path for the database rather than using the current folder. If the path basename ends with `.db` -- e.g. `~/Documents/FA/MyFA.db` -- , then a database file will be created/opened with that name. Otherwise, the path will be considered a folder, and a database named "FA.db" will be created therein.

### Help

`help [<command> [<operations>]]`

The `help` command gives information on the usage of the program and its commands and operations.

```
falocalrepo help
```
```
falocalrepo help download
```
```
falocalrepo help database search-users
```

### Init

The `init` command initialises the database or, if one is already present, updates to a new version - if available - and then exits.

It can be used to create the database and then manually edit it, or to update it to a new version without calling other commands.

### Configuration

`config [<setting> [<value1>] ... [<valueN>]]`

The `config` command allows to change the settings used by the program.

Running the command alone will list the current values of the settings stored in the database. Running `config <setting>` without value arguments will show the current value of that specific setting.

Available settings are:

* `list` list stored settings.
* `cookies [<cookie a> <cookie b>]` the cookies stored in the database.
```
falocalrepo config cookies 38565475-3421-3f21-7f63-3d341339737 356f5962-5a60-0922-1c11-65003b703038
```
* `files-folder [<new folder>]` the folder used to store submission files. This can be any path relative to the folder of the database. If a new value is given, the program will move any files to the new location.
```
falocalrepo config files-folder SubmissionFiles
```

### Download

`download <operation> [<option>=<value>] [<arg1>] ... [<argN>]`

The `download` command performs all download and repository update operations.

Available operations are:

* `users <user1>[,...,<userN>] <folder1>[,...,<folderN>]` download specific user folders. Requires two arguments with comma-separated users and folders. Prepending `list-` to a folder allows to list all remote items in a user folder without downloading them. Supported folders are:
    * `gallery`
    * `scraps`
    * `favorites`
    * `journals`
```
falocalrepo download users tom,jerry gallery,scraps,journals
```
```
falocalrepo download users tom,jerry list-favorites
```
* `update [stop=<n>] [<user1>,...,<userN>] [<folder1>,...,<folderN>]` update the repository by checking the previously downloaded folders (gallery, scraps, favorites or journals) of each user and stopping when it finds a submission that is already present in the repository. Can pass a list of users and/or folders that will be updated if in the database. To skip users, use `@` as argument. The `stop=<n>` option allows to stop the update after finding `n` submissions in a user's database entry, defaults to 1. If a user is deactivated, the folders in the database will be prepended with a '!', and the user will be skipped when update is called again.
```
falocalrepo download update stop=5
```
```
falocalrepo download update @ gallery,scraps
```
```
falocalrepo download update tom,jerry
```
* `submissions <id1> ... [<idN>]` download specific submissions. Requires submission IDs provided as separate arguments.
```
falocalrepo download submissions 12345678 13572468 87651234
```
* `journals <id1> ... [<idN>]` download specific journals. Requires journal IDs provided as separate arguments.
```
falocalrepo download journals 123456 135724 876512
```

### Database

`database [<operation> [<param1>=<value1> ... <paramN>=<valueN>]]`

The `database` command allows operating on the database. Used without an operation command shows the database information, statistics (number of users and submissions and time of last update), and version.

All search operations are conducted case-insensitively using the SQLite [`like`](https://sqlite.org/lang_expr.html#like) expression which allows for a limited pattern matching. For example this expression can be used to search two words together separated by an unknown amount of characters `%cat%mouse%`. Fields missing wildcards will only match an exact result, i.e. `cat` will only match a field equal to `cat` tag whereas `%cat%` wil match a field that has contains `cat`.

All search operations support the extra `order`, `limit`, and `offset` parameters with values in SQLite [`ORDER BY` clause](https://sqlite.org/lang_select.html#the_order_by_clause), [`LIMIT` clause](https://sqlite.org/lang_select.html#the_limit_clause) format, and [`OFFSET` clause](https://sqlite.org/lang_select.html#the_limit_clause). The `order` parameter supports all fields of the specific search command.

Available operations are:

* `info` show database information, statistics and version.
* `history` show commands history
* `search-users [<param1>=<value1>] ... [<paramN>=<valueN>]` search the users entries using metadata fields. Search parameters can be passed multiple times to act as OR values. All columns of the users table are supported: [#Users](#users). Parameters can be lowercase. If no parameters are supplied, a list of all users will be returned instead.
```
falocalrepo database search-users folders=%gallery% gallery=%0012345678%
```
* `search-submissions [<param1>=<value1>] ... [<paramN>=<valueN>]` search the submissions entries using metadata fields. Search parameters can be passed multiple times to act as OR values. All columns of the submissions table are supported: [#Submissions](#submissions). Parameters can be lowercase. If no parameters are supplied, a list of all submissions will be returned instead.
```
falocalrepo database search-submissions tags=%cat,%mouse% date=2020-% category=%artwork% order="AUTHOR" order="ID"
```
```
falocalrepo database search-submissions tags=%cat% tags=%mouse% date=2020-% category=%artwork%
```
* `search-journals [<param1>=<value1>] ... [<paramN>=<valueN>]` search the journals entries using metadata fields. Search parameters can be passed multiple times to act as OR values.  All columns of the journals table are supported: [#Journals](#journals). Parameters can be lowercase. If no parameters are supplied, a list of all journals will be returned instead.
```
falocalrepo database search-journals date=2020-% author=CatArtist order="ID DESC"
```
```
falocalrepo database search-journals date=2020-% date=2019-% content=%commission%
```
* `add-user <param1>=<value1> ... <paramN>=<valueN>` add a user to the database manually. If the user is already present, the `folders` parameter will overwrite the existing value if given. The following parameters are necessary for a user entry to be accepted:
    * `username`<br>
  The following parameters are optional:
    * `folders`
```
falocalrepo database add-user username=tom folders=gallery,scraps
```
* `add-submission <param1>=<value1> ... <paramN>=<valueN>` add a submission to the database manually. The submission file is not downloaded and can instead be provided with the extra parameter `file_local_url`. The following parameters are necessary for a submission entry to be accepted:
    * `id` submission id
    * `title`
    * `author`
    * `date` date in the format YYYY-MM-DD
    * `category`
    * `species`
    * `gender`
    * `rating`<br>
The following parameters are optional:
    * `tags` comma-separated tags
    * `description`
    * `file_url` the url of the submission file, not used to download the file
    * `file_local_url` if provided, take the submission file from this path and put it into the database
```
falocalrepo database add-submission id=12345678 'title=cat & mouse' author=CartoonArtist \
    date=2020-08-09 category=Artwork 'species=Unspecified / Any' gender=Any rating=General \
    tags=cat,mouse,cartoon 'description=There once were a cat named Tom and a mouse named Jerry.' \
    'file_url=http://remote.url/to/submission.file' file_local_url=path/to/submission.file
```
* `add-journal <param1>=<value1> ... <paramN>=<valueN>` add a journal to the database manually. The following parameters are necessary for a journal entry to be accepted:
    * `id` journal id
    * `title`
    * `author`
    * `date` date in the format YYYY-MM-DD<br>
The following parameters are optional:
    * `content` the body of the journal
```
falocalrepo database add-journal id=12345678 title="An Update" author=CartoonArtist \
    date=2020-08-09 content="$(cat journal.html)"
```
* `remove-users <user1> ... [<userN>]` remove specific users from the database.
```
falocalrepo database remove-users jerry
```
* `remove-submissions <id1> ... [<idN>]` remove specific submissions from the database.
```
falocalrepo database remove-submissions 12345678 13572468 87651234
```
* `remove-journals <id1> ... [<idN>]` remove specific journals from the database.
```
falocalrepo database remove-journals 123456 135724 876512
```
* `server [host=<host>] [port=<port>]` starts a server at `<host>:<port>` to navigate the database using `falocalrepo-server`. Defaults to `0.0.0.0:8080`. See [falocalrepo-server](https://pypi.org/project/falocalrepo-server) for more details on usage.
```
falocalrepo database server host=127.0.0.1 port=5000
```
* `merge <path>` merge (or create) the database in the current folder with a second database located at `path`. `path` must point to the database file itself.
```
falocalrepo database merge ~/Documents/FA/FA.db
```
* `clean` clean the database using the SQLite [VACUUM](https://www.sqlite.org/lang_vacuum.html) function. Requires no arguments.

## Database

To store the metadata of the downloaded submissions, journals, users, cookies and statistics, the program uses a SQLite3 database. This database is built to be as light as possible while also containing all the metadata that can be extracted from a submission page.

To store all this information, the database uses four tables: `SETTINGS`, `USERS`, `SUBMISSIONS` and `JOURNALS`.

### Settings

The settings table contains settings for the program and statistics of the database.

* `HISTORY` list of executed commands in the format `[[<time1>, "<command1>"], ..., [<timeN>, "<commandN>"]]` (UNIX time in seconds)
* `COOKIES` cookies for the scraper, stored in JSON format
* `FILESFOLDER` location of downloaded submission files
* `VERSION` database version, this can differ from the program version

### Users

The users table contains a list of all the users that have been download with the program, the folders that have been downloaded, and the submissions found in each of those.

Each entry contains the following fields:

* `USERNAME` The URL username of the user (no underscores or spaces)
* `FOLDERS` the folders downloaded for that specific user.
* `GALLERY`
* `SCRAPS`
* `FAVORITES`
* `MENTIONS` this is a legacy entry used by the program up to version 2.11.2 (was named `EXTRAS`)
* `JOURNALS`

### Submissions

The submissions table contains the metadata of the submissions downloaded by the program and information on their files 

* `ID` the id of the submission
* `AUTHOR` the username of the author (uploader) in full format
* `TITLE`
* `DATE` upload date in the format YYYY-MM-DD
* `DESCRIPTION` description in html format
* `TAGS` keywords sorted alphanumerically and comma-separated
* `CATEGORY`
* `SPECIES`
* `GENDER`
* `RATING`
* `FILELINK` the remote URL of the submission file
* `FILEEXT` the extensions of the downloaded file. Can be empty if the file contained errors and could not be recognised upon download
* `FILESAVED` 1 if the file was successfully downloaded and saved, 0 if there was an error during download

### Journals

The journals table contains the metadata of the journals downloaded by the program.

* `ID` the id of the journal
* `AUTHOR` the username of the author (uploader) in full format
* `TITLE`
* `DATE` upload date in the format YYYY-MM-DD
* `CONTENT` content in html format

## Submission Files

Submission files are saved in a tiered tree structure based on their submission ID. IDs are zero-padded to 10 digits and then broken up in 5 segments of 2 digits; each of these segments represents a folder tha will be created in the tree.

For example, a submission `1457893` will be padded to `0001457893` and divided into `00`, `01`, `45`, `78`, `93`. The submission file will then be saved as `00/01/45/78/93/submission.file` with the correct extension extracted from the file itself - FurAffinity links do not always contain the right extension.

## Upgrading Database

When the program starts, it checks the version of the database against the one used by the program and if the latter is more advanced it upgrades the database.

_Note:_ Versions before 2.7.0 are not supported by falocalrepo version 3.0.0 and above. To update from those to the new version use version 2.11.2 to update the database to version 2.7.0

For details on upgrades and changes between database versions, see [falocalrepo-database](https://pypi.org/project/falocalrepo-database/).

## Contributing

All contributions and suggestions are welcome!

The only requirement is that any merge request must be sent to the GitLab project as the one on GitHub is only a mirror: [GitLab/FALocalRepo](https://gitlab.com/MatteoCampinoti94/FALocalRepo)

If you have suggestions for fixes or improvements, you can open an issue with your idea, see [#Issues](#issues) for details.

## Issues

If any problem is encountered during usage of the program, an issue can be opened on the project's pages on [GitLab](https://gitlab.com/MatteoCampinoti94/FALocalRepo/issues) (preferred) or [GitHub](https://github.com/MatteoCampinoti94/FALocalRepo/issues) (mirror repository).

Issues can also be used to suggest improvements and features.

When opening an issue for a problem, please copy the error message and describe the operation in progress when the error occurred.

## Appendix

### Earlier Releases

Release 3.0.0 was deleted from PyPi because of an error in the package information. However, it can still be found in the code repository under tag [v3.0.0](https://gitlab.com/MatteoCampinoti94/FALocalRepo/tags/v3.0.0).

Release binaries for versions 2.11.x can be found on GitLab under tags -> [FALocalRepo/tags 2.11](https://gitlab.com/MatteoCampinoti94/FALocalRepo/tags?search=v2.11)

Release binaries before and including 2.10.2 can be found on GitHub -> [Releases](https://github.com/MatteoCampinoti94/FALocalRepo/releases).