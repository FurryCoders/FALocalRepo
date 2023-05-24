# Changelog

## 4.4.4

### Changes

* The new version of FAAPI does not use [CloudflareScrape](https://github.com/Anorov/cloudflare-scrape) anymore

### Fixes

* Fix compatibility issues between version 2.0.0 of [urllib3](https://pypi.org/project/urllib3/)
  and [cfscrape](https://pypi.org/project/cfscrape/)

### Dependencies

* Use [faapi ~3.11.0](https://pypi.org/project/faapi/3.11.0)
    * Fix [issue #8](https://github.com/FurryCoders/FALocalRepo/issues/8)
    * Fix [CVE-2023-32681](https://cve.report/CVE-2023-32681)

## 4.4.3

### Fixes

* Fix user folders being incorrectly saved as `Folder.x` instead of just the folder name in the database when
  running `download users` on Python 3.11
    * Also fixes `ValueError: 'Folder.x' is not in list` errors when running `download update`
    * *NOTE:* To fix user folders with the wrong content, use the `database edit` command

### Dependencies

* Use [falocalrepo-database ~5.4.4](https://pypi.org/project/falocalrepo-database/5.4.4)
    * Fix crash on startup on Python 3.11

## 4.4.2

### New Features

* Support New Fur Affinity UI ✨
    * Support the new UI introduced on November 26, 2022
    * *Note:* the new UI does not show comment parents yet, but the parent comment link is still present in the HTML and
      just commented out, so the parser uses regex to extract the parent ID; this could cause unforeseen issues so be
      careful when downloading comments

### Dependencies

* Use [faapi ~3.10.0](https://pypi.org/project/faapi/3.10.0)
    * Support New Fur Affinity UI
    * Fix [issue #7](https://github.com/FurryCoders/FALocalRepo/issues/7)

## 4.4.1

### Fixes

* Fix dates for journals and submissions being parsed incorrectly on some occasions

### Dependencies

* Use [faapi ~3.9.6](https://pypi.org/project/faapi/3.9.6)
    * Fix incorrect parsing of dates on some journals and submissions
* Use [falocalrepo-server ~3.3.3](https://pypi.org/project/falocalrepo-server/3.3.3)
    * Fix issues with thumbnails and the zoom button for submissions with multiple files

## 4.4.0

### New Features

* \[BBCode\]
    * Thanks to the new HTML to BBCode converter introduced with [faapi 3.8.0](https://pypi.org/project/faapi),
      submissions, journals, and user profiles can now be stored in BBCode format instead of the raw HTML
    * BBCode mode can be toggled on and off using the new `database bbcode` command
    * BBCode mode greatly improves search results by removing HTML boilerplate, and reduces the size of the database
    * **Warning**: HTML to BBCode conversion (and vice versa) is still a work in progress, and it may cause some
      content to be lost, so a backup of the database should be made before changing the setting
* Database doctor 🩺
    * New `database doctor` command to check entries for errors and fix them when possible
    * Users are checked for inconsistencies in their name to make sure that they can be properly matched with their
      submissions, journals, and comments
    * Submissions are checked with their thumbnails and files to ensure they are consistent, and the program will
      attempt to add files that are in the submission folder but are not saved in the database
    * Comments are checked against their parents, if the parent object does not exist then the comment is deleted if
      the `--allow-deletion` option was used with `database doctor`
* Headers and footers
    * Submissions and journals now support headers and footers as separate columns in their respective tables
    * Headers and footers can be temporarily turned off when running `download` commands using the `--content-only`
      option; when turned off journal downloads are much faster, as the program doesn't need to get each individual
      journal page
* Pre-operation backups 💽
    * New triggers have been added to perform backups before config changes, database edits, and downloads instead of
      only afterwards

### Changes

* Comments are now saved by default and can be turned off with the `--no-comments` option (the old `--save-comments` is
  no longer supported)
* Improve formatting of counters during download
* Hide terminal cursor on Linux and macOS systems
* Allow second database of `database merge` command to be non-writable (e.g. if it is owned by root on a UNIX systems)

### Fixes

* Fix journals not being always saved when comments, headers, and footers were disabled, the journals folder was the
  last one to be downloaded/updated, and the download was interrupted manually or by an error
* Fix after-download counters not being correct if the download was interrupted
* Fix typos and errors in help messages
* Fix ` being removed from usernames

### Dependencies

* Use [faapi ~3.9.2](https://pypi.org/project/faapi/3.9.2)
    * Fix users with ` in their name not being handled correctly
    * BBCode to HTML conversion
    * Improvements to BBCode conversion
* Use [falocalrepo-database ~5.4.3](https://pypi.org/project/falocalrepo-database/5.4.3)
    * Add `SUBMISSIONS.FOOTER`, `JOURNAL.HEADER`, and `JOURNAL.FOOTER`
    * Add BBCode setting to `SETTINGS`
* Use [falocalrepo-server ~3.3.2](https://pypi.org/project/falocalrepo-server/3.3.2)
    * New grid view for submissions with multiple files
    * Support BBCode
    * Show user icons
    * Show headers and footers for submissions and journals
* Use [psutil ^5.9.3](https://pypi.org/project/faapi/5.9.3)

## 4.3.7

### Fixes

* Fix `config list` not working

## 4.3.6

### Fixes

* Fix remaining `--replace` option in `database add` help message

## 4.3.5

### Fixes

* Fix editing of non-submissions tables (USERS, JOURNALS, and COMMENTS)

### Dependencies

* Use [falocalrepo-server ~3.2.8](https://pypi.org/project/falocalrepo-server/3.2.8)

## 4.3.4

### Dependencies

* Use [faapi ~3.7.4](https://pypi.org/project/faapi/3.7.4)
    * Fix [CVE-2022-2309](https://cve.report/CVE-2022-2309.pdf) issue
* Use [falocalrepo-server ~3.2.7](https://pypi.org/project/falocalrepo-server/3.2.7)
    * Fix [CVE-2022-2309](https://cve.report/CVE-2022-2309.pdf) issue
* Use [falocalrepo-database ~5.3.7](https://pypi.org/project/falocalrepo-database/5.3.7)

## 4.3.3

### Changes

* Remove `--replace` option from `database add` command, the `database edit` command can be used modify existing entries

### Fixes

* Fix submission files extensions not being correctly detected for some files when adding/replacing them
  with `database edit`

### Dependencies

* falocalrepo-database dependency set to [\~5.3.5](https://pypi.org/project/falocalrepo-database/5.3.5)
    * Improve detection of plain text files

## 4.3.2

### Changes

* Remove `--browser` option from the `server` command as it had no effect since it was the default value;
  the `--no-browser` option remains to disable opening the browser automatically
* When an error is encountered during downloads, the program exists with status code 1 instead of 0

### Dependencies

* falocalrepo-server dependency set to [\~3.2.4](https://pypi.org/project/falocalrepo-server/3.2.4)

## 4.3.1

### New Features

* Open browser for server 💻
    * A new browser tab/window is opened automatically when using the `server` command
    * New `--browser` and `--no-browser` options for `server` to toggle opening the browser (defaults on)

### Changes

* Requests are timed out after 60 seconds to avoid infinite waits during file downloads.

### Dependencies

* falocalrepo-database dependency set to [\~5.3.4](https://pypi.org/project/falocalrepo-database/5.3.4)
    * Fix incorrect extension selection for files with non-specific MIME types (e.g. docx)
    * Interrupting a database backup does not leave a temporary file behind
* falocalrepo-server dependency set to [\~3.2.2](https://pypi.org/project/falocalrepo-server/3.2.2)
    * Open browser on startup
    * Fix [CVE-2022-30595](https://github.com/advisories/GHSA-hr8g-f6r6-mr22)
    * Fix journals searches
    * Fix visual errors
    * Support spoiler text
    * Add file counter in search results for submissions with multiple files
* faapi dependency set to [\~3.7.2](https://pypi.org/project/faapi/3.7.2)
    * Fix journals parsing when using full date format
    * Add requests timeout

## 4.3.0

### New Features

* Multiple submission files 🗂
    * Add extra submission files for submissions in the database for alts, extra versions, attachments, etc.
    * All submission files can be viewed with the web app
* Automatic backups 💾
    * Automatic backup options can be set using the new `config backup` command
    * Backup can be triggered for downloads, added/modified/removed entries, or modified options

### Changes

* Removed the `--relative/--absolute` option from `config files-folder` command, the given folder path is saved as-is
* The `@any` query field does not include `FAVORITES`, `FILESAVED`, `USERUPDATE`, nor `ACTIVE` to avoid redundant
  results
* The `@author` query field matches using `LIKE` instead of finding only exact matches (i.e. `ab` matches `cabd`, `abcd`
  , etc.)
* Show paths to submission files with `database view`

### Fixes

* Fix `database add` and `database edit` using submission thumbnail as submission file
* Fix missing `database edit` from `database` commands list
* Fix incorrect formatting for `database edit` and `database view` help
* Fix missing help message for `--replace` option of `database add` command

### Dependencies

* falocalrepo-database dependency set to [\~5.3.0](https://pypi.org/project/falocalrepo-database/5.3.0)
    * Support multiple submission files
* falocalrepo-server dependency set to [\~3.2.0](https://pypi.org/project/falocalrepo-server/3.2.0)
    * Support multiple submission files
    * Support video files for submissions
    * Update style to Bootstrap 5.2.0 (beta 1)
* faapi dependency set to [\~3.7.1](https://pypi.org/project/faapi/3.7.1)
    * Fix incorrect username extracted from userpages, which broke `@me` for `download` commands

## 4.2.6

### Changes

* `config files-folder` command does not move files by default, only when using the `--move` option
    * Remove `--no-move` option

### Fixes

* Fix `FileNotFoundError` when moving files to a new location with `config files-folder`

### Dependencies

* faapi dependency set to [\~3.7.0](https://pypi.org/project/faapi/3.7.0)
* falocalrepo-server dependency set to [\~3.1.4](https://pypi.org/project/falocalrepo-server/3.1.4)
* click dependency set to [\~8.1.3](https://pypi.org/project/click/8.1.3)

## 4.2.5

### Fixes

* Fix error occurring on watchlist download/update when adding a new watch for a user that wasn't part of the database
  already
* Fix `--replace` value not respect in `download users` for folders declared after a watchlist folder option

## 4.2.4

### Fixes

* Fix error when setting a new files folder using `config files-folder`

## 4.2.3

### Fixes

* Fix comments for submissions overwriting comments for journals (and vice versa) if the comment ID was the same
    * Caused by Fur Affinity not using a unique ID key for comments, using instead the submission/journal ID as part of
      unique index

### Dependencies

* falocalrepo-database dependency set to [\~5.2.2](https://pypi.org/project/falocalrepo-database/5.2.2)
    * Update `COMMENTS` table to accept comments with same ID but different parent
* falocalrepo-server dependency set to [\~3.1.2](https://pypi.org/project/falocalrepo-server/3.1.2)

## 4.2.2

### New Features

* Comments to submissions and journals can now be viewed directly in the terminal with `database view` using
  the `--view-comments` option

### Changes

* Improvements to link rendering with `database view`

### Fixes

* Fix `database merge` and `database copy` not finding all entries when using `%` as query

### Dependencies

* falocalrepo-server dependency set to [\~3.1.1](https://pypi.org/project/falocalrepo-server/3.1.1)

## 4.2.1

### New Features

* New `--replace` option for `download users`
    * Update metadata for entire user galleries
    * Fetch the latest comments with the `--save-comments` option

### Changes

* Add comments to `database info`

### Fixes

* Fix journals stopping after the first page due to a change in Fur Affinity's journals page that broke the FAAPI parser
    * To fix the affected users and download their journals, use the following
      command `download update -f journals --stop 9999`
        * This will update all users that have `journals` in their folders, and not stop until 9999 journals are found
          in the database for each user (or no more journals are available on FA)
        * To be sure that all journals are downloaded, a higher stop number can be used
* Fix database merge/copy not working because of `COMMENTS` table

### Dependencies

* faapi dependency set to [\~3.6.1](https://pypi.org/project/faapi/3.6.1)
    * Fix `FAAPI.journals` not detecting the next page correctly, caused by a change in Fur Affinity's journals page
* falocalrepo-database dependency set to [\~5.2.1](https://pypi.org/project/falocalrepo-database/5.2.1)
    * Fix missing support for merge/copy of `COMMENTS` table

## 4.2.0

### New Features

* Comments! 💬
    * New `--save-comments` option for `download` commands allows saving comments of submissions and journals
    * Comments can be updated on a per-entry basis using the `download submission` and `download journal` commands with
      both the `--replace` and `--save-comments` options enabled
    * Comments can be viewed with the `database view` command and in the web app with the `server` command
    * Search, view, edit, remove, etc. all work with comments
        * Submissions and journals search cannot query the comments table

### Fixes

* Fix incorrect argument error for `download journals`

### Dependencies

* falocalrepo-database dependency set to [\~5.2.0](https://pypi.org/project/falocalrepo-database/5.2.0)
    * Add comments table
* falocalrepo-server dependency set to [\~3.1.0](https://pypi.org/project/falocalrepo-server/3.1.0)
    * View comments for submissions and journals

## 4.1.13

### Dependencies

* faapi dependency set to [\~3.6.0](https://pypi.org/project/faapi/3.6.0)
* falocalrepo-server dependency set to [\~3.0.5](https://pypi.org/project/falocalrepo-server/3.0.5)
* click dependency set to [\~8.1.2](https://pypi.org/project/click/8.1.2)

## 4.1.12

### Changes

* `--retry` option for `download` commands defaults to 1
* Removed `--retry` option from `download journals` (it is only used for file downloads, which never occur when
  downloading journals only)

### Dependencies

* falocalrepo-server dependency set to [\~3.0.4](https://pypi.org/project/falocalrepo-server/3.0.4)
* faapi dependency set to [\~3.5.0](https://pypi.org/project/faapi/3.5.0)

## 4.1.11

### New Features

* Added `--retry` option to `download` commands. When set, failed submission files and thumbnails downloads will be
  performed again up to a maximum of 5 retries.

### Dependencies

* falocalrepo-server dependency set to [\~3.0.3](https://pypi.org/project/falocalrepo-server/3.0.3)

## 4.1.10

### Changes

* Separate download counter for userpages to make the "modified users" counter specific to changes to `ACTIVE`
  and `FOLDERS`

### Fixes

* Fix some download counters not giving the correct amount of unique entries
* Fix rare error when using the `database view` command on entries that contained CSS color styles that were not
  lowercase, causing the color to not be displayed correctly

### Dependencies

* falocalrepo-server dependency set to [\~3.0.2](https://pypi.org/project/falocalrepo-server/3.0.2)
    * Change default sorting column of journals and submissions to `DATE` (same results as `ID`)
    * Fix rare decoding error when the submission file was an unrecognized file format and the file url had no extension

## 4.1.9

### New Features

* Fully rewritten web server!
    * Completely new UI using [Bootstrap](https://getbootstrap.com) for a responsive, modern interface
    * Javascript usage has been almost completely eliminated for a much faster experience and lighter load
    * Search settings can now be customized for each table and saved in the database
    * Search results can be viewed in both list and card (with thumbnails for submissions) mode for all tables and
      device sizes

### Changes

* A message is now printed when using `database upgrade` on a database that is already up-to-date
* A message is now printed when no users can be updated with `download update` (either because the `--like` queries
  returned no results or because the selected users are not active)
* Give meaningful error messages for those cases where the program does not have read or write access to the database
  path or its parent folder, or if the latter does not exist

### Fixes

* Fix deleted users (accounts that have been removed instead of simply disabled) not being deactivated in the database
  during `download users` and `download update`
* Fix watchlists downloads and updates causing users to be deactivated
* Fix uncaught `OperationalError` exception raised when calling `init` with a database path pointing to an external
  volume that wasn't mounted or other inaccessible location

### Dependencies

* falocalrepo-database dependency set to [\~5.1.2](https://pypi.org/project/falocalrepo-database/5.1.2)
    * Add a new `ACTIVE` column to the `USERS` table for easier tracking of inactive users (added in version 5.1.0)
    * Fix `CATEGORY` column in the `SUBMISSIONS` not respecting spaces around slashes (/) as they are shown on Fur
      Affinity
* falocalrepo-server dependency set to [\~3.0.0](https://pypi.org/project/falocalrepo-server/3.0.0)
    * Fully rewritten frontend using Bootstrap and almost no Javascript for a much faster and more responsive experience
* faapi dependency set to [\~3.4.3](https://pypi.org/project/faapi/3.4.3)
    * Fix submission category not respecting spaces around slashes (/) as they are shown on Fur Affinity

## 4.1.8

### Changes

* If an invalid username (one that does not contain any of the allowed characters `[a-z0-9.~-]` and is not `@me`) is
  passed to `download users` and `download update` an error is raised and the program stops
* Raise a clear error if no cookies are saved in the database instead of raising `faapi.exceptions.Unauthorized`
* Handle `faapi.exceptions.Unauthorized` if it's caught during a download
* Login status is checked before starting a download

### Fixes

* Fix unexpected keyword argument error in `paw` command
* Fix invalid usernames passing through `download users` and `download update` arguments parsers without errors
* Fix download history event added even when the download never started
* Fix rare error occurring when setting a crawl delay with `FALOCALREPO_CRAWL_DELAY` and Fur Affinity's robots.txt was
  somehow empty
* Fix missing color formatting in `config cookies` help message

## 4.1.7

### Fixes

* Fix submissions not being fully updated if a submission is already present in the database and has changed folder
  since it was downloaded

## 4.1.6

### Fixes

* Fix incorrect formatting of error message when `database view` could not find the entry
* Fix missing `@me` information in `download users` and `download update` help messages
* Fix inverted `UPDATED` and `ADDED FAV` messages when downloading submissions via `download users`
  and `download update`

## 4.1.5

### New Features

* Add support for `@me` user in `download users` and `download update` commands to select own username
    * The username is fetched at the start of the download process

### Changes

* The `download update` command treats watchlists updates like downloads
    * During updates, only modified/added entries will be shown unless the `--stop` option is used, in which case all
      entries are shown

### Fixes

* Fix crashes when piping output of `download` commands
* Fix watchlists updates stopping too early because of alphabetic sorting
* Fix modified entries being considered as found by `download update`, stopping the update too early
* Fix color ANSI codes used by `download` output for userpages not being turned off for pipes or when using `--no-color`
  option

## 4.1.4

### Fixes

* Fix `database date` throwing an error when called without `--filter-date`

## 4.1.3

### Changes

* Catch request exceptions during `download` commands for better output and graceful exit

### Fixes

* Fix leftover debug code blocking the terminal width to 80 columns
* Fix incorrect output of `download login` when `FALOCALREPO_FA_ROOT` was set

## 4.1.2

### Fixes

* Fix infinite loop on `download` if the terminal width was too small

## 4.1.1

### Fixes

* Fix users being set as modified when using `download update` with a watchlist folder
* Fix `download update` throwing an error if no `--user` option was given

## 4.1.0

### New Features

* Add `database view` command to view entries directly in the terminal
    * Alignment, colors, emphasis, links and more are converted from the HTML fields and formatted for the terminal
* Add watchlist by/to support to `download users`
    * Creates/modifies user entries for each user found in the specified watchlist
* Allow passing SQLite LIKE queries to `--user` arguments of `download update`
* Add `--filter-date` option to `database history`
* Use `FALOCALREPO_FA_ROOT` environment variable to set Fur Affinity request root
* Shell completions for `database search` columns
* Shell completions for `help` commands

### Changes

* Rewrite of the download handler to be more stable and fix inconsistent output
* Remove `database export` command
    * `database search` can produce the same output with the `--column @` option and piping
* Table column widths for `table` output of `database search` command are now set using the `--table-widths` option
* History events are not added for `download` command using `--dry-run`
* Rename `--true-color` option to `--truecolor` for `paw` command

### Fixes

* Fix `help` raising an error if the command seeking help for required an existing database file which couldn't be
  found, but was set by the `FALOCALREPO_DATABASE` environment variable.
* Fix rare inconsistent download output

### Dependencies

* faapi dependency set to [\~3.4.2](https://pypi.org/project/faapi/3.4.2)
    * Detect users pending deletion and flag them as deactivated

## 4.0.11

### Fixes

* Fix `download update` command warning for users not in archive

## 4.0.10

### New Features

* Print an error for users given to `download update` command that aren't in the archive
* Use `FALOCALREPO_CRAWL_DELAY` environment variable to set a crawl delay higher (or equal) than the one in Fur
  Affinity's [robots.txt](https://furaffinity.net/robots.txt)

### Changes

* Improve download messages for journals

### Fixes

* Fix submissions that changed folder not being updated

## 4.0.9

### Changes

* Improved colors in the `paw` command help

### Fixes

* Fix error when `--report-file` was used together with a `download` command concerning user pages.

## 4.0.8

### New Features

* `database search` command now supports multiple `--sort` options for multiple levels of sorting (e.g. `AUTHOR asc`
  and `ID desc`)
* `--report-file` option added to `download` functions (excluding `download login`) to print a detailed report in JSON
  format to a file

### Changes

* Remove `--order` option of `database search` command, the `--sort` option now handles both columns and sorting order
* The last entry found during `download update` is cleared only if the `--stop` option is left to its default value of 1
* `download` reports are more detailed and broken down by type (users, submissions, and journals)
* `download` reports use _thumbnail_ instead of _thumb_

### Fixes

* Fix non-printable character in simple output mode (enabled automatically when not printing to a terminal) for
  `download` commands
* Fix missing color for `IN DB` message during user page downloads

## 4.0.7

### New Features

* Add `--verbose-report` option to `download` functions (excluding `download login`)

### Fixes

* Fix user pages being updated incorrectly

### Dependencies

* faapi dependency set to [\~3.4.1](https://pypi.org/project/faapi/3.4.1)
    * Fix incorrect parsing of notice error messages
        * Fix incorrect detection of not found errors

## 4.0.6

### Changes

* Improved download error handling
* `paw` command detects terminal color capabilities and enables truecolor automatically if supported
    * Add option to manually switch to 8bit color mode
* Add deactivated users to download report

### Dependencies

* faapi dependency set to [\~3.4.0](https://pypi.org/project/faapi/3.4.0)
    * Improve exceptions

## 4.0.5

### Changes

* Better replacement of non-ASCII characters. Only characters with a Unicode width greater than 1 are replaced.

### Fixes

* Fix `database search` JSON output for submissions and journals
* Fix `database search` CSV output columns
* Fix `database search` colorized table output not being enabled unless turned on explicitly with `--color`

## 4.0.4

### New Features

* Add `paw` command, show some PRIDE colors!

### Changes

* Improve dry run behaviour for `download` commands

### Fixes

* Fix favorites being incorrectly saved in the database if the submission was downloaded as a favorite first.
* Fix incorrect history entry for `config files-folder`
* Fix users and folders not respecting arguments order when using `download update`

### Dependencies

* falocalrepo-database dependency set to [\~5.0.10](https://pypi.org/project/falocalrepo-database/5.0.10)
    * Fix favorites errors, see _Notes_ below for details on upgrade.
* falocalrepo-server dependency set to [\~2.1.1](https://pypi.org/project/falocalrepo-server/2.1.1)
    * Improve descriptions and profiles
    * Fix loading user stats for users not in the database

### Notes

The database upgrade to version 5.0.10 contains a fix for incorrect favorites. Favorites added manually using
the `database edit` command will not be conserved, unless the users are saved in the USERS table and the `favorites`
folders is enabled for them. Some favorites will also be removed even if the user has the `favorites` folder enabled.

To restore the favorites, use the `download users` command to download them again.

## 4.0.3

### Changes

* Move to new repository at [GitHub/FurryCoders/FALocalRepo](https://github.com/FurryCoders/FALocalRepo)
* Improved output for download operations
* Clear userpage update lines if no change is saved
* User pages update download and modify counters

### Fixes

* Fix formatting error when printing database search results with non ASCII characters
* Fix report formatting error when interrupting a download operation
* Fix repeated user arguments for download operations triggering multiple downloads

### Dependencies

* faapi dependency set to [\~3.3.7](https://pypi.org/project/faapi/3.3.7)
    * No changes, move to new repository
* falocalrepo-database dependency set to [\~5.0.8](https://pypi.org/project/falocalrepo-database/5.0.8)
    * No changes, move to new repository
* falocalrepo-server dependency set to [\~2.1.0](https://pypi.org/project/falocalrepo-server/2.1.0)
    * Use [Click](https://click.palletsprojects.com) to handle arguments
    * Move to new repository

## 4.0.2

### Dependencies

* faapi dependency set to [\~3.3.6](https://pypi.org/project/faapi/3.3.6)
    * Fix parsing error when downloading user profile with limited info or contacts

## 4.0.1

### Changes

* Always print download report (also when manually interrupting)

### Fixes

* Fix userpage download
* Fix `--no-color` option not working in `download login` command when login failed

### Dependencies

* falocalrepo-database dependency set to [\~5.0.7](https://pypi.org/project/falocalrepo-database/5.0.7)
    * Fix possible duplicate values in list columns

## 4.0.0 - 200th Release!

### New Features

* Colorized output using ANSI codes
* Shell completions
* Database search using advanced query language
* Complete rewrite using Python 3.10 and [Click](https://click.palletsprojects.com)
* Add support to download user profiles
* Add filtering and clearing to history command

### Changes

* History events added only when database is modified

### Dependencies

* faapi dependency set to [\~3.3.5](https://pypi.org/project/faapi/3.3.5)
    * Upgrade to Python 3.9+
    * Improved parsing
    * Fully documented and type-annotated
* falocalrepo-database dependency set to [\~5.0.5](https://pypi.org/project/falocalrepo-database/5.0.5)
    * Add `USERS.USERPAGE` column
    * Separate `HISTORY` table
    * Improved type safety
    * Improved efficiency
* falocalrepo-server dependency set to [\~2.0.1](https://pypi.org/project/falocalrepo-server/2.0.1)
    * Improved styling with fonts and responsive design
    * Improved efficiency

## 3.25.0

### Changes

* Move `--update` option to its own `update` command

### Fixes

* Fix `SystemExit` being caught as an error

### Dependencies

* falocalrepo-server dependency set to [\~1.14.0](https://pypi.org/project/falocalrepo-server/1.14.0)
    * Change behaviour of HTTP to HTTPS redirection

## 3.24.1

### Changes

* Add new `move` argument to `config files-folder` command to skip moving the files to the new location

### Fixes

* Fix possible errors when passing 0 as port to `database server`

### Dependencies

* falocalrepo-server dependency set to [\~1.13.0](https://pypi.org/project/falocalrepo-server/1.13.0)
    * Support new HTTP redirection
        * Add `redirect-http` argument to `database server` command

## 3.24.0

### Fixes

* Fix rare errors caused by unexpected keyword arguments passed to the exception-raiser function
* Fix error causing keyword arguments with spaces to be ignored

### Dependencies

* falocalrepo-database dependency set to [\~4.19.3](https://pypi.org/project/falocalrepo-database/4.19.3)
    * Check database connection before opening database
* falocalrepo-server dependency set to [\~1.12.0](https://pypi.org/project/falocalrepo-server/1.12.0)
    * Support new SSL arguments and change default port to 80/443
        * Add `ssl-cert` and `ssl-key` arguments to `database server` command

## 3.23.15

### Dependencies

* falocalrepo-database dependency set to [\~4.19.1](https://pypi.org/project/falocalrepo-database/4.19.1)
    * Submissions tags are no longer sorted alphabetically

## 3.23.14

### Fixes

* Fix error when using `database search` commands with no search parameters
* Fix error when using `database merge` and `database copy` commands with no selection parameters

### Dependencies

* falocalrepo-database dependency set to [\~4.19.0](https://pypi.org/project/falocalrepo-database/4.19.0)
* falocalrepo-server dependency set to [\~1.11.0](https://pypi.org/project/falocalrepo-server/1.11.0)

## 3.23.13

### Fixes

* Fix error in `database add-submission` occurring when not passing a new file/thumbnail with none already present in
  the database

## 3.23.12

### Fixes

* Fix absolute files' folder path printed by `config` command
* Fix a type error that caused `database add-submission` to crash

### Dependencies

* falocalrepo-database dependency set to [\~4.18.1](https://pypi.org/project/falocalrepo-database/4.18.1)

## 3.23.11

### Fixes

* Reduced minimum width of user column when printing search results to avoid over-padding

### Dependencies

* falocalrepo-database dependency set to [\~4.18.0](https://pypi.org/project/falocalrepo-database/4.18.0)
    * Use ISO format YYYY-MM-DD**T**HH:MM for date columns

## 3.23.10

### Fixes

* Fix `download update` bug when passing parameters

## 3.23.9

### Changes

* Add support for `any` parameter in database search

### Dependencies

* falocalrepo-database dependency set to [\~4.17.0](https://pypi.org/project/falocalrepo-database/4.17.0)

## 3.23.8

### Changes

* The `config` command prints the absolute path of the files' folder together with its database value
* The `database info` command shows the location of the database

### Fixes

* Fix incorrect output when using the `database search-submisisons` and `database search-journals` commands
* Fix matching of some edge cases of `<param>=<value>` arguments

## 3.23.7

### Fixes

* Fix `database server` not closing properly (the database file could still be read as open on some systems)

## 3.23.6

### Fixes

* Fix `database server` throwing a `TypeError` exception when passing port parameter

## 3.23.5

### Changes

* `database server` command does not occupy a database connection to allow running other commands on the same database
  while the server is running

### Dependencies

* falocalrepo-database dependency set to [\~4.16.2](https://pypi.org/project/falocalrepo-database/4.16.2)

## 3.23.4

### Fixes

* Fix `database add-user` command

## 3.23.3

### Dependencies

* faapi dependency set to [\~2.18.0](https://pypi.org/project/faapi/2.18.0)

## 3.23.2

### Dependencies

* falocalrepo-database dependency set to [\~4.16.0](https://pypi.org/project/falocalrepo-database/4.16.0)

## 3.23.1

### Dependencies

* falocalrepo-server dependency set to [\~1.10.0](https://pypi.org/project/falocalrepo-server/1.10.0)

## 3.23.0

### Changes

* `database add-user`, `add-submission`, and `add-journal` commands now take metadata via JSON files

### Fixes

* Fix errors and invalid examples in help messages

### Dependencies

* falocalrepo-database dependency set to [\~4.15.0](https://pypi.org/project/falocalrepo-database/4.15.0)

## 3.22.1

### Changes

* `database merge` command supports selectors like `database copy`

### Dependencies

* falocalrepo-database dependency set to [\~4.14.0](https://pypi.org/project/falocalrepo-database/4.14.0)

## 3.22.0

### Changes

* Add `database copy` command

### Fixes

* Fix `config files-folder` command error

### Dependencies

* falocalrepo-database dependency set to [\~4.13.0](https://pypi.org/project/falocalrepo-database/4.13.0)

## 3.21.3

### Changes

* Check connections to selected database to ensure only one is active
* Check multiple instances of the program only when running the `download` command
* Any version difference will trigger an error

### Dependencies

* falocalrepo-database dependency set to [\~4.12.0](https://pypi.org/project/falocalrepo-database/4.12.0)

## 3.21.2

### Fixes

* Fix error with `database add submission` command

## 3.21.1

### Changes

* Database version is checked for all `database` commands, but no exception is raised for `info` and `upgrade`

## 3.21.0

### Changes

* Migrate to Python 3.9

### Dependencies

* falocalrepo-database dependency set to [\~4.11.0](https://pypi.org/project/falocalrepo-database/4.11.0)
* falocalrepo-server dependency set to [\~1.9.0](https://pypi.org/project/falocalrepo-server/1.9.0)
    * Solve issue #9

## 3.20.3

### Changes

* Let `UnknownFolder` exceptions rise, exit with code 3 when caught
    * Error codes that were 3 or greater have been moved up by 1
        * 1 `MalformedCommand`, `UnknownCommand`
        * 2 `MultipleInstances`
        * 3 `UnknownFolder`
        * 4 `ConnectionError`
        * 5 `DatabaseError`, `IntegrityError`
        * 6 `TypeError`, `AssertionError`
        * 7 `Exception`, `BaseException`
* Exception `repr` is not printed if `FALOCALREPO_DEBUG` option is on

### Fixes

* Fix `columns` option being ignore in database search commands
* Fix `columns` not being selected properly when used in conjunction with `json` option in database search commands

## 3.20.2

### Changes

* Print environmental variables flags to stderr

## 3.20.1

### Fixes

* Fix `KeyError`'s in search

## 3.20.0

### Changes

* Add `json` and `columns` options to database search commands to output results in JSON format

### Fixes

* Fix zero-padded ID's not being matched by search commands
* Fix possible output error during single submissions download

## 3.19.4

### Fixes

* Fix output error in `download submissions` command

## 3.19.3

### Fixes

* Catch `NoSuchProcess` exception when checking for other instances of falocalrepo

## 3.19.2

### Fixes

* Fix incorrect call to database merge

## 3.19.1

### Fixes

* Fix printing of users search results

## 3.19.0

### Changes

* Add `database upgrade` command, do not upgrade automatically
* Check database version and stop if major or minor do not match with falocalrepo-database

### Fixes

* Fix `database add-user` folders error

### Dependencies

* falocalrepo-database dependency set to [\~4.9.4](https://pypi.org/project/falocalrepo-database/4.9.4)
    * Solve issue [#6](https://gitlab.com/MatteoCampinoti94/FALocalRepo/-/issues/6)

## 3.18.2

### Dependencies

* falocalrepo-database dependency set to [\~4.9.4](https://pypi.org/project/falocalrepo-database/4.9.4)
    * Solve issue [#5](https://gitlab.com/MatteoCampinoti94/FALocalRepo/-/issues/5)

## 3.18.1

### Fixes

* Fix a type signature causing a startup crash in some systems
    * Solve issue [#4](https://gitlab.com/MatteoCampinoti94/FALocalRepo/-/issues/4)

## 3.18.0

### Dependencies

* falocalrepo-database dependency set to [\~4.9.0](https://pypi.org/project/falocalrepo-database/4.9.0)
    * Support new `TYPE` column in `SUBMISSIONS`
* faapi dependency set to [\~2.17.0](https://pypi.org/project/faapi/2.17.0)
    * Download submissions thumbnails

## 3.17.2

### Dependencies

* falocalrepo-database dependency set to [\~4.8.0](https://pypi.org/project/falocalrepo-database/4.8.0)
    * Use new bar-separation for list fields

## 3.17.1

### Changes

* Use the same output format for all `config` commands
* Print caught exceptions and traceback to standard error
* `UnknownFolder` exception is caught and handled inside download functions instead of rising

## 3.17.0

### Changes

* Add `deactivated` option to the `download update` command to check previously deactivated users again
* Use "deactivated" instead of "disabled" in output messages

## 3.16.13

### Changes

* Check downloaded size against requests headers before saving submission files

## 3.16.12

### Fixes

* Fix error when opening help for `database add-user`

## 3.16.11

### Changes

* `download submissions` and `download journals` never overwrite items already in the database

### Fixes

* Fix printing errors with `download submissions` and `download journals` that occurred if items where already in the
  database

## 3.16.10

### Fixes

* Fix sorting of users used in download arguments

## 3.16.9

### Fixes

* Fix `IS IN DB` message remaining when downloading journals

## 3.16.8

### Fixes

* Remove test code that interfered with item clearing on update stop

## 3.16.7

### Changes

* When using a stop number higher than 1 for `download update`, the last found item is not cleared
* Do not display `IS IN DB` message until all database transactions are complete
* Display `SEARCH DB` message while checking of a submission/journal is already in the database

### Fixes

* Fix an error in the completion bar function

## 3.16.6

### Fixes

* Fix output error for users search results
* Remove unnecessary debug call

## 3.16.5

### Fixes

* Fix update not finding changed folders correctly
* Fix update considering items as updated for users' galleries/scraps even when downloaded as favorites

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

### Fixes

* Fix submission tags not being sorted when adding a submission manually with `database add-submission`

### Dependencies

* falocalrepo-database dependency set to [\~4.7.0](https://pypi.org/project/falocalrepo-database/4.7.0)
    * Support new `MENTIONS` and `USERUPDATE` columns for journals and submission entries
* faapi dependency set to [\~2.15.0](https://pypi.org/project/faapi/2.15.0)
    * Remove calls to check user existence/status and instead rely on faapi exceptions

## 3.15.7

### Changes

* Add support for `FALOCALREPO_DEBUG` environmental variable

### Fixes

* Fix help message not displaying when no commands were passed

## 3.15.6

### Dependencies

* falocalrepo-database dependency set to [\~4.4.0](https://pypi.org/project/falocalrepo-database/4.4.0)
    * Support new `FAVORITE` column for submission entries

## 3.15.5

### Dependencies

* falocalrepo-server dependency set to [\~1.8.0](https://pypi.org/project/falocalrepo-server/1.8.0)

## 3.15.4

### Fixes

* The multiple instance check will not be triggered by modules that contain `falocalrepo` in their name (
  e.g. `falocalrepo-server`)

## 3.15.3

### Changes

* FAAPI (from [faapi](https://pypi.org/project/faapi)) is not loaded until needed. Commands structure is checked before
  connection is attempted
* Cookies are listed as-are to allow checking for errors (e.g. incorrect `name` field)

## 3.15.2

### Dependencies

* faapi dependency set to [\~2.12.0](https://pypi.org/project/faapi/2.12.0)

## 3.15.1

### Dependencies

* falocalrepo-server dependency set to [\~1.7.0](https://pypi.org/project/falocalrepo-server/1.7.0)

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

### Dependencies

* falocalrepo-database dependency set to [\~4.3.0](https://pypi.org/project/falocalrepo-database/4.3.0)
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

* Changed order of `database info` output

### Dependencies

* faapi dependency set to [\~2.11.0](https://pypi.org/project/faapi/2.11.0)

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

* Improve readme

### Dependencies

* falocalrepo-server dependency set to [\~1.6.0](https://pypi.org/project/falocalrepo-server/1.6.0)

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

With this new release comes the all-new [falocalrepo-database](https://pypi.org/project/falocalrepo-database) version 4.
Some column names in the database have been changed and the insertion functions have been made safer with built-in
checks. Search is now much more versatile and allows to query any columns in the users, submissions, and journals
tables. Thanks to the new checks, the `database check-errors` command was removed, as the new checks remove the
possibility of inserting erroneous data. The update function will notify of any faulty entry during the automatic update
of the database.

### Changes

* Improve data-entry safety
* Remove `database check-errors` command
* Allow to use all table columns for submissions and journals search

### Dependencies

* falocalrepo-database dependency set to [\~4.2.0](https://pypi.org/project/falocalrepo-database/4.2.0)
* falocalrepo-server dependency set to [\~1.5.0](https://pypi.org/project/falocalrepo-server/1.5.0)

## 3.12.1

### Changes

* Print `FALOCALREPO_DATABASE` environmental variable if used

### Fixes

* Fix missing messages for assertion errors

## 3.12.0

This new minor bump adds a new `list-<folder>` option to the download users command. Using it allows to list all remote
items present in a user folder without downloading them. Environmental variables are now supported starting
with `FALOCALREPO_DATABASE` which allows to set a different path for the database and files folder root.

### Changes

* Add `list-<folder>` folders to download users command
* Add `FALOCALREPO_DATABASE` environmental variable
* Remove subcommands arguments details from general help messages

### Fixes

* Fix padding inconsistencies in users search results
* Fix missing newline when server closes

### Dependencies

* falocalrepo-server dependency set to [\~1.4.0](https://pypi.org/project/falocalrepo-server/1.4.0)

## 3.11.0

This new minor version bump updates the [falocalrepo-database](https://pypi.org/project/falocalrepo-database/)
dependency to its latest version and adds a new `database merge` command. This new command allows to merge the database
located in the current folder with a second database located in another folder.

### Changes

* Add `database merge` command

### Dependencies

* falocalrepo-database dependency set to [\~3.8.0](https://pypi.org/project/falocalrepo-database/3.8.0)

## 3.10.11

### Fixes

* Fix an error occurring when date format was set to "
  full" [faapi#1](https://gitlab.com/MatteoCampinoti94/FAAPI/-/issues/1)

### Dependencies

* faapi dependency set to [2.10.2](https://pypi.org/project/faapi/2.10.2)

## 3.10.10

### Changes

* removed unused filetype dependency

## 3.10.9

### Changes

* Improved `search-users` command

### Fixes

* fix id parameter error when manually adding submissions/journals

### Dependencies

* falocalrepo-database dependency set to [\~3.7.1](https://pypi.org/project/falocalrepo-database/3.7.1)
* falocalrepo-server dependency set to [\~1.3.4](https://pypi.org/project/falocalrepo-server/1.3.4)

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

* Default database search order to ID/USERNAME
* Add some information on `order` parameter for database searches in readme

### Fixes

* Fix download error caused by faapi version 2.10.0

### Dependencies

* faapi dependency set to [2.10.1](https://pypi.org/project/faapi/2.10.1)

## 3.10.4

### Changes

* Better detection of deactivated users with updated faapi methods

### Dependencies

* faapi dependency set to [2.10.0](https://pypi.org/project/faapi/2.10.0)

## 3.10.3

### Dependencies

* faapi dependency set to [2.9.1](https://pypi.org/project/faapi/2.9.1)

## 3.10.2

### Fixes

* Fix error with users journals download

## 3.10.1

### Dependencies

* faapi dependency set to [2.9.0](https://pypi.org/project/faapi/2.9.0)

## 3.10.0

Added a new `database search-users` command to search the users table using all the collected metadata. The readme has
been improved slightly with better explanations. A small error in the database command help message was fixed.

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

Both the database and server modules have been update to versions 3.5.0 and 1.3.1 respectively. The database now holds a
history of all commands (except for version printing and help) instead of just last start and last update, and A
new `database history` command was added to print the commands' history.

When a non-help command is used, the program now checks for updates to its components and prints them to screen.

More exceptions are caught now and exit with a specific code; unforeseen exceptions are also caught and their trace
saved to FA.log.

### Changes

* Added `database history` command
* Catch ConnectionError and sqlite3.DatabaseError
* Catch general Exception and BaseException and print trace to FA.log

### Fixes

* Fix error with manual submissions and journals

### Dependencies

* falocalrepo-database dependency set to [\~3.5.0](https://pypi.org/project/falocalrepo-database/3.5.0)
* falocalrepo-server dependency set to [\~1.3.1](https://pypi.org/project/falocalrepo-server/1.3.1)

## 3.8.2

### Changes

* Added `-s`, `--server` option to print version of falocalrepo-server used by the program

### Fixes

* Fix missing instructions for download help

## 3.8.1

### Fixes

* Removed some lines of code used for debugging version 3.8.0 (now yanked)

## 3.8.0

From this release all database functions are handled separately by the
new [falocalrepo-database](https://pypi.org/project/falocalrepo-database/) package. The package is also used
in [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) allowing the falocalrepo console to be updated
more easily.

### Changes

* removed database functions in favor of [falocalrepo-database](https://pypi.org/project/falocalrepo-database/)

### Fixes

* Fixed an error in the description of tables in the readme

### Dependencies

* falocalrepo-database dependency set to [\~3.2.4](https://pypi.org/project/falocalrepo-database/3.2.4)
* falocalrepo-server dependency set to [\~1.2.2](https://pypi.org/project/falocalrepo-server/1.2.2)

## 3.7.5

The `download journals` command is now fixed and calling the correct function. Two sub-commands aliases have been
added: `config list` and `database info` which act as `config` and `database` respectively when called without
arguments. Database size in MB (base 10) and last start have been added to `database info` output, missing journals
counter in database info has also been added. falocalrepo-server dependency updated
to [^1.1.3](https://pypi.org/project/falocalrepo-server/1.1.3).

### Changes

* `database info` command to display database information
* `config list` command to list settings stored in database
* Database size and last start added to database info output

### Fixes

* Fixed `download journals`
* Added missing journals counter in database info output

### Dependencies

* falocalrepo-server dependency updated to [^1.1.3](https://pypi.org/project/falocalrepo-server/1.1.3)

## 3.7.4

### Dependencies

* Update faapi dependency to [2.8.3](https://pypi.org/project/faapi/2.8.3)

## 3.7.3

Background changes and fixes. The `main_console` function was renamed to `console` and is now the only direct export of
the package, falocalrepo-server dependency has been updated to ^1.1.2, help messages have been slightly reformatted, and
command does not default to `init` when absent.

### Changes

* Update help messages with falocalrepo, database and falocalrepo-server versions
* `main_console` renamed to `console`
* Parameters (e.g. `database search-submissions` search fields) are taken as are and not lowered
* LASTART value is not set when using `init`
* Calling without a command shows help, doesn't default to `init`

### Fixes

* Fix indentation of help messages

### Dependencies

* Update falocalrepo-server dependency to [^1.1.2](https://pypi.org/project/falocalrepo-server/1.1.2)

## 3.7.2

falocalrepo-server dependency has been updated to use the latest above 1.1.1. Command defaults to init if no command is
passed.

### Changes

* Default to init command if no command is passed

### Dependencies

* Update falocalrepo-server dependency to [^1.1.1](https://pypi.org/project/falocalrepo-server/1.1.1)

## 3.7.1

### Dependencies

* Update falocalrepo-server dependency to [1.1.1](https://pypi.org/project/falocalrepo-server/1.1.1)

## 3.7.0

The server interface has been moved to its own separate
package [falocalrepo-server](https://pypi.org/project/falocalrepo-server/) for ease of development, and it is now a
dependency of falocalrepo.

A few small bugs have also been fixed.

### Changes

* Transfer falocalrepo-server to its own package
* Make falocalrepo-server a dependency

### Fixes

* Fix incorrect exception in download journals command
* Fix erroneous FurAffinity theme name in readme
* Fix missing entry in table of contents

### Dependencies

* Set falocalrepo-server dependency to [1.0.0](https://pypi.org/project/falocalrepo-server/1.0.0)

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

A new `database server` command has been added, which starts a Flask server that allows to search the local database and
visualise submissions and journals in a friendly GUI.

The web interface allows to search the database using the same options and methods as the `database search-submissions`
and `database search-journals` commands.

Command line search commands now support `order`, `limit` and `offset` parameters for finer control of database
searches. For a more in-depth explanation refer to
the [SQLite SELECT documentation](https://sqlite.org/lang_select.html).

A few bugs have also been resolved, error messages have been improved, and more information has been added to the readme
regarding search wildcards.

### Changes

* New server interface to search database
* `order`, `limit` and `offset` parameters for database search commands
* More detailed exceptions for command errors
* More information regarding wildcards in readme

### Fixes

* Fix incorrect error message when passing an unknown database command
* Fix error caused by the options arguments parser

## 3.5.4

A new stop option has been added to the download update command to modify the number of submissions after which the
program stops looking through a user's folder. The database update from 2.7 to 3 has been upgraded and now files are
found directly in the submission folder.

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

The new `database search-journals` command allows searching journals by author, title, date and content. The old
submissions search command is now called `search-submissions`.

The help message and readme have been fixed and missing information has been added.

The output of the `download users` command has been generalised, so it does not use "submissions" even when downloading
journals; uses "items" instead.

### Changes

* Add database command to search journals

### Fixes

* Fix missing information in help message and readme
* Fix output of download users command not being generalised

## 3.4.0

The program now uses [FAAPI](https://gitlab.com/MatteoCampinoti94/FAAPI) version 2.7.3, which supports downloading users
journals. The database has been updated to version 3.2.0 to support this change with a new `JOURNALS` table and
a `JOURNALS` field in the `USERS` table. Journals can be downloaded with the `download users` command as any other
folder (gallery, scraps, etc...) or with the `download journals` command by supplying journal ID's. Journals can also be
added manually using the `database add-journal` command. A corresponding `database remove-journals` has also been added.

The previous `database manual-entry` command has been changed to `database add-submission`.

A few errors in the readme have also been solved.

### Changes

* Database version 3.2.0
    * Add `JOURNALS` table
    * Add `JOURNALS` field in the `USERS` table
* Download users' journals

### Fixes

* Fix readme errors

### Dependencies

* Update faapi dependency to [2.7.3](https://pypi.org/project/faapi/1.0.0)

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

Database version has been updated to 3.1.0; the "extras" folder has been renamed "mentions". Order of submissions ID's
is maintained when downloading single submissions.

### Fixes

* Maintain order of submission ID's when downloading single submissions

### Changes

* Database updated to 3.1.0
    * Extras renamed to mentions

## 3.2.5

### Fixes

* Fix output bug when downloading single submissions

## 3.2.4

Fixes a bug that causing tiered paths to overlap if the submission ID ended with zeroes.

### Fixes

* Tiered path for submissions ID's ended with zeroes

## 3.2.3

Order of users and folders passed to download users/update is maintained. Submissions already in the database but not in
user entry are not downloaded again.

### Fixes

* Maintain order of users and folders passed to download
* Do not download submissions again if already present in submissions table

## 3.2.2

Submissions titles are now cleaned of non-ASCII characters before printing them to screen. Non-ASCII characters would
break the spacing of the download output.

### Fixes

* Fix output of submissions titles with non-ASCII characters breaking spacing

## 3.2.1

Fix old database having the wrong version in the name when backing it after updating from version 2.7.0.

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

Exceptions raised during database updates are caught and any pending changes are committed before the exception is
raised again.

### Changes

* Safely commit and close when catching exceptions during database updates

## 3.1.7

The memory usage of database select (i.e. read) operations has been reduced by
using [sqlite3 cursors](https://docs.python.org/3/library/sqlite3.html#cursor-objects) instead of lists. The speed of
the database update function has been greatly improved by reducing database commits to one every 10000 processed
entries (1000 for the users table).

### Changes

* Database select operations return sqlite3 cursors to reduce memory usage
* Database update speed increased by reducing the number of commits

## 3.1.6

Fixes an output error in the database update function and improves the way settings and statistics are written in the
database, using UPDATE instead of INSERT OR REPLACE

### Fixes

* Database update output error
* Settings are updated instead of inserted

## 3.1.5

Improve database update function by saving the ID's of the submissions files that were not found during the transfer.

### Changes

* Save ID's of submissions not found during database update

## 3.1.4

### Dependencies

* Updated requirement [FAAPI](https://gitlab.com/MatteoCampinoti94/FAAPI) to version 2.6.0.

### Changes

* Use FAAPI 2.6.0

## 3.1.3

If the now unsupported "extras" folder is encountered during update, it now prints a warning and skips to the next.

### Changes

* Explicitly warn about extras folders

## 3.1.2

Fixed an IOError that happened when trying to pipe the database search output to a file.

### Fixes

* IOError when piping search results

## 3.1.1

Fix a version error. Database version was set to 3.1.0 instead of the program version.

### Fixes

* Fix versions

## 3.1.0

The database search command now allows to pass a parameter multiple times to act as OR values for the same field. The
readme has been slightly improved and some errors in it have been fixed.

### Fixes

* Readme typos and errors

### Changes

* Database search accepts OR parameters

## 3.0.3

This releases fixes counters not being updated in the new database when updating from version 2.7.

Under the hood changes include exporting the main console function so that the package can be imported and called with
arguments from other Python scripts.

Readme has also been improved with more information about issues and contributing.

### Fixes

* Database update function updates counters of new database

## 3.0.2

Small patch to fix a search bug and output the number of results found with search.

### Fixes

* Fix search crash when using description parameter

### Changes

* Output total number of results found by search

## 3.0.1

This release is only a minor fix to change the PyPi classifier for development status of the program from beta to
stable.

## 3.0.0 - All New and Improved

Release 3.0.0 marks a complete change in how the program is run, its capabilities and future development.

Following the change of interface on Fur Affinity in January 2020, version 2 stopped working, but with this new release
the tool can once again get content from FurAffinity and is much simpler to update to support future changes to FA's web
interface.

This change was achieved thanks to the FAAPI package (from the same author of
FALocalRepo [FAAPI@PyPi.org](https://pypi.org/project/faapi)). All scraping functions are now independent of the
interface, allowing for much quicker development and response to changes in the Fur Affinity website.

The interface of the program was changed from an interactive menu to a command line tool. This allows for much quicker
execution of commands, simpler code and automation via shell scripts.

The database has been updated and is now over 50% lighter for large numbers of downloaded submissions. Furthermore, it
now holds the cookies used by the scraper, reducing the program footprint.

All database functions have been completely overhauled and are now _considerably_ faster, especially searching. Using a
500k submissions table and a modern SSD drive, searching for a specific tag takes 0,90s on average, and searching for a
string in the descriptions takes only 1,30s. Time may vary depending on search parameters and drive speed.

The last big change regards the packaging and distribution of the program. falocalrepo is now a PyPi package, easily
installed with a single pip command. All dependencies have also been packaged and distributed on PyPi and are handled
without the need for git submodules. The new distribution method allows running falocalrepo in any folder, without the
need to have the program itself stored with the database.

### Changes

* Use FAAPI package to separate scraper development from interface
* Support for new FA's interface
* Menu interface replaced with a command line tool
* Database cleanup
* Cookies stored in database
* Database queries improvements
* Command line help
* Distribution via PyPi

### Dependencies

* Set FAAPI dependency to [2.5.0](https://pypi.org/project/FAAPI/2.5.0)

### Distribution

* [falocalrepo on PyPi.org](https://pypi.org/project/falocalrepo/)

## 2.10.2

Reduced the number of indexes created and made the whole process safer. Also, interruption is now available during
indexing.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.10.1

Extras' `e` option has been changed to search for ':iconusername:' and ':usernameicon:' only in the descriptions as
searching in keywords caused too many false positives in case the username was a common word/phrase.

Extras' `E` options has been changed to search 'username' in submissions' titles too.

A new 'warning' log type has been added for errors and exceptions. These will be saved in the log file regardless of
other settings. The log also has a new column for the type of log event: 'N', 'V', or 'W'

A small output error was also fixed.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.10

Thanks to a special Python module created by yours truly, Windows users can now enjoy the program with safe interruption
support. The module can be found on GitHub
&rarr; [SignalBlock](https://github.com/MatteoCampinoti94/PythonSignalBlocking-CrossPlatform).<br>
More information on the feature can be found in the README.

A new function has been added to the program to correctly detect version differences as the old method was causing
errors with some versions.

New log events have been added for SIGINT (CTRL-C interruption) detection and database version.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.9

Added logging to the program if launched with '--log' or '--logv' as argument (the latter logs ALL operations, thus the
v of verbose). Log is saved in a file named 'FA.log' and is trimmed to the last 10000 lines at each program start.

A new  'slow' option has been added to the download/update sections to throttle speed even further down by adding a
delay of 1,5 seconds between submissions downloads.

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

Unforeseen errors are now caught and displayed without being too verbose. To display errors normally the program can be
run with the option '--debug'.

An important bug has been fixed in the repair section. A missing return was breaking the INFOS table repair.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7.4

Fixed an error in the URL used to search extras. An OR was missing and would stop some results from showing up.

Users selected for download/update are now properly sorted.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.7.3

The search URL has been modified to avoid false positives by specifically searching only the description and keywords.
The default search employed by FA looks for search terms inside submissions filenames as well, and it could cause false
positives.

Unforeseen errors are now caught by the main script and their information displayed before exiting the program.

The header describing the various columns during download/update now reflects the new status output introduced
with [v2.7](https://github.com/MatteoCampinoti94/FALocalRepo/releases/tag/v2.7) and fixed
in [v2.7.1](https://github.com/MatteoCampinoti94/FALocalRepo/releases/tag/v2.7.1).

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

Download and update status output has been overhauled. The current operation is now showed in a small bracketed area at
the right end of the terminal screen. A progress bar is also shown when the submission file is downloaded (not all files
support this).

A new INDEX entry has been added to the INFOS table, it is used to save the update status of the indexes used in the
search function. Its values are either '0' if they are not up-to-date or '1' if they are.

Together with the new INDEX entry a new 'noindex' option has been added to the download/update section. If passed then
the program will not rebuild indexes after the download/update operation is completed and will set the INDEX entry to '
0' if new submissions where downloaded.

A few things have been improved around the program and some bugs removed.

PS: Linux release is once again bigger than it should. Will work on finding a more permanent fix.

**Warning**: Binaries are for 64bit systems only

## 2.6

Submissions descriptions are now saved in the database together with the submissions' data.

Search has been updated to work with the new description field, so it is now possible to search descriptions both
offline in the database and online with the web search.<br>
Case sensitivity can now be turned on/off with 'case' option in both normal and regex mode (but not online).<br>
Indexes have been added to quicken the search.

User entries have been slightly altered too: `NAME` column was changed to `USER` and `NAMEFULL` to `USERFULL`.

Repair has been improved with a new menu and a section dedicated to the `INFOS` table as well as shortcuts to optimize
the database or re-index it.

Upgrade functions have also been improved with lower memory usage.

Bugs have been fixed throughout the whole program.

PS: Linux binary size issue seems to be fixed for now.

Update 2018/05/02: Linux binary was compiled with an error, it is fixed now

**Warning**: Binaries are for 64bit systems only

## 2.5

The program is now capable of running searches on the main website. If no results can be found in the local database the
user will be automatically asked if they want to perform the search online instead.

A new 'options' field in the search menu allows enabling regex syntax and to search the website directly.

Local search can now match multiple users. For example if there are users 'tiger' and 'liger' in the database using '
iger' in the user field will match both of them.

Search output has also been improved.

A few more bugs have been squashed and some functions redesigned.

PS: I have no idea why but this release for Linux is over twice the size of previous ones. Will work on fixing it.

**Warning**: Binaries are for 64bit systems only

## 2.4

The search has been completely rewritten and should now be a lot faster. It is also now possible to search inside
specific sections of a user.<br>
Regex support has been disabled for now as it was hard to use and slowed the search down for everyone. A future update
will add an option to use regex.

A few small bugs have been fixed.

PS: I have no idea why but this release for Linux is over twice the size of previous ones. Will work on fixing it.

**Warning**: Binaries are for 64bit systems only

## 2.3

From this release the USERS table will also contain the "full" version of a user's nickname.<br>
In earlier versions user 'Tiger_Artist' would be saved only as 'tigerartist', the username used as url on the website.
However, from now on the USERS table will also contain the original name chosen by the user in a new column called '
NAMEFULL'.

The database version has been bumped up to 2.3 as well.

A few bugs have been squashed and some functions have been improved.

PS: I have no idea why but this release for Linux is over twice the size of previous ones. Will work on fixing it.

**Warning**: Binaries are for 64bit systems only

## 2.2

This new release is only a minor upgrade.

A new function has been added to check the cookies file for common errors in case a session cannot be created.

The cookies file has also been renamed to `FA.cookies.json` so that it can be opened properly as a json file for
editing. The program will take care of renaming the file.

Uncaught exceptions have also been taken care of when loading the cookies file.

Latest updates in the program used for reading keystrokes and text have also been included in these latest binaries.

PS: I have no idea why but this release for Linux is over twice the size of the previous one. Will work on fixing it for
the next release.

**Warning**: Binaries are for 64bit systems only

## 2.1

With this release all bugs with the users' database are fixed and the information are properly stored and saved.

The repair function has been expanded to include the users table. Repeating users, empty ones, names with capital
letters and/or underscores and empty sections/folders fields will be automatically corrected by the program.

A big number of bugs have been fixed as well, for the full list see
the [commits](https://github.com/MatteoCampinoti94/FALocalRepo/compare/v2.0.1...bdea9c2).

**Warning**: Binaries are for 64bit systems only

## 2.0.1

Fixed a bug in the update functions.

**Warning**: Binaries are for 64bit systems only

## 2.0

Big update and main version bump.

The program now also saves category, species, gender and rating of downloaded submissions. These can also be used during
search.

Format of the on-screen output has been completely changed for downloads and updates.

Databases can now be upgraded from earlier versions. Files from previous versions are backed up during the upgrade
process. Submissions that are no longer present on the forum will be saved with default, generalized values.

The new favorites page on the forum can now be handled correctly.

**Warning**: Binaries are for 64bit systems only

## 1.5.1

CTRL-C and CTRL-D can now be used to return to the main menu from input fields (e.g. username/sections/options)

Various small fixes

**Extra**: My gpg key was mistakenly deleted, thus all previous verified commits now show up as unverified.<br>
This new release is now verified

**Warning**: Binaries are for 64bit systems only

## 1.5

This new version comes with the usual fixes and a whole new menu entry to analyze the database and repair it. More
information in the readme.

**Warning**: Binaries are for 64bit systems only

## 1.4

The program now has a GUI! It is very simple and console-based, only a prototype of the planned one.

Search has also been added with its own menu entry, submissions can be searched for author, title and tags with regex
support.

Version has been bumped up to 1.4 skipping 1.3 due to the two major additions.

**Warning**: Binaries are for 64bit systems only

## 1.2.1

Small fix to make sure the infos table has the database name value created empty, to ensure compatibility with planned
gui.

Other changes are under-the-hood: moved some functions around and into modules to improve clarity and modularity.

**Warning**: Binaries are for 64bit systems only

## 1.2

Filetype detection now works reliably across Windows and Unix platforms!
Unfortunately safe exit still doesn't work reliably on Windows, so it's still disabled on it.

A new information table has been added to the database which stores:

* name of the database (for use in future versions)
* number of users
* number of submission
* time of last update start, in seconds since epoch
* duration of last update in seconds
* time of last download start, in seconds since epoch
* duration of last download in seconds

The table is created with all values reset to 0 in case it is not present, so it's perfectly compatible with older
versions.

**Warning**: Binaries are for 64bit systems only

## 1.1.2

The program can now be run on Windows as well!

Unfortunately due to missing libraries on Windows automatic filetype management and safe exit do NOT work so be careful.

**Warning**: Binaries are for 64bit systems only

## 1.1.1

The readme is now complete and contains all the instructions needed to use the program

Fixed a small bug in the sync code when using the Force option

A small search script has been added in the FA_tools folder

**Warning**: binary is for Linux 64bit only

## 1.1

Main change is usage of [cfscrape](https://github.com/Anorov/cloudflare-scrape) to bypass cloudflare wait at first
request

Improved printout & printout for checks

If a user was disabled gallery, scraps and favorites are disabled in the database as well and only extras are downloaded
if passed in sections

Better placement of interrupts for safe manual exit

General bugfixes

**Warning**: binary is for Linux 64bit only

## 1.0

Program now works and handles special cases

Exit codes for various events

Can interrupt at any moment using CTRL-C, exits safely

Needs cookies files

**Warning**: binary is for Linux 64bit only
