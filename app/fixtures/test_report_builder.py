from pandas import DataFrame
from sqlalchemy import func


from app.fixtures.base_test import BaseTest
from app.lib.call_center import CallCenter
from app.lib.report_builder import ReportBuilder
from app.lib.sla_cache import cache
from app.lib.sla_report import report


class ReportBuilderTest(BaseTest):

    def setUp(self):
        super().setUp()
        # need to use the test_db connection and internal connection
        self.test_conn_1 = CallCenter  # Simulated db connection one
        self.test_conn_2 = CallCenter  # Simulated db connection two

    def test_manual_report(self):
        # Report builder should be able to connect to multiple data pts
        with ReportBuilderTest.app.app_context():
            records = CallCenter().example(
                ReportBuilderTest.app.test_date,
                list(ReportBuilderTest.app.config['CLIENTS'])
            )
            name = 'sla_report'
            ReportBuilderTest.app.data_src.insert_records(name, records)
            record_set = ReportBuilderTest.app.data_src.get_records(
                'sla_report', filter=func.date(ReportBuilderTest.app.test_date)
            )
            # for record in record_set:
            #     print(record.start_time, type(record.start_time))
            test_report = report(cache(record_set, pk='call_id', subkey='event_id'))
            test_report.name = str(ReportBuilderTest.app.test_date.date())
            test_report_rownames = test_report.rownames
            test_report_content = test_report.to_dict()
            # TODO 3: This should likely be its own 'pyexcel' model or something of the like
            data = DataFrame.from_items(
                [col for col in test_report_content.items()]
            )
            data.index = test_report_rownames
            print(data)
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

