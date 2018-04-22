import sqlite3
from .v1v2 import db_upgrade_v1v2
from .v2v2_3 import db_upgrade_v2v2_3

def db_upgrade_main():
    while True:
        db = sqlite3.connect('FA.db')

        infos = db.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()
        if infos != [('SUBMISSIONS',), ('USERS',), ('INFOS',)]:
            db.close()
            return

        infos_f = db.execute('SELECT field FROM infos').fetchall()
        infos_v = db.execute('SELECT value FROM infos').fetchall()
        db.close()

        infos_f = [f[0] for f in infos_f]
        infos_v = [v[0] for v in infos_v]

        db_upgrade = False

        if 'VERSION' not in infos_f:
            db_upgrade = db_upgrade_v1v2
        else:
            version = infos_v[infos_f.index('VERSION')]
            if version < '2.3':
                db_upgrade = db_upgrade_v2v2_3


        if db_upgrade:
            print('-'*20)
            print('Database version upgrade')
            print('-'*20)
            print()
            db_upgrade()
            print()
        else:
            break
