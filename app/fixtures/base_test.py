from unittest import TestCase

from app import app


class BaseTest(TestCase):
    """ TestCase classes that want to be parametrized should
            inherit from this class.
    """
    app = app

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        # Make connections available to Fixtures
        # self.internal_connection = internal_connection
        # self.query_statement = query_statement
        # self.example_data_src = CallCenter

    def setUp(self):
        # Set up test configuration
        app.config.from_object('app.default_config.DevelopmentConfig')

    def tearDown(self):
        # Break down db connections
        pass

# TODO reading to extend Fixtures
# http://pythontesting.net/framework/unittest/unittest-fixtures/
# https://github.com/croach/Flask-Fixtures

