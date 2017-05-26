import unittest
from falcon_reporting.app import app


class BaseTest(unittest.TestCase):
    app = app

    def setUp(self):
        # Set up test configuration
        app.config.from_object('falcon_reporting.app.test_config.TestConfig')

    def tearDown(self):
        # Break down db connections
        pass

# TODO reading to extend Fixtures
# http://pythontesting.net/framework/unittest/unittest-fixtures/
# https://github.com/croach/Flask-Fixtures