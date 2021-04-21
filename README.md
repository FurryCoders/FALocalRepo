# FALocalRepo

[![version_pypi](https://img.shields.io/pypi/v/falocalrepo?logo=pypi)](https://pypi.org/project/falocalrepo/)
[![version_gitlab](https://img.shields.io/badge/dynamic/json?logo=gitlab&color=orange&label=gitlab&query=%24%5B%3A1%5D.name&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2Fmatteocampinoti94%252Ffalocalrepo%2Frepository%2Ftags)](https://gitlab.com/MatteoCampinoti94/FALocalRepo)
[![version_python](https://img.shields.io/pypi/pyversions/falocalrepo?logo=Python)](https://www.python.org)

[![issues_gitlab](https://img.shields.io/badge/dynamic/json?logo=gitlab&color=orange&label=issues&suffix=%20open&query=%24.length&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2Fmatteocampinoti94%252Ffalocalrepo%2Fissues%3Fstate%3Dopened)](https://gitlab.com/MatteoCampinoti94/FALocalRepo/issues)
[![issues_github](https://img.shields.io/github/issues/matteocampinoti94/falocalrepo?logo=github&color=blue)](https://github.com/MatteoCampinoti94/FALocalRepo/issues)

[![version_pypi](https://img.shields.io/pypi/v/faapi?logo=pypi&label=faapi)](https://pypi.org/project/faapi/)
[![version_pypi](https://img.shields.io/pypi/v/falocalrepo-database?logo=pypi&label=falocalrepo-database)](https://pypi.org/project/falocalrepo-database/)
[![version_pypi](https://img.shields.io/pypi/v/falocalrepo-server?logo=pypi&label=falocalrepo-server)](https://pypi.org/project/falocalrepo-server/)

Pure Python program to download any user's gallery/scraps/favorites from the FurAffinity forum in an easily handled
database.

## Introduction

This program was born with the desire to provide a relatively easy-to-use method for FA users to download submissions
that they care about from the forum.

The data is stored into a SQLite database, and the submissions files are saved in a tiered tree structure based on their
ID's. Using SQLite instead of a client-server database makes the program to be extremely portable, only needing a
working Python 3.9+ installation to work, and allows the downloaded data to be moved and backed up by simply
moving/copying the database file and submission files folder.

All download operations are performed through the custom FurAffinity scraping
library [faapi](https://pypi.org/project/faapi/). To ensure proper crawling behavior the library strictly follows
FurAffinity's [robots.txt](https://www.furaffinity.net/robots.txt) in regard to allowed paths and crawl delay.
Furthermore, submission files downloads are throttled to 100 KB/s to ensure the program won't use too much bandwidth.

The database and file-storage functions are handled independently by
the [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) package which performs all transactions,
queries, and file operations.

The [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) package is used to provide the server
functionalities of the program.

## Contents

1. [Installation and Update](#installation-and-update)
1. [Cookies](#cookies)
1. [Usage](#usage)
    1. [Environmental Variables](#environmental-variables)
    1. [Error Codes](#error-codes)
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

Python 3.9 or above is needed to run this program, all other dependencies are handled by pip during installation. For
information on how to install Python on your computer, refer to the official
website [Python.org](https://www.python.org/).

To upgrade the `falocalrepo` and its dependencies, use pip to upgrade all three components.

```shell
python3 -m pip install --upgrade falocalrepo faapi falocalrepo-database falocalrepo-server
```

To check for updates use the `--updates` option when launching the program. A message will be if there is an update
available for any component.

The program needs cookies from a logged-in FurAffinity session to download protected pages. Without the cookies the
program can still download publicly available pages, but others will return empty. See [#Cookies](#cookies) for more
details on which cookies to use.

**Warning**: FurAffinity theme template must be set to "modern". Can be changed
at [furaffinity.net/controls/settings/](https://www.furaffinity.net/controls/settings/).

## Cookies

The scraping library used by this program needs two specific cookies from a logged-in FurAffinity session. These are
cookie `a` and cookie `b`.

As of 2020-08-09 these take the form of hexadecimal strings like `356f5962-5a60-0922-1c11-65003b703038`.

The easiest way to obtain these cookies is by using a browser extension to extract your cookies and then search for `a`
and `b`.<br>
Alternatively, the storage inspection tool of a desktop browser can also be used. For example on Mozilla's Firefox this
can be opened with the &#8679;F9 shortcut.

To set the cookies use the `config cookies` command. See [#Configuration](#configuration) for more details.

## Usage

> **How to Read Usage Instructions**
>  * `command` a static command keyword
>  * `<arg>` `<param>` `<value>` an argument, parameter, value, etc... that must be provided to a command
>  * `[<arg>]` an optional argument that can be omitted
>  * `<arg1> | <arg2>` mutually exclusive arguments, only use one

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

_Note:_ only one instance of the program is allowed at any given time when performing download operations

_Note:_ only one connection to a database is allowed at any given time, if the database is opened in other processes,
the program will close with an error

_Note_: the program will not operate if the version of the database does not match the version of
the `falocalrepo-database` module. Only `database info` and `database upgrade` commands can be run if the database is
not up to date.

When the database is first initialised, it defaults the submissions files folder to `FA.files`. This value can be
changed using the [`config` command](#configuration).

Cookies need to be set manually with the config command before the program will be able to access protected pages.

### Environmental Variables

`falocalrepo` supports the following environmental variables:

* `FALOCALREPO_DATABASE` sets a path for the database rather than using the current folder. If the path basename ends
  with `.db` -- e.g. `~/Documents/FA/MyFA.db` -- , then a database file will be created/opened with that name.
  Otherwise, the path will be considered a folder, and a database named "FA.db" will be created therein.
* `FALOCALREPO_DEBUG` always print traceback of caught exceptions, regardless of whether they are known or not.

### Error Codes

If the program encounters a fatal error, the error is printed to `STDERR` and the program exits with a specific error
code:

* 1 `MalformedCommand`, `UnknownCommand` command error.
* 2 `MultipleInstances` another instance of the program was detected.
* 3 `UnknownFolder` an unknown download folder was given to the [`download` command](#download).
* 4 `ConnectionError` a connection error was encountered during download.
* 5 `DatabaseError`, `IntegrityError` an error with the database file occurred.
* 6 `TypeError`, `AssertionError` a type error was encountered.
* 7 an unknown exception was encountered. The full traceback is saved to a `FA.log` file located in the current working
  directory.

The exception traceback is printed only for unknown exception (error 7). Using the `FALOCALREPO_DEBUG`
[environmental variable](#environmental-variables) forces printing of traceback for all exceptions.

### Help

`help [<command> [<operations>]]`

The `help` command gives information on the usage of the program and its commands and operations.

> ```
> falocalrepo help
> ```
> ```
> falocalrepo help download
> ```
> ```
> falocalrepo help database search-users
> ```

### Init

The `init` command initialises the database or, if one is already present, updates to a new version - if available - and
then exits.

It can be used to create the database and then manually edit it, or to update it to a new version without calling other
commands.

### Configuration

`config [<setting> [<value1>] ... [<valueN>]]`

The `config` command allows to change the settings used by the program.

Running the command alone will list the current values of the settings stored in the database.
Running `config <setting>` without value arguments will show the current value of that specific setting.

Available settings are:

* `list` list stored settings.
* `cookies [<cookie1 name>=<cookie1 value>] ... [<cookieN name>=<cookieN value>]` the cookies stored in the database.

> ```
> falocalrepo config cookies a=38565475-3421-3f21-7f63-3d341339737 b=356f5962-5a60-0922-1c11-65003b703038
> ```

* `files-folder [<new folder>]` the folder used to store submission files. This can be any path relative to the folder
  of the database. If a new value is given, the program will move any files to the new location.

> ```
> falocalrepo config files-folder SubmissionFiles
> ```

### Download

`download <operation> [<option>=<value>] [<arg1>] ... [<argN>]`

The `download` command performs all download and repository update operations. Submission thumbnails are downloaded
alongside the main data and are stored as `thumbnail.jpg` in the submission folder (
see [Submission Files](#submission-files)).

Available operations are:

* `users <user1>[,...,<userN>] <folder1>[,...,<folderN>]` download specific user folders. Requires two arguments with
  comma-separated users and folders. Prepending `list-` to a folder allows to list all remote items in a user folder
  without downloading them. Supported folders are:
    * `gallery`
    * `scraps`
    * `favorites`
    * `journals`

> ```
> falocalrepo download users tom,jerry gallery,scraps,journals
> ```
> ```
> falocalrepo download users tom,jerry list-favorites
> ```

* `update [stop=<n>] [deactivated=<deactivated>] [<user1>,...,<userN>] [<folder1>,...,<folderN>]` update the repository
  by checking the previously downloaded folders (gallery, scraps, favorites or journals) of each user and stopping when
  it finds a submission that is already present in the repository. Can pass a list of users and/or folders that will be
  updated if in the database. To skip users, use `@` as argument. The `stop=<n>` option allows to stop the update after
  finding `n` submissions in a user's database entry, defaults to 1. If a user is deactivated, the folders in the
  database will be prepended with a '!'. Deactivated users will be skipped when update is called, unless
  the `<deactivated>` option is set to `true`.

> ```
> falocalrepo download update stop=5
> ```
> ```
> falocalrepo download update deactivated=true @ gallery,scraps
> ```
> ```
> falocalrepo download update tom,jerry
> ```

* `submissions <id1> ... [<idN>]` download specific submissions. Requires submission IDs provided as separate arguments,
  if a submission is already in the database it is ignored.

> ```
> falocalrepo download submissions 12345678 13572468 87651234
> ```

* `journals <id1> ... [<idN>]` download specific journals. Requires journal IDs provided as separate arguments, if a
  journal is already in the database it is ignored.

> ```
> falocalrepo download journals 123456 135724 876512
> ```

### Database

`database [<operation> [<param1>=<value1> ... <paramN>=<valueN>]]`

The `database` command allows operating on the database. Used without an operation command shows the database
information, statistics (number of users and submissions and time of last update), and version.

All search operations are conducted case-insensitively using the SQLite [`like`](https://sqlite.org/lang_expr.html#like)
expression which allows for a limited pattern matching. For example this expression can be used to search two words
together separated by an unknown amount of characters `%cat%mouse%`. Fields missing wildcards will only match an exact
result, i.e. `cat` will only match a field equal to `cat` whereas `%cat%` wil match a field that contains `cat`.
Bars (`|`) can be used to isolate individual items in list fields.

All search operations support the extra `order`, `limit`, and `offset` parameters with values in
SQLite [`ORDER BY` clause](https://sqlite.org/lang_select.html#the_order_by_clause)
, [`LIMIT` clause](https://sqlite.org/lang_select.html#the_limit_clause) format,
and [`OFFSET` clause](https://sqlite.org/lang_select.html#the_limit_clause). The `order` parameter supports all fields
of the specific search command.

Available operations are:

* `info` show database information, statistics and version.
* `history` show commands history
* `search-users [json=<json>] [columns=<columns>] [<param1>=<value1>] ... [<paramN>=<valueN>]` search the users entries
  using metadata fields. Search parameters can be passed multiple times to act as OR values. All columns of the users
  table are supported: [#Users](#users). Parameters can be lowercase. If no parameters are supplied, a list of all users
  will be returned instead. If `<json>` is set to 'true', the results are printed as a list of objects in JSON format.
  If `<columns>` is passed, then the objects printed with the JSON option will only contain those fields.

> ```
> falocalrepo database search-users json=true folders=%gallery%
> ```

* `search-submissions [json=<json>] [columns=<columns>] [<param1>=<value1>] ... [<paramN>=<valueN>]` search the
  submissions entries using metadata fields. Search parameters can be passed multiple times to act as OR values. All
  columns of the submissions table are supported: [#Submissions](#submissions). Parameters can be lowercase. If no
  parameters are supplied, a list of all submissions will be returned instead. If `<json>` is set to 'true', the results
  are printed as a list of objects in JSON format. If `<columns>` is passed, then the objects printed with the JSON
  option will only contain those fields.

> ```
> falocalrepo database search-submissions tags=%|cat|%|mouse|% date=2020-% category=%artwork% order="AUTHOR" order="ID"
> ```
> ```
> falocalrepo database search-submissions json=true columns=id,author,title author='CatArtist' tags=%|cat|% tags=%|mouse|% date=2020-% category=%artwork%
> ```

* `search-journals [json=<json>] [columns=<columns>] [<param1>=<value1>] ... [<paramN>=<valueN>]` search the journals
  entries using metadata fields. Search parameters can be passed multiple times to act as OR values. All columns of the
  journals table are supported: [#Journals](#journals). Parameters can be lowercase. If no parameters are supplied, a
  list of all journals will be returned instead. If `<json>` is set to 'true', the results are printed as a list of
  objects in JSON format. If `<columns>` is passed, then the objects printed with the JSON option will only contain
  those fields.

> ```
> falocalrepo database search-journals date=2020-% author=CatArtist order="ID DESC"
> ```
> ```
> falocalrepo database search-journals json=true columns=id,author,title date=2020-% date=2019-% content=%commission%
> ```

* `add-user <json>` Add or replace a user entry into the database using metadata from a JSON file. If the user already
  exists in the database, fields may be omitted from the JSON, except for the ID. Omitted fields will not be replaced in
  the database and will remain as they are. The following fields are supported:
    * `username`<br>
      The following fields are optional:
    * `folders`

> ```
> falocalrepo database add-user ./user.json
> ```

* `add-submission <json> [file=<file>] [thumb=<thumb>]` Add or replace a submission entry into the database using
  metadata from a JSON file. If the submission already exists in the database, fields may be omitted from the JSON,
  except for the ID. Omitted fields will not be replaced in the database and will remain as they are. The
  optional `<file>` and `<thumb>` parameters allow adding or replacing the submission file and thumbnail respectively.
  The following fields are supported:
    * `id`
    * `title`
    * `author`
    * `date` date in the format YYYY-MM-DD
    * `description`
    * `category`
    * `species`
    * `gender`
    * `rating`
    * `type` image, text, music, or flash * 'folder' gallery or scraps
    * `fileurl` the remote URL of the submission file<br>
      The following fields are optional:
    * `tags` list of tags, if omitted it defaults to existing entry or empty
    * `favorite` list of users that faved the submission, if omitted it defaults to existing entry or empty
    * `mentions` list of mentioned users, if omitted it defaults to existing entry or mentions are extracted from the
      description
    * `userupdate` 1 if the submission is downloaded as part of a user gallery/scraps else 0, if omitted it defaults to
      entry or 0

> ```
> falocalrepo database add-submission add-submission ./submission/metadata.json \
>     file=./submission/submission.pdf thumb=./submission/thumbnail.jpg
> ```

* `add-journal <json>` Add or replace a journal entry into the database using metadata from a JSON file. If the journal
  already exists in the database, fields may be omitted from the JSON, except for the ID. Omitted fields will not be
  replaced in the database and will remain as they are. The following fields are supported:
    * `id`
    * `title`
    * `author`
    * `date` date in the format YYYY-MM-DD * 'content' the body of the journal<br>
      The following fields are optional:
    * `mentions` list of mentioned users, if omitted it defaults to existing entry or mentions are extracted from the
      content

> ```
> falocalrepo database add-journal ./journal.json"
> ```

* `remove-users <user1> ... [<userN>]` remove specific users from the database.

> ```
> falocalrepo database remove-users jerry
> ```

* `remove-submissions <id1> ... [<idN>]` remove specific submissions from the database.

> ```
> falocalrepo database remove-submissions 12345678 13572468 87651234
> ```

* `remove-journals <id1> ... [<idN>]` remove specific journals from the database.

> ```
> falocalrepo database remove-journals 123456 135724 876512
> ```

* `server [host=<host>] [port=<port>]` starts a server at `<host>:<port>` to navigate the database
  using `falocalrepo-server`. Defaults to `0.0.0.0:8080`.
  See [falocalrepo-server](https://pypi.org/project/falocalrepo-server) for more details on usage. Running the server
  does not occupy the database connection (it is only occupied when the server is actively searching the database),
  which allows running other `database` commands; `download` commands remain unavailable.

> ```
> falocalrepo database server host=127.0.0.1 port=5000
> ```

* `merge <path> [<table1>.<param1>=<value1> ... <tableN>.<paramN>=<valueN>]` Merge selected entries from a second
  database to the main database (the one opened with the program). To select entries, use the same parameters as the
  search commands precede by a table name. Search parameters can be passed multiple times to act as OR values. All
  columns of the entries table are supported. Parameters can be lowercase. If no parameters are passed then all the
  database entries are copied. If submissions entries are selected, their files are copied to the files' folder of the
  main database.

> ```
> falocalrepo database merge ~/Documents/FA.backup/A/FA.db users.username=a% \
>     submissions.author=a% journals.author=a%
> ```
> ```
> falocalrepo database merge ~/Documents/FA2020/FA.db submissions.date=2020-% \
>     journals.date=2020-%
> ```
> ```
> falocalrepo database merge ~/Documents/FA.backup/FA.db
> ```

* `copy <path> [<table1>.<param1>=<value1> ... <tableN>.<paramN>=<valueN>]` Copy selected entries to a new or existing
  database. To select entries, use the same parameters as the search commands precede by a table name. Search parameters
  can be passed multiple times to act as OR values. All columns of the entries table are supported. Parameters can be
  lowercase. If no parameters are passed then all the database entries are copied. If submissions entries are selected,
  their files are copied to the files' folder of the target database.

> ```
> falocalrepo database copy ~/Documents/FA.backup/A/FA.db users.username=a% \
>     submissions.author=a% journals.author=a%
> ```
> ```
> falocalrepo database copy ~/Documents/FA2020/FA.db submissions.date=2020-% \
>     journals.date=2020-%
> ```
> ```
> falocalrepo database copy ~/Documents/FA.backup/FA.db
> ```

* `clean` clean the database using the SQLite [VACUUM](https://www.sqlite.org/lang_vacuum.html) function. Requires no
  arguments.
* `upgrade` upgrade the database to the latest version

## Database

To store the metadata of the downloaded submissions, journals, users, cookies and statistics, the program uses a SQLite3
database. This database is built to be as light as possible while also containing all the metadata that can be extracted
from a submission page.

To store all this information, the database uses four tables: `SETTINGS`, `USERS`, `SUBMISSIONS` and `JOURNALS`.

> **How Lists Are Stored**<br>
> Some fields in the database table contain lists of items. These are stored as strings, with each item surrounded by
> bars (`|`). This allows to properly separate and search individual items regardless of their position in the list.<br>
> `|item1||item2|`<br>

### Settings

The settings table contains settings for the program and statistics of the database.

* `HISTORY` list of executed commands in the format `[[<time1>, "<command1>"], ..., [<timeN>, "<commandN>"]]` (UNIX time
  in seconds)
* `COOKIES` cookies for the scraper, stored in JSON format
* `FILESFOLDER` location of downloaded submission files
* `VERSION` database version, this can differ from the program version

### Users

The users table contains a list of all the users that have been download with the program, the folders that have been
downloaded, and the submissions found in each of those.

Each entry contains the following fields:

* `USERNAME` The URL username of the user (no underscores or spaces)
* `FOLDERS` the folders downloaded for that specific user, sorted and bar-separated

### Submissions

The submissions table contains the metadata of the submissions downloaded by the program and information on their files

* `ID` the id of the submission
* `AUTHOR` the username of the author (uploader) in full format
* `TITLE`
* `DATE` upload date in the format YYYY-MM-DD
* `DESCRIPTION` description in html format
* `TAGS` keywords sorted alphanumerically and bar-separated
* `CATEGORY`
* `SPECIES`
* `GENDER`
* `RATING`
* `TYPE` image, text, music, or flash
* `FILEURL` the remote URL of the submission file
* `FILEEXT` the extensions of the downloaded file. Can be empty if the file contained errors and could not be recognised
  upon download
* `FILESAVED` file and thumbnail download status: 00, 01, 10, 11. 1*x* if the file was downloaded 0*x* if not, *x*1 if
  thumbnail was downloaded, *x*0 if not
* `FAVORITE` a bar-separated list of users that have "faved" the submission
* `MENTIONS` a bar-separated list of users that are mentioned in the submission description as links
* `FOLDER` the folder of the submission (`gallery` or `scraps`)
* `USERUPDATE` whether the submission was added as a user update or favorite/single entry

### Journals

The journals table contains the metadata of the journals downloaded by the program.

* `ID` the id of the journal
* `AUTHOR` the username of the author (uploader) in full format
* `TITLE`
* `DATE` upload date in the format YYYY-MM-DD
* `CONTENT` content in html format
* `MENTIONS` a bar-separated list of users that are mentioned in the journal content as links
* `USERUPDATE` whether the journal was added as a user update or single entry

## Submission Files

Submission files are saved in a tiered tree structure based on their submission ID. IDs are zero-padded to 10 digits and
then broken up in 5 segments of 2 digits; each of these segments represents a folder tha will be created in the tree.

For example, a submission `1457893` will be padded to `0001457893` and divided into `00`, `01`, `45`, `78`, `93`. The
submission file will then be saved as `00/01/45/78/93/submission.file` with the correct extension extracted from the
file itself - FurAffinity links do not always contain the right extension.

## Upgrading Database

When the program starts, it checks the version of the database against the one used by the program and if the latter is
more advanced it upgrades the database.

_Note:_ Versions before 2.7.0 are not supported by falocalrepo version 3.0.0 and above. To update from those to the new
version use version 2.11.2 to update the database to version 2.7.0

For details on upgrades and changes between database versions,
see [falocalrepo-database](https://pypi.org/project/falocalrepo-database/).

## Contributing

All contributions and suggestions are welcome!

The only requirement is that any merge request must be sent to the GitLab project as the one on GitHub is only a
mirror: [GitLab/FALocalRepo](https://gitlab.com/MatteoCampinoti94/FALocalRepo)

If you have suggestions for fixes or improvements, you can open an issue with your idea, see [#Issues](#issues) for
details.

## Issues

If any problem is encountered during usage of the program, an issue can be opened on the project's pages
on [GitLab](https://gitlab.com/MatteoCampinoti94/FALocalRepo/issues) (preferred)
or [GitHub](https://github.com/MatteoCampinoti94/FALocalRepo/issues) (mirror repository).

Issues can also be used to suggest improvements and features.

When opening an issue for a problem, please copy the error message and describe the operation in progress when the error
occurred.

## Appendix

### Earlier Releases

Release 3.0.0 was deleted from PyPi because of an error in the package information. However, it can still be found in
the code repository under tag [v3.0.0](https://gitlab.com/MatteoCampinoti94/FALocalRepo/tags/v3.0.0).

Release binaries for versions 2.11.x can be found on GitLab
at [FALocalRepo/tags 2.11](https://gitlab.com/MatteoCampinoti94/FALocalRepo/tags?search=v2.11).

Release binaries before and including 2.10.2 can be found
in [GitHub Releases](https://github.com/MatteoCampinoti94/FALocalRepo/releases).
