# Changelog

## 3.16.4

### Fixes

* Fix early stop when update found a submission that changed folder

## 3.16.3

### Fixes

* Fix error when sorting users during update
* Fix disabled users being printed even when not selected for updated

## 3.16.2

### Fixes

* Fix update not working if no users are passed
* Fix update not finding favorites in the database
* Fix missing version 3.16.1 in the changelog

## 3.16.1

### Fixes

* Fix missing information in README

## 3.16.0

### Changes

* `config cookies` command now takes parameters to allow for any number and name of cookies
* falocalrepo-database dependency set to \~4.7.0
  * Support new `MENTIONS` and `USERUPDATE` columns for journals and submission entries
* faapi dependency set to \~2.15.0
  * Remove calls to check user existence/status and instead rely on faapi exceptions
  
### Fixes

* Fix submission tags not being sorted when adding a submission manually with `database add-submission` 

## 3.15.7

### Changes

* Add support for `FALOCALREPO_DEBUG` environmental variable

### Fixes

* Fix help message not displaying when no commands were passed

## 3.15.6

### Changes

* falocalrepo-database dependency set to \~4.4.0
    * Support new `FAVORITE` column for submission entries

## 3.15.5

### Changes

* falocalrepo-server dependency set to \~1.8.0

## 3.15.4

### Fixes

* The multiple instance check will not be triggered by modules that contain `falocalrepo` in their name (e.g. `falocalrepo-server`)

## 3.15.3

### Changes

