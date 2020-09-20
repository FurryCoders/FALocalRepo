from sys import argv, exit

from .console import MalformedCommand
from .console import UnknownCommand
from .console import main_console


def main():
    # Run main program
    try:
        main_console(argv)
    except KeyboardInterrupt:
        print()
        pass
    except (MalformedCommand, UnknownCommand) as err:
        print(repr(err))
        exit(1)
    except ModuleNotFoundError as err:
        print(repr(err))
        exit(2)


if __name__ == "__main__":
    main()
