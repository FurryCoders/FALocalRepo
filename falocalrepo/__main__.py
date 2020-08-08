from sys import argv

from .console import main_console


def main():
    # Run main program
    try:
        main_console(argv)
    except KeyboardInterrupt:
        print()
        pass
    except (Exception, BaseException) as err:
        print("\nERROR:", repr(err))


if __name__ == "__main__":
    main()
