from os import getcwd
from os.path import join
from sqlite3 import DatabaseError
from sqlite3 import IntegrityError
from sys import argv
from sys import exit
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
        print(repr(err))
        exit(1)
    except MultipleInstances as err:
        print(repr(err))
        exit(2)
    except ConnectionError as err:
        print(repr(err))
        exit(3)
    except (DatabaseError, IntegrityError) as err:
        print(repr(err))
        exit(4)
    except (TypeError, AssertionError) as err:
        print(repr(err))
        exit(5)
    except (Exception, BaseException) as err:
        with open(join(getcwd(), "FA.log"), "w") as f:
            print_exc(file=f)
            print(repr(err))
            print(f"Trace written to {f.name}")
        exit(6)


if __name__ == "__main__":
    main()