* FAAPI (from [faapi](https://pypi.org/project/faapi)) is not loaded until needed. Commands structure is checked before connection is attempted
* Cookies are listed as-are to allow checking for errors (e.g. incorrect `name` field)

## 3.15.2

### Changes

* faapi dependency set to \~2.12.0

## 3.15.1

### Changes

* falocalrepo-server dependency set to \~1.7.0

## 3.15.0

### Changes

* Add `database add-user` command to manually add a user to the database

## 3.14.1

### Fixes

* Fix an error when users search found 0 results

## 3.14.0

### Changes

* Add `-u`/`--updates` option to check for updates on PyPi instead of checking when program starts

### Fixes

* Fix incorrect UnknownCommand exceptions

## 3.13.17

### Fixes

* Fix error in help function

## 3.13.16

### Fixes

* Fix _ not working when searching AUTHOR and USERNAME fields

## 3.13.15

### Fixes

* Fix error with instance checking causing the program to fail at start

## 3.13.14

### Changes

* Check for other running instances of `falocalrepo` and raise exception if any is found

### Fixes

* Fix a line-wrapping error in the main help message

## 3.13.13

### Changes

* Improved usage patterns, instructions, and general language in both help messages and readme
* falocalrepo-database dependency set to \~4.3.0
    * Removed counters from `SETTINGS` table

## 3.13.12

### Changes

* Separate all commands and subcommands into separate functions
* Add help for subcommands with descriptions and examples
* Improved efficiency of search and results printing

### Fixes

* Fix % not working when searching AUTHOR and USERNAME fields
* Fix USERNAME field not being cleaned when performing users search
* Fix an error when users search found 0 results

## 3.13.11

### Changes

* Check for faapi updates

## 3.13.10

### Changes

* faapi dependency set to \~2.11.0
* Changed order of `database info` output

## 3.13.9

### Changes

* Exit with code 130 on KeyboardInterrupt (Ctrl-C)

### Fixes

* Fix users not being skipped during update if no folder matches manual folders argument

## 3.13.8

### Changes

* More precise database info command output

### Fixes

* Fix missing import causing error when importing the module

## 3.13.7

### Changes

* falocalrepo-server dependency set to \~1.6.0
* Improve readme

### Fixes

* Fix usage pattern of main help

## 3.13.6

### Fixes

* Fix submissions with _ in the author name not being found with url formatted name

## 3.13.5

### Changes

* Improve exception-catching of database errors

### Fixes

* Fix database transaction being left open and locking `VACUUM` operation 

## 3.13.4

### Fixes

* Fix search filtering out column parameters
* Fix search not using `like`

## 3.13.3

### Fixes

* Fix search failing without limit and offset parameters

## 3.13.2

### Fixes

* Fix missing database upgrade

## 3.13.1

### Fixes

* Fix broken import causing the program to crash on start

## 3.13.0

With this new release comes the all-new [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) version 4. Some column names in the database have been changed and the insertion functions have been made safer with built-in checks. Search is now much more versatile and allows to query any columns in the users, submissions, and journals tables. Thanks to the new checks, the `database check-errors` command was removed, as the new checks remove the possibility of inserting erroneous data. The update function will notify of any faulty entry during the automatic update of the database.

### Changes

* falocalrepo-database dependency set to \~4.2.0
* falocalrepo-server dependency set to \~1.5.0
* Improve data-entry safety
* Remove `database check-errors` command
* Allow to use all table columns for submissions and journals search

## 3.12.1

### Changes

* Print `FALOCALREPO_DATABASE` environmental variable if used

### Fixes

* Fix missing messages for assertion errors

## 3.12.0

This new minor bump adds a new `list-<folder>` option to the download users command. Using it allows to list all remote items present in a user folder without downloading them. Environmental variables are now supported starting with `FALOCALREPO_DATABASE` which allows to set a different path for the database and files folder root.

### Changes

* Add `list-<folder>` folders to download users command
* Add `FALOCALREPO_DATABASE` environmental variable
* falocalrepo-server dependency set to \~1.4.0
* Remove subcommands arguments details from general help messages  

### Fixes

* Fix padding inconsistencies in users search results
* Fix missing newline when server closes

## 3.11.0

This new minor version bump updates the [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) dependency to its latest version and adds a new `database merge` command. This new command allows to merge the database located in the current folder with a second database located in another folder.

### Changes

* falocalrepo-database dependency set to \~3.8.0
* Add `database merge` command

## 3.10.11

### Changes

* faapi dependency set to 2.10.2

### Fixes

* Fix an error occurring when date format was set to "full" [faapi#1](https://gitlab.com/MatteoCampinoti94/FAAPI/-/issues/1)

## 3.10.10

### Changes

* removed unused filetype dependency

## 3.10.9

### Changes

* falocalrepo-database dependency set to \~3.7.1
* falocalrepo-server dependency set to \~1.3.4
* Improved `search-users` command

### Fixes

* fix id parameter error when manually adding submissions/journals

## 3.10.8

### Changes

* Add output while waiting for faapi to connect

### Fixes

* Fix output error when submission is found in user entry

## 3.10.7

### Changes

* Do not display last found match in download update
* Sort update folders when none is provided

### Fixes

* Fix some errors in README

## 3.10.6

### Changes

* Display length of commands history instead of last command
* Improved progress background functions

### Fixes

* Fix submissions not being removed from users' entries with `database remove-submissions` command

## 3.10.5

### Changes

* faapi dependency set to 2.10.1
* Default database search order to ID/USERNAME
* Add some information on `order` parameter for database searches in readme

### Fixes

* Fix download error caused by faapi version 2.10.0

## 3.10.4

### Changes

* faapi dependency set to 2.10.0
* Better detection of deactivated users with updated faapi methods

## 3.10.3

### Changes

* faapi dependency set to 2.9.1

## 3.10.2

### Fixes

* Fix error error with users journals download

## 3.10.1

### Changes

* faapi dependency set to 2.9.0

## 3.10.0

Added a new `database search-users` command to search the users table using all the collected metadata. The readme has been improved slightly with better explanations. A small error in the database command help message was fixed.

### Changes

* Add `database search-users` command
* Add help for `help` and `init` commands
* Improve explanation of SQLite `like` expression

### Fixes

* Fix error in database command help

## 3.9.2

### Changes

* Small optimisation to database init and update process

### Fixes

* Fixed erroneous general help message

## 3.9.1

### Fixes

* Fix bug occurring when saving submissions/journals into the database

## 3.9.0 - 100th Release!

Both the database and server modules have been update to versions 3.5.0 and 1.3.1 respectively. The database now holds a history of all commands (except for version printing and help) instead of just last start and last update, and A new `database history` command was added to print the commands history.

When a non-help command is used, the program now checks for updates to its components and prints them to screen.

More exceptions are caught now and exit with a specific code; unforeseen exceptions are also caught and their trace saved to FA.log.

### Changes

* falocalrepo-database dependency set to \~3.5.0
* falocalrepo-server dependency set to \~1.3.1
* Added `database history` command
* Catch ConnectionError and sqlite3.DatabaseError
* Catch general Exception and BaseException and print trace to FA.log

### Fixes

* Fix error with manual submissions and journals

## 3.8.2

### Changes

* Added `-s`, `--server` option to print version of falocalrepo-server used by the program

### Fixes

* Fix missing instructions for download help

## 3.8.1

### Fixes

* Removed some lines of code used for debugging version 3.8.0 (now yanked)

## 3.8.0

From this release all database functions are handled separately by the new [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) package. The package is also used in [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) allowing the falocalrepo console to be updated more easily.

### Changes

* removed database functions in favor of [falocalrepo-database](https://pypi.org/project/falocalrepo-database/)
* falocalrepo-database dependency set to ~3.2.4
* falocalrepo-server dependency set to ~1.2.2

### Fixes

* Fixed an error in the description of tables in the readme

## 3.7.5

The `download journals` command is now fixed and calling the correct function. Two sub-commands aliases have been added: `config list` and `database info` which act as `config` and `database` respectively when called without arguments. Database size in MB (base 10) and last start have been added to `database info` output, missing journals counter in database info has also been added. falocalrepo-server dependency updated to ^1.1.3.

### Changes

* `database info` command to display database information
* `config list` command to list settings stored in database
* Database size and last start added to database info output
* falocalrepo-server dependency updated to ^1.1.3

### Fixes

* Fixed `download journals`
* Added missing journals counter in database info output

## 3.7.4

### Changes

* Update faapi dependency to 2.8.3

## 3.7.3

Background changes and fixes. The `main_console` function was renamed to `console` and is now the only direct export of the package, falocalrepo-server dependency has been updated to ^1.1.2, help messages have been slightly reformatted, and command does not dwfault to `init` when absent.

### Changes

* Update falocalrepo-server dependency to ^1.1.2
* Update help messages with falocalrepo, database and falocalrepo-server versions
* `main_console` renamed to `console`
* Parameters (e.g. `database search-submissions` search fields) are taken as are and not lowered
* LASTART value is not set when using `init`
* Calling without a command shows help, doesn't default to `init`

### Fixes

* Fix indentation of help messages

## 3.7.2

falocalrepo-server dependency has been updated to use the latest above 1.1.1. Command defaults to init if no command is passed.

### Changes

* Update falocalrepo-server dependency to ^1.1.1
* Default to init command if no command is passed

## 3.7.1

### Changes

* Update falocalrepo-server dependency to 1.1.1

## 3.7.0

The server interface has been moved to its own separate package [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) for ease of development, and it is now a dependency of falocalrepo.

A few small bugs have also been fixed.

### Changes

* Transfer falocalrepo-server to its own package
* Make falocalrepo-server a dependency

### Fixes

* Fix incorrect exception in download journals command
* Fix erroneous FurAffinity theme name in readme
* Fix missing entry in table of contents

## 3.6.2

### Changes

* Removed `/user/<username>` server shortcut in favor of `/submissions/<username>/` and `/journals/<username>/`

### Fixes

* Fix missing information in readme

## 3.6.1

### Changes

* New order parameter for server search
* Reorder server search results by clicking on results headers

### Fixes

* Fix wildcards being removed from author parameter when searching
* Fix uppercase parameters not matching

## 3.6.0

A new `database server` command has been added, which starts a Flask server that allows to search the local database and visualise submissions and journals in a friendly GUI.

The web interface allows to search the database using the same options and methods as the `database search-submissions` and `database search-journals` commands.

Command line search commands now support `order`, `limit` and `offset` parameters for finer control of database searches. For a more in-depth explanation refer to the [SQLite SELECT documentation](https://sqlite.org/lang_select.html).

A few bugs have also been resolved, error messages have been improved, and more information has been added to the readme regarding search wildcards.

### Changes

* New server interface to search database
* `order`, `limit` and `offset` parameters for database search commands
* More detailed exceptions for command errors
* More information regarding wildcards in readme

### Fixes

* Fix incorrect error message when passing an unknown database command
* Fix error caused by the options arguments parser

## 3.5.4

A new stop option has been added to the download update command to modify the number of submisisons after which the program stops looking through a user's folder. The database update from 2.7 to 3 has been upgraded and now files are found directly in the submission folder.

### Changes

* Add stop option to download update
* Improved file-finding for database update from 2.7 to 3

## 3.5.3

### Fixes

* Fix a SQLite Cursor error

## 3.5.2

### Changes

* Error checking now includes the Journals table
* FAAPI has been updated to version 2.8.1
  * Check connection status before running download commands

### Fixes

* Fix missing exception when database receives an unknown subcommand

## 3.5.1

### Fixes

* Fix an import error

## 3.5.0

The new `database search-journals` command allows to search journals by author, title, date and content. The old submissions search command is now called `search-submissions`.

The help message and readme have been fixed and missing information has been added.

The output of the `download users` command has been generalised so it does not use "submissions" even when downloading journals; uses "items" instead.

### Changes

* Add database command to search journals

### Fixes

* Fix missing information in help message and readme
* Fix output of download users command not being generalised

## 3.4.0

The program now uses [FAAPI](https://gitlab.com/MatteoCampinoti94/FAAPI) version 2.7.3, which supports downloading users journals. The database has been updated to version 3.2.0 to support this change with a new `JOURNALS` table and a `JOURNALS` field in the `USERS` table. Journals can be download with the `download users` command as any other folder (gallery, scraps, etc...) or with the `download journals` command by supplying journal ID's. Journals can also be added manually using the `database add-journal` command. A corresponding `database remove-journals` has also been added.

The previous `database manual-entry` command has been changed to `database add-submission`.

A few errors in the readme have also been solved.

### Changes

* Database version 3.2.0
  * Add `JOURNALS` table
  * Add `JOURNALS` field in the `USERS` table
* Download users' journals

### Fixes

* Fix readme errors

## 3.3.5

### Fixes

* Fixes porting of disabled folders when updating database from 2.7 to 3.0
* Fixes version when updating database from 3.0 to 3.1
* Disabled folders do not trigger an error when using download update

## 3.3.4

### Fixes

* Fix users folders not being properly ported when updating database from 2.7 to 3.0

## 3.3.3

### Fixes

* Fix file download bar spacing
* Fix settings not porting over when updating database from 3.0.0 to 3.1.0

## 3.3.2

### Fixes

* Fix spacing when download page goes over 100

## 3.3.1

### Fixes

* Fix readme not including new information about database version 3.1.0

## 3.3.0

Database version has been updated to 3.1.0; the "extras" folder has been renamed "mentions". Order of submissions ID's is maintained when downloading single submissions.

### Fixes

* Maintain order of submission ID's when downloading single submissions

### Changes

* Database updated to 3.1.0
  * Extras renamed to mentions

## 3.2.5

### Fixes

* Fix output bug when downloading single submissions

## 3.2.4

Fixes a but that caused tiered paths to overlap if the submission ID ended with zeroes.

### Fixes

* Tiered path for submssions ID's ended with zeroes

## 3.2.3

Order of users and folders passed to download users/update is maintained. Submissions already in the database but not in user entry are not downloaded again.

### Fixes

* Maintain order of users and folders passed to download
* Do not redownload submissions if already present in submissions table

## 3.2.2

Submissions titles are now cleaned of non-ASCII characters before printing them to screen. Non-ASCII characters would break the spacing of the download output.

### Fixes

* Fix output of submissions titles with non-ASCII characters breaking spacing

## 3.2.1

Fix old database having the wrong version in the name when backing it after updating from verison 2.7.0.

### Fixes

* Fix database backup name up when updating from 2.7.0

## 3.2.0

Download update now allows to pass a list of users and/or folders to restrict the update to those.

### Changes

* Pass users and/or folders to download update

## 3.1.9

Database search now allows to use either display or URL author usernames; i.e. `Pippo_Pluto` is equal to `pippopluto`.

### Changes

* Accept both display and URL author usernames in database search

## 3.1.8

Exceptions raised during database updates are caught and any pending changes are committed before the exception is raised again.

### Changes

* Safely commit and close when catching exceptions during database updates

## 3.1.7

The memory usage of database select (i.e. read) operations has been reduced by using [sqlite3 cursors](https://docs.python.org/3/library/sqlite3.html#cursor-objects) instead of lists. The speed of the database update function has been greatly improved by reducing database commits to one every 10000 processed entries (1000 for the users table).

### Changes

* Database select operations return sqlite3 cursors to reduce memory usage
* Database update speed increased by reducing the number of commits

## 3.1.6

Fixes an output error in the database update function and improves the way settings and statistics are written in the database, using UPDATE instead of INSERT OR REPLACE

### Fixes

* Database update output error
* Settings are updated instead of inserted

## 3.1.5

Improve database update function by saving the ID's of the submissions files that weren't found during the transfer.

### Changes

* Save ID's of submisions not found during database update

## 3.1.4

Updated requirement [FAAPI](https://gitlab.com/MatteoCampinoti94/FAAPI) to version 2.6.0.

### Changes

* Use FAAPI 2.6.0

## 3.1.3

If the now unsupported "extras" folder is encountered during update, it now prints a warning and skips to the next.

### Changes

* Explicitely warn about extras folders

## 3.1.2

Fixed an IOError that happened when trying to pipe the database search output to a file.

### Fixes

* IOError when piping search results

## 3.1.1

Fix a version error. Database version was set to 3.1.0 instead of the program version.

### Fixes

* Fix versions

## 3.1.0

The database search command now allows to pass a parameter multiple times to act as OR values for the same field. The readme has been slightly improved and some errors in it have been fixed.

### Fixes

* Readme typos and errors

### Changes

* Database search accepts OR parameters

## 3.0.3

This releases fixes counters not being updated in the new database when updating from version 2.7.

Under the hood changes include exporting the main console function so that the package can be imported and called with arguments from other Python scripts.

Readme has also been improved with more informations about issues and contributing.

### Fixes

* Database update function updates counters of new database

## 3.0.2

Small patch to fix a search bug and output the number of results found with search.

### Fixes

* Fix search crash when using description parameter

### Changes

* Output total number of results found by search

## 3.0.1

This release is only a minor fix to change the PyPi classifier for development status of the program from beta to stable.

## 3.0.0

## 3.0.0 - All New and Improved

Release 3.0.0 marks a complete change in how the program is run, its capabilities and future developement.

Following the change of interface in January 2020, version 2 stopped working, but with this new release the tool can once again get content from FurAffinity and is much simpler to update to support future changes to FA's web interface.

This change was achieved thanks to the FAAPI package (from the same author of FALocalRepo [FAAPI@PyPi.org](https://pypi.org/project/faapi)). All scraping functions are now independent of the interface, allowing for much quicker

The interface of the program was changed from an interactive menu to a command line tool. This allows for much quicker execution of commands, simpler code and automation via shell scripts.

The database has been updated and is now over 50% lighter for large numbers of downloaded submissions. Furthermore, it now holds the cookies used by the scraper, reducing the program footprint.

All database functions have been completely overhauled and are now _considerably_ faster, especially searching. Using a 500k submissions table and a modern SSD drive, searching for a specific tag takes 0,90s on average, and searching for a string in the descriptions takes only 1,30s. Time may vary depending on search parameters and drive speed.

The last big change is in regards to the packaging and distribution of the program. falocalrepo is now a PyPi package, easily installed with a single pip command. All dependencies have also been packaged and distributed on PyPi and are handled without the need for git submodules. The new distribution method allows to run falocalrepo in any folder, without the need to have the program itself stored with the database.

### Changes

* Use FAAPI package to separate scraper developement from interface
* Support for new FA's interface
* Menu interface replaced with a command line tool
* Database cleanup
* Cookies stored in database
* Database queries improvements
* Command line help
* Distribution via PyPi

### Distribution

* [falocalrepo on PyPi.org](https://pypi.org/project/falocalrepo/)

## 2.10.2

Reduced the number of indexes created and made the whole process safer. Also, interruption is now available during indexing.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.10.1

Extras' `e` option has been changed to search for ':iconusername:' and ':usernameicon:' only in the descriptions as searching in keywords too caused too many false positives in case the username was a common word/phrase.

Extras' `E` options has been changed to search 'username' in submissions' titles too.

A new 'warning' log type has been added for errors and exceptions. These will be saved in the log file regardless of other settings.
The log also has a new column for the type of log event: 'N', 'V', or 'W'

A small output error was also fixed.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.10

Thanks to a special Python module created by yours truly, Windows users can now enjoy the program with safe interruption support. The module can be found on GitHub &rarr; [SignalBlock](https://github.com/MatteoCampinoti94/PythonSignalBlocking-CrossPlatform).<br>
More information on the feature can be found in the README.

A new function has been added to the program to correctly detect version differences as the old method was causing errors with some versions.

New log events have been added for SIGINT (CTRL-C interruption) detection and database version.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.9

Added logging to the program if launched with '--log' or '--logv' as argument (the latter logs ALL operations, thus the v of verbose). Log is saved in a file named 'FA.log' and is trimmed to the last 10000 lines at each program start.

A new  'slow' option has been added to the download/update sections to throttle speed even further down by adding a delay of 1,5 seconds between submissions downloads.

A critical bug in the update function has been fixed.

Argument '--debug' was changed to '--raise' to be clearer.

Search results are now properly sorted by author, id.

Some functions have been improved removing bits of unused code.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.8.1

Just a small fix for an incorrect check in the analysis of submissions values.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.8

A new entry has been added to the repair menu to analyze all the tables without attempting repair.

Download and update have a new 'dbonly' option that allows to add the entries to the database without saving any file.

Unforeseen errors are now caught and displayed without being too verbose. To display errors normally the program can be run with the option '--debug'.

An important bug has been fixed in the repair section. A missing return was breaking the INFOS table rapair.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7.4

Fixed an error in the URL used to search extras. An OR was missing and would stop some results from showing up.

Users selected for download/update are now properly sorted.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7.3

The search URL has been modified to avoid false positives by specifically searching only the description and keywords. The default search employed by FA looks for search terms inside submissions filenames as well and it could cause false positives.

Unforeseen errors are now caught by the main script and their information displayed before exiting the program.

The header describing the various columns during download/update now reflects the new status output introduced with [v2.7](https://github.com/MatteoCampinoti94/FALocalRepo/releases/tag/v2.7) and fixed in [v2.7.1](https://github.com/MatteoCampinoti94/FALocalRepo/releases/tag/v2.7.1).

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7.2

Fixed bugs with the new submission download status on Windows by moving it to the left of the title.

Version saved inside program is now correct at 2.7.2 (was still saved as 2.7)

The code handling the upgrade and creation of the database at startup has been slightly improved and should run faster.

New output has been added for when the database is created the first time.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7.1

Just a fix for an output error in the v2.6 to v2.7 upgrade function.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7

New outputs have been added at the start of the program to show what it is doing instead of showing an empty screen.

Download and update status output has been overhauled. The current operation is now showed in a small bracketed area at the right end of the terminal screen. A progress bar is also shown when the submission file is downloaded (not all files support this).

A new INDEX entry has been added to the INFOS table, it is used to save the update status of the indexes used in the search function. Its values are either '0' if they are not up to date or '1' if they are.

Together with the new INDEX entry a new 'noindex' option has been added to the download/update section. If passed then the program will not rebuild indexes after the download/update operation is completed and will set the INDEX entry to '0' if new submissions where downloaded.

A few things have been improved around the program and some bugs removed.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.6

Submissions descriptions are now saved in the database together with the submissions data.

Search has been updated to work with the new description field so it is now possible to search descriptions both offline in the database and online with the web search.<br>
Case sensitivity can now be turned on/off with 'case' option in both normal and regex mode (but not online).<br>
Indexes have been added to quicken the search.

User entries have been slightly altered too: `NAME` column was changed to `USER` and `NAMEFULL` to `USERFULL`.

Repair has been improved with a new menu and a section dedicated to the `INFOS` table as well as shortcuts to optimize the database or re-index it.

Upgrade functions have also been improved with lower memory usage.

Bugs have been fixed throughout the whole program.

PS: Linux binary size issue seems to be fixed for now.

Update 2018/05/02: Linux binary was compiled with an error, it is fixed now

**Warning**: Binaries are for 64bit systems only

## 2.5

The program is now capable of running searches on the main website. If there no results can be found in the local database the user will be automatically asked if they want to perform the search online instead.

A new 'options' field in the search menu allows to enable regex syntax and to search the website directly.

Local search can now match multiple users. For example if there are users 'tiger' and 'liger' in the database using 'iger' in the user field will match both of them.

Search output has also been improved.

A few more bugs have been squashed and some functions redesigned.

PS: I have no idea why but this release for Linux is over twice the size of previus ones. Will work on fixing it.

**Warning**: Binaries are for 64bit systems only

## 2.4

The search has been completely rewritten and should now be a lot faster. It is also now possible to search inside specific sections of a user.<br>
Regex support has been disabled for now as it was hard to use and slowed the search down for everyone. A future update will add an option to use regex.

A few small bugs have been fixed.

PS: I have no idea why but this release for Linux is over twice the size of previus ones. Will work on fixing it.

**Warning**: Binaries are for 64bit systems only

## 2.3

From this release the USERS table will also contain the "full" version of a user's nickname.<br>
In earlier versions user 'Tiger_Artist' would be saved only as 'tigerartist', the username used as url on the website. However from now on the USERS table will also contain the original name choosen by the user in a new column called 'NAMEFULL'.

The database version has been bumped up to 2.3 as well.

A few bugs have been squashed and some functions have been improved.

PS: I have no idea why but this release for Linux is over twice the size of previus ones. Will work on fixing it.

**Warning**: Binaries are for 64bit systems only

## 2.2

This new release is only a minor upgrade.

A new function has been added to check the cookies file for common errors in case a session cannot be created.

The cookies file has also been renamed to `FA.cookies.json` so that it can be opened properly as a json file for editing. The program will take care of renaming the file.

Uncaught exceptions have also been taken care of when loading the cookies file.

Latest updates in the program used for reading keystrokes and text have also been included in these latest binaries.

PS: I have no idea why but this release for Linux is over twice the size of the previus one. Will work on fixing it for the next release.

**Warning**: Binaries are for 64bit systems only

## 2.1

With this release all bugs with the users database are fixed and the informations are properly stored and saved.

The repair function has been expanded to include the users table. Repeating users, empty ones, names with capital letters and/or underscores and empty sections/folders fields will be automatically corrected by the program.

A big number of bugs have been fixed as well, for the full list see the [commits](https://github.com/MatteoCampinoti94/FALocalRepo/compare/v2.0.1...bdea9c2).

**Warning**: Binaries are for 64bit systems only

## 2.0.1

Fixed a bug in the update functions.

**Warning**: Binaries are for 64bit systems only

## 2.0

Big update and main version bump.

The program now also saves category, species, gender and rating of downloaded submissions. These can also be used during search.

Format ofthe on-screen output has ben completely changed for downloads and updates.

Databases can now be upgraded from earlier versions. Files from previous versions are backed up during the upgrade process. Submissions that are no longer present on the forum will be saved with default, generalized values.

The new favorites page on the forum can now be handled correctly.

**Warning**: Binaries are for 64bit systems only

## 1.5.1

CTRL-C and CTRL-D can now be used to return to the main menu from input fields (e.g. username/sections/options)

Various small fixes

**Extra**: My gpg key was mistakenly deleted, thus all previous verified commits now show up as unverified.<br>
This new release is now verified

**Warning**: Binaries are for 64bit systems only

## 1.5

This new version comes with the usual fixes and a whole new menu entry to analyze the database and repair it. More information in the readme.

**Warning**: Binaries are for 64bit systems only

## 1.4

The program now has a GUI! It is very simple and console-based, only a prototype of the planned one.

Search has also been added with its own menu entry, submissions can be searched for author, title and tags with regex support.

Version has been bumped up to 1.4 skipping 1.3 due to the two major additions.

**Warning**: Binaries are for 64bit systems only

## 1.2.1

Small fix to make sure the infos table has the database name value created empty, to ensure compatibility with planned gui.

Other changes are under-the-hood: moved some functions around and into modules to improve clarity and modularity.

**Warning**: Binaries are for 64bit systems only

## 1.2

Filetype detection now works reliably across Windows and Unix platforms!
Unfortunately safe exit still doesn't work reliably on Windows so it's still disabled on it.

A new informations table has been added to the database which stores:
* name of the database (for use in future versions)
* number of users
* number of submission
* time of last update start, in seconds since epoch
* duration of last update in seconds
* time of last download start, in seconds since epoch
* duration of last download in seconds

The table is created with all values reset to 0 in case it is not present so it's perfectly compatible with older versions.


**Warning**: Binaries are for 64bit systems only

## 1.1.2

The program can now be run on windows as well!

Unfortunately due to missing libraries on windows automatic filetype management and safe exit do NOT work so be careful.

**Warning**: Binaries are for 64bit systems only

## 1.1.1

The readme is now complete and contains all the instructions needed to use the program

Fixed a small bug in the sync code when using the Force option

A small search script has been added in the FA_tools folder

**Warning**: binary is for Linux 64bit only

## 1.1

Main change is usage of [cfscrape](https://github.com/Anorov/cloudflare-scrape) to bypass cloudflare wait at first request

Improved printout & printout for checks

If a user was disabled gallery, scraps and favorites are disabled in the database as well and only extras are downloaded if passed in sections

Better placement of interrupts for safe manual exit

General bugfixes

**Warning**: binary is for Linux 64bit only

## 1.0

Program now works and handles special cases

Exit codes for various events

Can interrupt at any moment using CTRL-C, exits safely

Needs cookies files

**Warning**: binary is for Linux 64bit only
