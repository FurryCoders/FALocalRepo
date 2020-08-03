from json import load as json_load
from os import chdir
from os.path import abspath
from os.path import dirname
from typing import Dict
from typing import List

from fa import main

if __name__ == '__main__':
    # Switch to master file directory
    workdir: str = dirname(abspath(__file__))
    chdir(workdir)

    # Read cookies
    cookies: List[Dict[str, str]]
    with open("FA.cookies.json", "r") as f:
        cookies = [
            {"name": c["name"], "value": c["value"]}
            for c in json_load(f)
            if c["name"] in ("a", "b")
        ]
    assert len(cookies) == 2

    # Pass directory and cookies to main
    main(workdir, cookies)
