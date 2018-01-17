# FALocalRepo
Pure Python script to download any user's gallery/scraps/favorites and more from FurAffinity forum in an easily handled database.

**Warning**: A cookie file named FA.cookies in json format is needed.<br>
**Warning**: At the moment the script does NOT work on Windows because of how Windows handles signals, specifically SIGINT which is intercepted to exit the script safely.

## Usage
Run `FA.py` with Python 3.x or create a binary.

1. `Insert username: `<br>
First field is reserved for users. To download or sync a specific user/s insert the username (url or userpage name are both valid)

2. `Insert sections: `<br>
Second field is reserved for sections. These can be:
  * g - Gallery
  * s - Scraps
  * f - Favorites
  * e - Extras partial<br>
  Searches submissions that contain ':iconusername:' OR ':usernameicon:' in the description AND NOT from username gallery/scraps
  * E - Extras full<br>
  Like partial but also searches for 'username' in the descriptions

3. `Insert options: `<br>
Last field is reserved for options. These can be:
  * Y - Sync<br>
  Stops download when a submission already present in the user database entry is encountered
  * U - Update<br>
  Reads usernames from the database and downloads new submissions in the respective sections. This option can be used without specifying a users or sections, if either is specified then the uodatewill belimited to those user/s and/or section/s.
  * F - Force<br>
  Prevents update and sync from stopping download at the first already present submission. Download stops at the first downloaded submission from page 3 included
  * A - All<br>
  Like 'F' but it will prevent interrupting download for the whole section (this means **ALL** pages from each user will be checked, only use for a limited ammount of users)

## Cookies
The script needs to use cookies from a login session to successfully connect to FA. These cookies need to be in json format and can be easily extracted from Firefox/Chrome/Opera/Vivaldi/etc... using extensions or  manually. The value must be wirtten in a file named FA.cookies<br>
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
