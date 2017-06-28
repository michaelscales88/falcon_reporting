import os


class Config(object):
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.urandom(24)     # Generate a random session key

    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Turn this off to reduce overhead

    # pagination
    POSTS_PER_PAGE = 50

    # indexing service
    WHOOSH_BASE = os.path.join(BASEDIR, 'tmp/whoosh')
    ENABLE_SEARCH = True

    # email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # administrator list
    ADMINS = ['your-gmail-username@gmail.com']

    # Set external connections
    EXTERNAL_CONNECTION = None


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    WIPE_SESSION = True
    MAX_RECORDS = 3000
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Turn this off to reduce overhead


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + ':memory:'
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
