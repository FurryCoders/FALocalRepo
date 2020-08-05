from datetime import datetime
from os import getcwd
from os.path import abspath
from os.path import join as path_join
from sys import argv

from .console import main_console
from .database import Connection
from .database import connect_database
from .database import make_database
from .interactive import main_menu
from .settings import setting_write


def main():
    # Initialise and prepare database
    db: Connection = connect_database(path_join(abspath(getcwd()), "FA.db"))
    make_database(db)
    setting_write(db, "LASTSTART", str(datetime.now().timestamp()))

    # Run main program
    if argv[1:] and argv[1] == "interactive":
        main_menu(db)
    else:
        main_console(db, argv)

    # Close database
    db.commit()
    db.close()
