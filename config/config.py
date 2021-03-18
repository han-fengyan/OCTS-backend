import os


BASE_DIR = os.path.abspath(os.getcwd())

DEBUG = bool(os.environ.get('DEBUG', None))

SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' \
                          % (os.path.join(BASE_DIR, 'sqlite.db'),)
SQLALCHEMY_TRACK_MODIFICATIONS = False

