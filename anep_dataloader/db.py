from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

PGSQL_HOST = os.environ.get('PGSQL_HOST','192.168.0.18')
#PGSQL_HOST = os.environ.get('PGSQL_HOST','127.0.0.1')
PGSQL_PORT = os.environ.get('PGSQL_PORT', '5433')
PGSQL_USER = os.environ.get('PGSQL_USER', 'admin')
PGSQL_PASSWD = os.environ.get('PGSQL_PASSWD','pexco599')
PGSQL_BD = os.environ.get('PGSQL_BD', 'bd_anep')

BD_URL = f'postgresql+psycopg2://{PGSQL_USER}:{PGSQL_PASSWD}@{PGSQL_HOST}:{PGSQL_PORT}/{PGSQL_BD}'
# BD_URL = 'sqlite:///anep.sqlite'

engine = create_engine(url=BD_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()
