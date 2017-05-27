from platform import system

if system() in ('Darwin', 'Linux'):
    from app.fixtures.base_test import BaseTest
else:
    from falcon_reporting.app.fixtures.base_test import BaseTest


class ReportBuilderTest(BaseTest):

    def setUp(self):
        super().setUp()
        pass

    def test_1(self):
        self.assertTrue(True)

