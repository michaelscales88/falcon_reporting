from unittest import TestCase, TestLoader, TestSuite
from click import command, option, pass_context


from falcon_reporting.app import app


class BaseTest(TestCase):
    """ TestCase classes that want to be parametrized should
            inherit from this class.
    """
    app = app

    # def __init__(self, methodName='runTest', params=None):
    #     super().__init__(methodName)
    #     self.param = params
    #
    # @staticmethod
    # def parametrize(testcase_klass, param=None):
    #     """ Create a suite containing all tests taken from the given
    #         subclass, passing them the parameter 'param'.
    #     """
    #     testloader = TestLoader()
    #     testnames = testloader.getTestCaseNames(testcase_klass)
    #     suite = TestSuite()
    #     for name in testnames:
    #         suite.addTest(testcase_klass(name, param=param))
    #     return suite

    def setUp(self):
        # Set up test configuration
        app.config.from_object('falcon_reporting.app.test_config.TestConfig')
        # app.config['DEBUG'] = self.param['DEBUG']
        # app.config['SQLALCHEMY_ECHO'] = self.param['ECHO']

    def tearDown(self):
        # Break down db connections
        pass

# TODO reading to extend Fixtures
# http://pythontesting.net/framework/unittest/unittest-fixtures/
# https://github.com/croach/Flask-Fixtures

