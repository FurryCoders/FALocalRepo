if __name__ == "__main__":
    from .main import main
    from os import getcwd
    from os.path import abspath

    main(abspath(getcwd()))
