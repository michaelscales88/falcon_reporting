from datetime import datetime


from falcon_reporting.src.factory import query_statement
from falcon_reporting.lib.report_utilities import ReportUtilities

_connection = 'postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall'


def test(query_date):
    statement = '''
    Select Distinct c_call.call_id, c_call.dialed_party_number, c_call.calling_party_number, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''.format(date=str(query_date))

    src, result = query_statement(statement, _connection)   # Make a connection to the PG dB and execute the query
    data_src_records = [dict(zip(row.keys(), row)) for row in result]

    for record in data_src_records:
        print(src.print_record(record))

if __name__ == '__main__':
    from sys import argv

    test(ReportUtilities.valid_dt(argv[1]) if len(argv) > 1 else datetime.today().date())
