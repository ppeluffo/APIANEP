#!/home/pablo/Spymovil/python/proyectos/APIANEP/venv/bin/python3

"""
Este script lo corro cuando uso por ej. sqlite.
Si uso una postgres en un contenedor, la inicialización de BD y creación
de las tablas la hago en un script de inicio del contenedor.
"""

import anep_db.db as db
from anep_db.dbmodels import Datos, ControAcceso

if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    print('BD Creada !!')

