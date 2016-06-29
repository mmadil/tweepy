import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

DATABASE = 'database.db'
WTF_CSRD_ENABLED = True

# use something like os.urandom(24) for productional uses.
SECRET_KEY = 'my precious'

DATABASE_PATH = os.path.join(BASE_DIR, DATABASE)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = True
