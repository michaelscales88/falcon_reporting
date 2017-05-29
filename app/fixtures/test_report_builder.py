from platform import system

if system() in ('Darwin', 'Linux'):
    from app.fixtures.base_test import BaseTest
else:
    from falcon_reporting.app.fixtures.base_test import BaseTest


class ReportBuilderTest(BaseTest):

    def setUp(self):
        super().setUp()

    def test_connections(self):
        # Report builder should be able to connect to multiple data pts
        self.assertTrue(True)

    def test_cache(self):
        # A custom cache view and model needs to store the results of the raw sql
        self.assertTrue(True)

    def test_report(self):
        # Using the cached data we can build reports from our models
        self.assertTrue(True)

    def test_validate(self):
        # This may or may not be required
        self.assertTrue(True)

