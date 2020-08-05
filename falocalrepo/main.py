from datetime import datetime
from os import getcwd
from os.path import abspath
from os.path import join as path_join
from sys import argv

from .__version__ import __version__
from .console import main_console
from .database import Connection
from .database import connect_database
from .database import make_database
from .interactive import main_menu
from .settings import setting_write


def main():
    # Get current work directory
    workdir: str = abspath(getcwd())

    # Initialise and prepare database
    db: Connection = connect_database(path_join(workdir, "FA.db"))
    make_database(db)
    setting_write(db, "LASTSTART", str(datetime.now().timestamp()))
    setting_write(db, "VERSION", __version__)

    # Run main program
    if argv[1:] and argv[1] == "interactive":
        main_menu(workdir, db)
    else:
        main_console(workdir, db, argv)

    # Close database
    db.commit()
    db.close()
