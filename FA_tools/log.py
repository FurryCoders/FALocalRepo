import os, sys
from datetime import datetime
import FA_var as favar


class log:
    _normal = "--log" in sys.argv[1:] or "--logv" in sys.argv[1:]
    _verbose = "--logv" in sys.argv[1:]
    _file = "FA.log"

    @classmethod
    def log_start(cls):
        if not cls._normal:
            return
        with open(cls._file, "a") as logf:
            logf.write("*" * 44 + "\n")

    @classmethod
    def log_trim(cls, lines=10000):
        if not cls._normal or not os.path.isfile(cls._file):
            return

        with open(cls._file, "r") as logf:
            logl = logf.readlines()

        if len(logl) <= lines:
            return

        with open(cls._file, "w") as logf:
            for l in logl[-lines:]:
                logf.write(l)

    @classmethod
    def normal(cls, data=""):
        if not cls._normal:
            return
        with open(cls._file, "a") as logf:
            time = str(datetime.now())
            if type(data) in (list, tuple):
                for d in data:
                    logf.write(f"{time} | N | {d}\n")
            else:
                logf.write(f"{time} | N | {data}\n")

    @classmethod
    def verbose(cls, data=""):
        if not cls._verbose:
            return
        with open(cls._file, "a") as logf:
            time = str(datetime.now())
            if type(data) in (list, tuple):
                for d in data:
                    logf.write(f"{time} | V | {d}\n")
            else:
                logf.write(f"{time} | V | {data}\n")

    @classmethod
    def warning(cls, data=""):
        with open(cls._file, "a") as logf:
            time = str(datetime.now())
            if type(data) in (list, tuple):
                for d in data:
                    logf.write(f"{time} | W | {d}\n")
            else:
                logf.write(f"{time} | W | {data}\n")
