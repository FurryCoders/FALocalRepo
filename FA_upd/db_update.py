import sqlite3
from .v1v2 import db_update_v1v2

def db_update():
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

    if 'VERSION' not in infos_f:
        db_update_v1v2()
    else:
        version = infos_v[infos_f.index('VERSION')]
        if version == '2.0':
            return
