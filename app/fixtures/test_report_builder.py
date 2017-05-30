from platform import system

if system() in ('Darwin', 'Linux'):
    from app.fixtures.base_test import BaseTest
    from app.src.factory import internal_connection
    from app.models.flexible_storage import FlexibleStorage
    from app.lib.call_center import CallCenter
    from app.lib.report_builder import ReportBuilder
else:
    from falcon_reporting.app.fixtures.base_test import BaseTest
    from falcon_reporting.app.src.factory import query_statement, internal_connection
    from falcon_reporting.app.models.flexible_storage import FlexibleStorage
    from falcon_reporting.app.lib.call_center import CallCenter
    from falcon_reporting.app.lib.report_builder import ReportBuilder


class ReportBuilderTest(BaseTest):

    def setUp(self):
        super().setUp()
        # need to use the test_db connection and internal connection
        self.test_conn_1 = CallCenter  # Simulated db connection one
        self.test_conn_2 = CallCenter  # Simulated db connection two

    def test_connections(self):
        # Report builder should be able to connect to multiple data pts
        # with ReportBuilderTest.app.app_context():
        #     self.test_conn_1(
        #         ReportBuilderTest.app.config['TEST_STATEMENT'],
        #         ReportBuilderTest.app.config['EXTERNAL_CONNECTION']
        #     )
        #     self.test_conn_2(
        #         ReportBuilderTest.app.config['SQLALCHEMY_DATABASE_URI'],
        #         echo=ReportBuilderTest.app.config['SQLALCHEMY_ECHO'],
        #         cls=FlexibleStorage
        #     )
        self.assertTrue(True)

    def test_cache(self):
        # A custom cache view and model needs to store the results of the raw sql
        self.assertTrue(True)

    def test_report(self):
        # Using the cached data we can build reports from our models
        self.report = ReportBuilder()
        self.assertTrue(True)

    def test_validate(self):
        # This may or may not be required
        self.assertTrue(True)

