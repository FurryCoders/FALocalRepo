<div align="center">

<img alt="logo" width="400" src="https://raw.githubusercontent.com/FurryCoders/Logos/main/logos/falocalrepo-transparent.png">

# FALocalRepo

Pure Python program to download submissions, journals, and user folders from the FurAffinity forum in an easily handled
database.

[![](https://img.shields.io/pypi/v/falocalrepo?logo=pypi)](https://pypi.org/project/falocalrepo/)
[![](https://img.shields.io/pypi/pyversions/falocalrepo?logo=Python)](https://www.python.org)

[![](https://img.shields.io/github/v/tag/FurryCoders/falocalrepo?label=github&sort=date&logo=github&color=blue)](https://github.com/FurryCoders/falocalrepo)
[![](https://img.shields.io/github/issues/FurryCoders/falocalrepo?logo=github&color=blue)](https://github.com/FurryCoders/falocalrepo/issues)

</div>

## Introduction

This program was born with the desire to provide a relatively easy-to-use method for FA users to download submissions
that they care about from the forum.

The data is stored into a SQLite database, and the submissions files are saved in a tiered tree structure based on their
ID's. Using SQLite instead of a client-server database makes the program extremely portable, only needing a working
Python 3.10+ installation to work, and allows the downloaded data to be moved and backed up by simply moving/copying the
database file and submissions files folder.

All download operations are performed through the custom FurAffinity scraping
library [faapi](https://pypi.org/project/faapi/). To ensure proper crawling behavior the library strictly follows
FurAffinity's [robots.txt](https://www.furaffinity.net/robots.txt) in regard to allowed paths and crawl delay.

The database and file-storage functions are handled independently by
the [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) package which performs all transactions,
queries, and file operations.

The [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) package is used to provide the server
functionalities of the program.

For an in-depth guide on the features of the program and guides on how to perform the most common operations, visit the
project's [GitHub wiki](https://github.com/FurryCoders/falocalrepo/wiki).

## Contents

1. [Requirements](#requirements)
2. [Installation and Update](#installation-and-update)
3. [Cookies](#cookies)
4. [Usage](#usage)
    1. [Environmental Variables](#environmental-variables)
    2. [Init](#init)
    3. [Login](#login)
    4. [Config](#config)
    5. [Download](#download)
    6. [Database](#database)
        1. [Database Query Language](#database-query-language)
    7. [Server](#server)
    8. [Completions](#completions)
    9. [Updates](#updates)
    10. [Help](#help)
    11. [Paw](#paw)
5. [Database](#database-1)
    1. [Users](#users)
    2. [Submissions](#submissions)
    3. [Journals](#journals)
    4. [Comments](#comments)
    5. [Settings](#settings)
    6. [History](#history)
6. [Submission Files](#submission-files)
7. [Upgrading Database](#upgrading-database)
8. [Contributing](#contributing)
9. [Issues](#issues)
10. [Appendix](#appendix)

## Requirements

Python 3.10 or above is needed to run this program, all other dependencies are handled by pip during installation. For
information on how to install Python on your computer, refer to the official
website [Python.org](https://www.python.org/).

The program needs cookies from a logged-in FurAffinity session to download protected pages. See [Cookies](#cookies) for
more details on which cookies to use.

**Warning**: FurAffinity theme template must be set to "modern". Can be changed
at [furaffinity.net/controls/settings/](https://www.furaffinity.net/controls/settings/).

## Installation and Update

To install the program it is sufficient to use Python pip and get the package `falocalrepo`.

```shell
pip install falocalrepo
```

To upgrade the program and its dependencies, use pip to upgrade all three components.

```shell
pip install --upgrade falocalrepo faapi falocalrepo-database falocalrepo-server
```

To check for updates use the [`updates` command](#updates). A message will appear if there is an update available for
any component.

_Note_: make sure that pip points to a Python 3.10 installation; you can check if it is correct using `pip --version`.

### Installation From Source

To install from source, clone the repository, then using [poetry](https://python-poetry.org)
run `poetry install` and `poetry build`. After the wheel has been built, you can install it using
pip `pip install dist/*.whl`.

## Cookies

The scraping library used by this program needs two specific cookies from a logged-in FurAffinity session. These are
cookie `a` and cookie `b`. The cookies' values usually take the form of hexadecimal strings
like `356f5962-5a60-0922-1c11-65003b703038`.

The easiest way to obtain these cookies is by using the [`login`](#login) command, which will let you log in with your
browser of choice and then automatically extract the necessary cookies.

Alternatively, a browser extension or the browser's developer tools can be used to extract the cookies.

To set the cookies manually use the `config cookies` command. See [Config](#config) for more details.

## Usage

> **How to Read Usage Instructions**
>  * `command` a static command keyword
>  * `{arg1|arg2}` mutually exclusive arguments, only use one
>  * `<arg>` `<param>` `<value>` an argument, parameter, value, etc. that must be provided to a command
>  * `--option <value>` an option argument with a static key and a value
>  * `[<arg>]` an optional argument that can be omitted

To run the program, simply call `falocalrepo` in your shell after installation.

Running without arguments will prompt a help message with all the available options and commands.

The usage pattern for the program is as follows:

```
falocalrepo [OPTIONS] COMMAND [ARGS]...
```

Available options are:

* `--version` Show version and exit.
* `--versions` Show components' versions and exit.

The following global options are available for all commands:

* `--database` Specify a database different from the default (FA.db in the current working directory). Overrides
  the `FALOCALREPO_DATABASE` environment variable (see [Environmental Variables](#environmental-variables)).
* `--color / --no-color` Toggle ANSI colors.
* `-h, --help` Show help message and exit.

Available commands are:

* `init` Initialise the database.
* `login` Login using a browser.
* `config` Change settings.
* `download` Download resources.
* `database` Operate on the database.
* `server` Start local server to browse database.
* `completions` Generate tab-completion scripts.
* `updates` Check for updates to components.
* `help` Show the help for a command.
* `paw` Print the paw.

_Note:_ only one connection to a database is allowed at any given time, if the database is opened in other processes,
the program will close with an error.

_Note_: the program will not operate if the version of the database does not match the version of
the `falocalrepo-database` module. Only `database info` and `database upgrade` commands can be run if the database is
not up-to-date.

When the database is first initialised, it sets the submissions files folder to `FA.files` (relative to the database
location). This value can be changed using the [`config` command](#config).

Cookies need to be set manually with the config command before the program will be able to access protected pages.

### Environmental Variables

`falocalrepo` supports the following environmental variables:

* `FALOCALREPO_CRAWL_DELAY` sets a different crawl delay for the `download` operations.<br/>
  _Note_: the crawl delay can only be higher or equal to the one in
  FurAffinity's [robots.txt](https://furaffinity.net/robots.txt) (1 second), lower values will cause an error.
* `FALOCALREPO_FA_ROOT` sets a different root for Fur Affinity pages (default is `https://furaffinity.net`).
* `FALOCALREPO_DATABASE` sets a path for the database rather than using the current folder.
* `FALOCALREPO_MULTI_CONNECTION` allow operating on the database even if it is already opened in other processes.<br/>
  **Warning**: using this option may cause the database to become corrupt and irreparable.
* `FALOCALREPO_NO_COLOR` turn off colors for all commands.

### BBCode

Starting from version 4.4.0, falocalrepo supports saving data in BBCode format instead of HTML. This is achieved thanks
to the HTML to BBCode converter introduced with [faapi 3.8.0](https://pypi.org/project/faapi/3.8.0). This converter is
not perfect however, and it is possible that data may be lost during the conversion process.

It is suggested to keep your main database in HTML mode, and only use BBCode in a copy to be used with
the [`server`](#server) command.

### Init

```
init
```

The `init` command initialises the database. If a database is already present, no operation is performed except for a
version check.

### Login

```
login [--browser/--no-browser] [--domain TEXT] [--name NAME...] BROWSER
```

Login using a browser.

To get the cookies without opening the browser use the `--no-browser` option.

To specify a domain other than furaffinity.net, use the `--domain` option.

The `--name` option can be used to specify which cookies to use by
name. Defaults to 'a' and 'b'.

Cookies can also be added manually using the `config cookies` command.

The following browsers are supported:

* Brave
* Chrome
* Chromium
* Edge
* Firefox
* LibreWolf
* Opera
* OperaGX
* Safari
* Vivaldi

_Note_: depending on the system, the terminal application may require
additional access privileges in order to get the cookies from some browsers. On macOS, the Terminal must be given full
disk access.

> ```
> falocalrepo login Firefox --name a --name b --name cf_clearance
> ```

### Config

```
config <OPERATION>
```

The config command allows reading and changing the settings used by the program.

#### list

```
list
```

Show a list of all stored settings.

#### cookies

```
cookies [--cookie <NAME> <VALUE>...]
```

Read or modify stored cookies. If no `--cookie` option is given, the current values are read instead.

> ```
> falocalrepo config cookies --cookie a 38565475-3421-3f21-7f63-3d341339737 --cookie b 356f5962-5a60-0922-1c11-65003b703038
> ```

#### files-folder

```
files-folder [--move] [<NEW_FOLDER>]
```

Read or modify the folder used to store submission files, where `NEW_FOLDER` is the path to the new folder. If
`NEW_FOLDER` is omitted, the current value is read instead.

If the `--move` option is used, all files will be moved to the new location.

> ```
> falocalrepo config files-folder --move FA.files2
> ```

#### backup

```
backup [--date-format FMT] [--folder DIRECTORY] [--remove] [{download|database|config|predownload|predatabase|preconfig}]
```

Read or modify automatic backup settings. Backup will be performed automatically based on stored triggers and date
formats. The date format `FMT` supports the standard
[C _strftime_ codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes), and it
defaults to `%Y %W` (year and week).

To set the backup folder, use the `--folder` option.

To remove a trigger from the settings, use the `--remove` option.

The trigger can be one of:

* `download`  backup after performing download operations
* `database`  backup after editing the database
* `config`    backup after changing settings
* `predownload`  backup after performing download operations
* `predatabase`  backup after editing the database
* `preconfig`    backup after changing settings

### Download

```
download <OPERATION>
```

The download command performs all download operations to save and update users, submissions, and journals. Submissions
are downloaded together with their files and thumbnails, if there are any. For details on submission files,
see [Submission Files](#submission-files).

All download operations (except login) support the `--dry-run` option. When this is active, the database is not
modified, nor are submission files downloaded. Entries are simply listed and the program checks whether they are in the
database or not.

All download operations pertaining submissions (`users`, `update` and `submissions`) support the `--retry` option to
enable download retries for submission files and thumbnails up to 5 times. The default behaviour is to retry one time.

All download operations support the `--no-comments` option to disable saving comments of submissions and journals.
Comments can be updated on a per-entry basis using the `download submission` and `download journal` commands,
or `download users` to update entire user folders with the `--replace` option enabled.

All download operations support the ` --content-only` option to disable saving headers and footers of submissions and
journals. Headers and footers can be updated on a per-entry basis using the `download submission` and `download journal`
commands, or `download users` to update entire user folders with the `--replace` option enabled.

When downloading, submission and journal titles will be displayed in the terminal. Characters in the titles outside the
ASCII range will be replaced with □ to avoid formatting errors.

#### users

```
users -u <USER>... -f <FOLDER>... [--retry] [--no-comments] [--content-only] [--replace] [--dry-run] [--verbose-report] [--report-file REPORT_FILE]
```

Download specific user folders, where `FOLDER` is one of gallery, scraps, favorites, journals, userpage, watchlist-by,
watchlist-to. Multiple `--user` and `--folder` arguments can be passed. `USER` can be set to `@me` to fetch own
username. `watchlist-by:FOLDER` and `watchlist-to:FOLDER` arguments add the specified `FOLDER`(s) to the new user
entries.

If the `--replace` option is used, existing entries in the database will be updated (favorites are maintained).

The `--verbose-report` options enables printing all the IDs and usernames of the entries fetched/added/modified by the
program. The `--report-file` options allows saving a detailed download report in JSON format to `REPORT_FILE`.

> ```
> falocalrepo download users -u tom -u jerry -f gallery -f scraps -f journals -f userpage
> ```
> ```
> falocalrepo download users -u cat -f watchlist-by:gallery -f watchlist-by:scraps -f watchlist-by:journals 
> ```
> ```
> falocalrepo download users -u tom -u jerry -f favorites --dry-run
> ```

#### update

```
update [-u <USER>...] [-f <FOLDER>...] [--stop N] [--deactivated] [--like] [--retry] [--no-comments] [--content-only] [--dry-run] [--verbose-report] [--report-file REPORT_FILE]
```

Download new entries using the users and folders already in the database. `--user` and `--folder` options can be used to
restrict the update to specific users and or folders, where `FOLDER` is one of gallery, scraps, favorites, journals,
userpage. Multiple `--user` and `--folder` arguments can be passed. `USER` can be set to `@me` to fetch own username.

If the `--deactivated` option is used, deactivated users are fetched instead of ignore. If the user is no longer
inactive, the database entry will be modified as well.

The `--stop` option allows setting how many entries of each folder should be found in the database before stopping the
update.

The `--like` option enables using SQLite LIKE statements for `USER` values, allowing to select multiple users at once.

The `--verbose-report` options enables printing all the IDs and usernames of the entries fetched/added/modified by the
program. The `--report-file` options allows saving a detailed download report in JSON format to `REPORT_FILE`.

_Note_: userpages may be updated even if the text is the same if they contain user icons, as the URLs used in the HTML
tags are temporary

_Note_: watchlists updates check all watches, regardless of the `--stop` value because watchlist pages are sorted by
name, not by watch date

> ```
> falocalrepo download update --stop 5
> ```
> ```
> falocalrepo download update --deactivated -f gallery -f scraps
> ```
> ```
> falocalrepo download update -u tom -u jerry -f favorites --report-file FA.update.json
> ```
> ```
> falocalrepo download update -u a% -u b%
> ```

#### submissions

```
submissions [--replace] [--retry] [--no-comments] [--content-only] [--verbose-report] [--report-file REPORT_FILE] <SUBMISSION_ID>...
```

Download single submissions, where `SUBMISSION_ID` is the ID of the submission. If the `--replace` option is used,
database entries will be overwritten with new data (favorites will be maintained).

The `--verbose-report` options enables printing all the IDs and usernames of the entries fetched/added/modified by the
program. The `--report-file` options allows saving a detailed download report in JSON format to `REPORT_FILE`.

> ```
> falocalrepo download submissions 12345678 13572468 87651234
> ```

#### journals

```
journals [--replace] [--no-comments] [--content-only] [--verbose-report] [--report-file REPORT_FILE] <JOURNAL_ID>...
```

Download single journals, where `JOURNAL_ID` is the ID of the journal. If the `--replace` option is used, database
entries will be overwritten with new data (favorites will be maintained).

The `--verbose-report` options enables printing all the IDs and usernames of the entries fetched/added/modified by the
program. The `--report-file` options allows saving a detailed download report in JSON format to `REPORT_FILE`.

> ```
> falocalrepo download journals 123456 135724 876512
> ```

### Database

```
database <OPERATION>
```

Operate on the database to add, remove, or search entries. For details on columns see [Database](#database-1).

Available operations are:

#### info

```
info
```

Show database information, statistics and version.

#### bbcode

```
bbcode [{true|false}]
```

Read or modify the BBCode setting of the database and convert existing entries when changing it. See [BBCode](#bbcode)
for more details.

Use `true` to enable BBCode and convert entries and `false` to disable BBCode and convert entries back to HTML.

**WARNING**: HTML to BBCode conversion (and vice versa) is still a work in progress, and it may cause some content to be
lost. A backup of the database should be made before changing the setting.

Conversion can be interrupted at any moment with `CTRL+C` and all changes will be rolled back.

#### history

```
history [--filter FILTER] [--filter-date DATE] [--clear]
```

Show database history. History events can be filtered using the `--filter` option to match events that contain
`FILTER` (the match is performed case-insensitively). The `--filter-date` option allows filtering by date. The `DATE`
value must be in the format `YYYY-MM-DD HH:MM:SS`, any component can be omitted for generalised results.

Using the `--clear` option will delete all history entries, or the ones containing `FILTER` if the `--filter` option is
used.

> ```
> falocalrepo database history --filter upgrade 
> ```
> ```
> falocalrepo database history --filter-date 2022-01 --filter download 
> ```

#### search

```
search [--column <COLUMN[,WIDTH]>...] [--limit LIMIT] [--offset OFFSET] [--sort COLUMN] [--order {asc|desc}] [--output {table|csv|tsv|json|none}] [--ignore-width] [--sql] [--show-sql] [--total] {SUBMISSIONS|JOURNALS|USERS} <QUERY>...
```

Search the database using queries, and output in different formats. For details on the query language,
see [Database Query Language](#database-query-language).

The default output format is a table with only the most relevant columns displayed for each entry. To override the
displayed column, or change their width, use the --column option to select which columns will be displayed (SQLite
statements are supported). The optional `WIDTH` value can be added to format that specific column when the output is set
to table.

To output all columns and entries of a table, `COLUMN` and `QUERY` values can be set to `@` and `%` respectively.
However, the `database export` command is better suited for this task.

Search is performed case-insensitively.

The output can be set to five different types:

* `table` Table format
* `csv` CSV format (comma separated)
* `tsv` TSV format (tab separated)
* `json` JSON format
* `none` Do not print results to screen

_Note_: characters outside the ASCII range will be replaced with □ when using table output

> ```
> falocalrepo search USERS --output json '@folders ^gallery'
> ```

> ```
> falocalrepo search SUBMISSIONS '@tags |cat| |mouse| @date 2020- @category artwork' --sort AUTHOR asc --sort DATE desc
> ```

> ```
> falocalrepo search JOURNALS --output csv '@date (2020- | 2019-) @content commission'
> ```

#### view

```
view [--raw-content] [--view-comments] {SUBMISSIONS|JOURNALS|USERS} ID
```

View a single entry in the terminal. Submission descriptions, journal contents, and user profile pages are rendered and
formatted.

Comments are not shown by default; to view them, use the `--view-comments` option.

Formatting is limited to alignment, horizontal lines, quotes, links, color, and emphasis. To view the properly formatted
HTML/BBCode content, use the `server` command. Formatting can be disabled with the `--raw-content` option to print the
raw content.

_Note_: full color support is only enabled for truecolor terminals. If the terminal does not support truecolor, the
closest ANSI color match will be used instead.

> ```
> falocalrepo database view USERS tom
> ```
> ```
> falocalrepo database view SUBMISSIONS 12345678
> ```

#### add

```
add [--submission-file FILENAME] [--submission-thumbnail FILENAME] {SUBMISSIONS|JOURNALS|USERS} <FILE>
```

Add entries and submission files manually using a JSON file. Submission files/thumbnails can be added using the
respective options; all existing files are removed. Multiple submission files can be passed.

The JSON file must contain fields for all columns of the table. For a list of columns for each table,
see [Database](#database-1).

The program will throw an error when trying to add an entry that already exists. To edit entries use
the [`database edit`](#edit) command, or remove the entry with [`database remove`](#remove).

> ```
> falocalrepo database add USERS user.json
> ```

> ```
> falocalrepo database add SUBMISSIONS submission.json --submission-file file1.png --submission-file file2.gif --submission-thumbnail thumbnail.jpg
> ```

#### edit

```
edit [--submission-file FILENAME] [--add-submission-files] [--submission-thumbnail FILENAME] {SUBMISSIONS|JOURNALS|USERS} <ID> [<FILE>]
```

Edit entries and submission files manually using a JSON file. Submission files/thumbnails can be added using the
respective options; existing files are overwritten unless the `--add-submission-files` option is used. Multiple
submission files can be passed.

The JSON fields must match the column names of the selected table. For a list of columns for each table,
see [Database](#database-1).

If the `--submission-file` and/or `--submission-thumbnail` options are used, the `FILE` argument can be omitted.

> ```
> falocalrepo database edit JOURNALS 123456 journal.json
> ```

> ```
> falocalrepo database edit SUBMISSIONS 12345678 --submission-file alt.png --add-submission-files
> ```

#### remove

```
remove [--yes] {SUBMISSIONS|JOURNALS|USERS} ID...
```

Remove entries from the database using their IDs. The program will prompt for a confirmation before commencing deletion.
To confirm deletion ahead, use the `--yes` option.

> ```
> falocalrepo database remove SUBMISSIONS 1 5 14789324
> ```

#### merge

```
merge [--query <TABLE QUERY>...] [--replace] DATABASE_ORIGIN
```

Merge database from `DATABASE_ORIGIN`. Specific tables can be selected with the `--query` option. For details on the
syntax for the `QUERY` value, see [Database Query Language](#database-query-language). To select all entries in a table,
use `%` as query. The `TABLE` value can be one of SUBMISSIONS, JOURNALS, USERS.

If no `--query` option is given, all major tables from the origin database are copied (SUBMISSIONS, JOURNALS, USERS).

Existing submissions are not replaced by default; to replace existing entries with those from `DATABASE_ORIGIN`, use
the `--replace` option.

> ```
> falocalrepo database merge ~/FA.db --query USERS tom --SUBMISSIONS '@author tom'
> ```

#### copy

```
copy [--query <TABLE QUERY>...] [--replace] DATABASE_DEST
```

Copy database to `DATABASE_DEST`. Specific tables can be selected with the `--query` option. For details on the syntax
for the `QUERY` value, see [Database Query Language](#database-query-language). To select all entries in a table,
use `%` as query. The `TABLE` value can be one of SUBMISSIONS, JOURNALS, USERS.

If no `--query` option is given, all major tables from the origin database are copied (SUBMISSIONS, JOURNALS, USERS).

Existing submissions are not replaced by default; to replace existing entries in `DATABASE_DEST`, use the `--replace`
option.

> ```
> falocalrepo database copy ~/FA.db --query USERS tom --SUBMISSIONS '@author tom'
> ```

#### doctor

```
doctor [--users] [--submissions] [--comments] [--fix] [--allow-deletion]
```

Check the database for errors and attempt to repair them.

Users are checked for inconsistencies in their name to make sure that they can be properly matched with their
submissions, journals, and comments.

Submissions are checked with their thumbnails and files to ensure they are consistent, and the program will attempt to
add files that are in the submission folder but are not saved in the database

Comments are checked against their parents, if the parent object does not exist then the comment is deleted if
the `--allow-deletion` option is used.

To check only specific tables, use the `--users`, `--submissions`, and `--comments` options.

By default, errors are only logged and no attempt will be made to fix them. To allow the program to try to repair
the database, use the `--fix` option.

Use the `--allow-deletion` option to allow deleting entries that are redundant or erroneous (e.g. a comment without
parent object).

#### clean

```
clean
```

Clean the database using the SQLite [VACUUM](https://www.sqlite.org/lang_vacuum.html) function.

#### upgrade

```
upgrade
```

Upgrade the database to the latest version.

#### Database Query Language

The query language used for search queries is based and improves upon the search syntax currently used by the Fur
Affinity website. Its basic elements are:

* `@<field>` field specifier (e.g. `@title`), all database columns are available as search fields.
* `()` parentheses, they can be used for better logic operations
* `&` _AND_ logic operator, used between search terms
* `|` _OR_ logic operator, used between search terms
* `!` _NOT_ logic operator, used as prefix of search terms
* `""` quotes, allow searching for literal strings without needing to escape
* `%` match 0 or more characters
* `_` match exactly 1 character
* `^` start of field, when used at the start of a search term it matches the beginning of the field
* `$` end of field, when used at the end of a search term it matches the end of the field

All other strings are considered search terms.

The search uses the `@any` field by default for submissions and journals, allowing to do general searches without
specifying a field. The `@any` field does not include the `FAVORITE`, `FILESAVED`, `USERUPDATE`, and `ACTIVE` fields and
must be searched manually using the respective query fields. When searching users, `@username` is the default field.

Search terms that are not separated by a logic operator are considered _AND_ terms (i.e. `a b c` -> `a & b & c`).

Except for the `ID`, `FILESAVED`, `USERUPDATE`, and `ACTIVE` fields, all search terms are searched through the
whole content of the various fields: i.e. `@description cat` will match any item whose description field contains "cat".
To match items that contain only "cat" (or start with, end with, etc.), the `%`, `_`, `^`, and `$` operators need to be
used (e.g. `@description ^cat`).

Search terms for `ID`, `FILESAVED`, `USERUPDATE`, and `ACTIVE` are matched exactly as they are: i.e. `@id 1` will match
only items whose ID field is exactly equal to "1", to match items that contain "1" the `%`, `_`, `^`, or `$` operators
need to be used (e.g. `@id %1%`).

### Server

```
server [--host HOST] [--port PORT] [--ssl-cert FILE] [--ssl-key FILE] [--auth USERNAME PASSWORD...] [--auth-ignore IP...] [--editor USERNAME...] [--max-results INTEGER] [--no-cache] [--no-browser]
```

Start a server at `HOST`:`PORT` to navigate the database. The `--ssl-cert` and `--ssl-cert` allow serving with HTTPS.

When the app has finished loading, it automatically opens a browser window. To avoid this, use the `--no-browser`
option.

The server caches results by default. To avoid caching, use the `--no-cache` option.

To reduce the number of results in search pages, and thus increase the speed of the system, the `--max-results` option
can be used. The default value is 2400. If set to 0, then the queries will not be limited.

Using the `--auth` option, multiple users can be added, each with their own password. Specific users can be given
editing rights using the `--editor` option. If no authorization is given, then anyone accessing the server can edit.

The `--auth-ignore` option allows skipping authentication for specific IP addresses. The option supports patterns such
as "192.168.0.*".

For more details on usage see [falocalrepo-server](https://pypi.org/project/falocalrepo_server/).

### Completions

```
completions [--alias NAME] {bash|fish|zsh}
````

Generate tab-completion scripts for your shell. The generated completion must be saved in the correct location for it to
be recognized and used by the shell.

The optional `--alias` option allows generating completion script with a name other than `falocalrepo`.

Supported shells are:

* `bash` The Bourne Again SHell
* `fish` The friendly interactive shell
* `zsh` The Z shell

### Updates

```
updates [--shell]
```

Check for updates to falocalrepo and its main dependencies on PyPi. The `--shell` option can be used to output
the shell command to upgrade any component that has available updates.

_Note_: The command needs an internet connection.

### Help

```
help [<COMMAND>...]
```

The `help` command gives information on the usage of the program and its commands.

> ```
> falocalrepo help database search
> ```

### Paw

```
paw [--truecolor | --8bit-color] [FLAG]
```

Print a PRIDE paw!

<img src="https://raw.githubusercontent.com/FurryCoders/Logos/main/logos/paw-pride.svg" height="300" alt="">

Built-in colors are available for the following flags: pride (default), trans, bisexual, pansexual, non-binary, lesbian,
agender, asexual, genderqueer, genderfluid, aromantic, polyamory. Further, the palestinian and ukrainian flags are also
available.

If used inside a truecolor-supporting terminal, the full 24bit color range can be used for the most colorful flags!

truecolor and 8bit color modes can be set using the `--truecolor` and `--8bit-color` options respectively.

_Note_: the paw works best with a dark background.

If you have suggestions on new flags to add (or color improvements for the existing ones), don't hesitate to open
a [feature request](https://github.com/FurryCoders/FALocalRepo/issues/new?labels=enhancement&template=FEATURE-REQUEST.yml&title=%5BFeature+Request%5D%3A+)!

## Database

To store the metadata of the downloaded submissions, journals, users, cookies and statistics, the program uses a SQLite3
database. This database is built to be as light as possible while also containing all the metadata that can be extracted
from a submission page.

To store all this information, the database uses four tables: `SETTINGS`, `USERS`, `SUBMISSIONS` and `JOURNALS`.

> **How Lists Are Stored**<br>
> Some fields in the database table contain lists of items. These are stored as strings, with each item surrounded by
> bars (`|`). This allows to properly separate and search individual items regardless of their position in the list.<br>
> `|item1||item2|`<br>

### Users

The users' table contains a list of all the users that have been downloaded with the program, the folders that have been
downloaded, and the submissions found in each of those.

Each entry contains the following fields:

* `USERNAME` The URL username of the user (no underscores or spaces)
* `FOLDERS` the folders downloaded for that specific user, sorted and bar-separated
* `ACTIVE` `1` if the user is active, `0` if not
* `USERPAGE` the user's profile text

### Submissions

The submissions' table contains the metadata of the submissions downloaded by the program and information on their files

* `ID` the id of the submission
* `AUTHOR` the username of the author (uploader) in full format
* `TITLE`
* `DATE` upload date in ISO format _YYYY-MM-DDTHH:MM_
* `DESCRIPTION` description in HTML/BBCode format
* `FOOTER` footer in HTML/BBCode format
* `TAGS` bar-separated tags
* `CATEGORY`
* `SPECIES`
* `GENDER`
* `RATING`
* `TYPE` image, text, music, or flash
* `FILEURL` a bar-separated list of the remote URLs for the submission files
* `FILEEXT` a bar-separated list of extensions of the downloaded files. Can be empty if the file contained errors and
  could not be recognised upon download
* `FILESAVED` file and thumbnail download status as a 3bit flag:`xx1` if thumbnail was downloaded, `xx0` if not; `x1x`
  if at least one file was valid `x0x` if not; `1xx` if all given files where valid, `0xx` if not. Possible values
  are `0` through `7` (3 bit).
* `FAVORITE` a bar-separated list of users that have "faved" the submission
* `MENTIONS` a bar-separated list of users that are mentioned in the submission description as links
* `FOLDER` the folder of the submission (`gallery` or `scraps`)
* `USERUPDATE` whether the submission was added as a user update or favorite/single entry

### Journals

The journals' table contains the metadata of the journals downloaded by the program.

* `ID` the id of the journal
* `AUTHOR` the username of the author (uploader) in full format
* `TITLE`
* `DATE` upload date in ISO format _YYYY-MM-DDTHH:MM_
* `CONTENT` content in HTML/BBCode format
* `HEADER` header in HTML/BBCode format
* `FOOTER` footer in HTML/BBCode format
* `MENTIONS` a bar-separated list of users that are mentioned in the journal content as links
* `USERUPDATE` whether the journal was added as a user update or single entry

### Comments

The comments' table contains the metadata of the journals and submissions stored in the database.

* `ID` the id of the comment
* `PARENT_TABLE` `SUBMISSIONS` if the comment relates to a submission, `JOURNAL` if the comment relates to a journal
* `PARENT_ID` the id of the parent object (submission or journal)
* `REPLY_TO` the id of the parent comment, if the comment is a reply
* `AUTHOR` the username of the author in full format
* `DATE` post date in ISO format _YYYY-MM-DDTHH:MM:SS_
* `TEXT` the text of the comment in HTML/BBCode format

### Settings

The settings table contains settings for the program and variable used by the database handler and main program.

* `COOKIES` cookies for the scraper, stored in JSON format
* `FILESFOLDER` location of downloaded submission files
* `VERSION` database version, this can differ from the program version
* `SERVER.SEARCH` search settings if saved using the web server (see [server](#server))
* `BACKUPFOLDER` folder for automatic backups
* `BACKUPSETTINGS` settings for automatic backups
* `BBCODE` settings for BBCode mode

### History

The history table holds events related to the database.

* `TIME` event time in ISO format _YYYY-MM-DDTHH:MM:SS.ssssss_
* `EVENT` the event description

## Submission Files

Submission files are saved in a tiered tree structure based on their submission ID. IDs are zero-padded to 10 digits and
then broken up in 5 segments of 2 digits; each of these segments represents a folder tha will be created in the tree.

For example, a submission `1457893` will be padded to `0001457893` and divided into `00`, `01`, `45`, `78`, `93`. The
submission file will then be saved as `00/01/45/78/93/submission.file` with the correct extension extracted from the
file itself - FurAffinity links do not always contain the right extension.

Extra submission files are saved in the same folder with a 0-based index appended to the filename. The first file is
named `submission.file`, and subsequent files are called `submission1.file`, `submission2.file`, etc.

## Upgrading Database

When the program starts, it checks the version of the database against the one used by the program and if the latter is
more advanced it stops execution and prompts the user to upgrade using the [`database upgrade`](#upgrade) command.

_Note:_ versions prior to 4.19.0 are not supported by falocalrepo version 4.0.0 and above. To update from
those, use [falocalrepo version 3.25.0](https://pypi.org/project/falocalrepo/v3.25.0) to upgrade the database to version
4.19.0 first.

_Note:_ Versions before 2.7.0 are not supported by falocalrepo version 3.0.0 and above. To update from those to the new
version use version 2.11.2 to update the database to version 2.7.0

For details on upgrades and changes between database versions,
see [falocalrepo-database](https://pypi.org/project/falocalrepo-database/).

## Contributing

All contributions and suggestions are welcome!

If you have suggestions for fixes or improvements, you can open an issue with your idea, see [Issues](#issues) for
details.

## Issues

If you encounter any problem while using the program, an issue can be opened on the project's page
on [GitHub](https://github.com/FurryCoders/FALocalRepo/issues).

Issues can also be used to suggest improvements and features.

When opening an issue for a problem, please copy the error message and describe the operation in progress when the error
occurred.

## Appendix

### Earlier Releases

Release 3.0.0 was deleted from PyPi because of an error in the package information. However, it can still be found on
GitHub [v3.0.0](https://github.com/FurryCoders/FALocalRepo/releases/tag/v3.0.0).

Release binaries for versions 2.11.2 can be found on GitHub
at [v2.11.2](https://github.com/FurryCoders/FALocalRepo/releases/tag/v2.11.2)
