# app/test_config.py


class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + ':memory:'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + 'app/db/test.db'
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
