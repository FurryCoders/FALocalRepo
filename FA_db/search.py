import sqlite3
import re
import time, os, sys
import PythonRead as readkeys

def regexp(pattern, input):
    return bool(re.match(pattern, input, flags=re.IGNORECASE))

def search(DB, fields):
    DB.create_function("REGEXP", 2, regexp)

def main(DB):
    pass
