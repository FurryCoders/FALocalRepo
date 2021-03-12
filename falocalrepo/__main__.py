from os import environ
from os import getcwd
from os.path import join
from sqlite3 import DatabaseError
from sqlite3 import IntegrityError
from sys import argv
from sys import exit
from sys import stderr
from traceback import print_exc

from .console import MalformedCommand
from .console import MultipleInstances
from .console import UnknownCommand
from .console import console


def main():
    try:
        console(*filter(bool, map(str.strip, argv[1:])))
    except KeyboardInterrupt:
        print()
        exit(130)
    except (MalformedCommand, UnknownCommand) as err:
        print_exc(file=stderr) if environ.get("FALOCALREPO_DEBUG", None) is not None else None
        print(repr(err), file=stderr)
        exit(1)
    except MultipleInstances as err:
        print_exc(file=stderr) if environ.get("FALOCALREPO_DEBUG", None) is not None else None
        print(repr(err), file=stderr)
        exit(2)
    except ConnectionError as err:
        print_exc(file=stderr) if environ.get("FALOCALREPO_DEBUG", None) is not None else None
        print(repr(err), file=stderr)
        exit(3)
    except (DatabaseError, IntegrityError) as err:
        print_exc(file=stderr) if environ.get("FALOCALREPO_DEBUG", None) is not None else None
        print(repr(err), file=stderr)
        exit(4)
    except (TypeError, AssertionError) as err:
        print_exc(file=stderr) if environ.get("FALOCALREPO_DEBUG", None) is not None else None
        print(repr(err), file=stderr)
        exit(5)
    except (Exception, BaseException) as err:
        print_exc(file=stderr) if environ.get("FALOCALREPO_DEBUG", None) is not None else None
        with open(join(getcwd(), "FA.log"), "w") as f:
            print_exc(file=f)
            print(repr(err), file=stderr)
            print(f"Trace written to {f.name}", file=stderr)
        exit(6)


if __name__ == "__main__":
    main()
