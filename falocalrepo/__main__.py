from sys import argv

from .console import CommandError
from .console import main_console


def main():
    # Run main program
    try:
        main_console(argv)
    except KeyboardInterrupt:
        print()
        pass
    except CommandError as err:
        print(repr(err))


if __name__ == "__main__":
    main()
