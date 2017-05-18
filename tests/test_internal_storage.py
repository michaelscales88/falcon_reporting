from datetime import datetime, timedelta
from sqlalchemy import func

from falcon_reporting.src.factory import query_statement, internal_connection
from falcon_reporting.lib.report_utilities import ReportUtilities
from falcon_reporting.lib.flexible_storage import SlaStorage
from falcon_reporting.lib.flexible_storage import MyEncoder

_connection = 'postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall'


def cache(data_src_records, pk, subkey):
    cached_events = {}
    for record in data_src_records:
        key = record.pop(pk)  # Connect to c_call table
        event_id = record.pop(subkey)  # Organize events
        cached_event = cached_events.get(
            key,
            {  # This could be a configobj from AppSettings "Call Template"
                'Start Time': None,  # MIN time
                'End Time': None,  # MAX time
                'Unique Id1': None,  # Hunt Group from c_call table
                'Unique Id2': None,  # Hunt Group from c_call table
                'Events': {},
                'Event Summary': {}
            }
        )

        # Unique ID from query
        if not cached_event['Unique Id1']:  # Set if none
            cached_event['Unique Id1'] = record['dialed_party_number']

        if not cached_event['Unique Id2']:  # Set if none
            cached_event['Unique Id2'] = record['calling_party_number']

        # MIN start time
        if not cached_event['Start Time']:  # Set if none
            cached_event['Start Time'] = record['start_time']
        elif cached_event['Start Time'] > record['start_time']:  # or with a new lowest start_time
            cached_event['Start Time'] = record['start_time']

        # MAX end time
        if not cached_event['End Time']:  # Set if none
            cached_event['End Time'] = record['end_time']
        elif cached_event['End Time'] < record['end_time']:  # or with a new highest end_time
            cached_event['End Time'] = record['end_time']

        cached_event['Events'][event_id] = record  # Preserve event order / Serialization breaks

        # Create a summary of the event_types
        event_accum = cached_event['Event Summary'].get(
            record['event_type'],
            timedelta(0)
        )
        event_accum += record['end_time'] - record['start_time']
        cached_event['Event Summary'][record['event_type']] = event_accum

        cached_events[key] = cached_event

    return cached_events


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

    src, result = query_statement(statement, _connection)  # Make a connection to the PG dB and execute the query
    data_src_records = [dict(zip(row.keys(), row)) for row in result]
    print('got data src records')
    cached_records = cache(data_src_records, pk='call_id', subkey='event_id')
    print('cached records')
    session = internal_connection('sqlite:///:memory:')
    print('got internal connection')
    for pk, call_data_dict in cached_records.items():
        call_data = SlaStorage(
            id=pk,
            start=call_data_dict.pop('Start Time'),
            end=call_data_dict.pop('End Time'),
            unique_id1=call_data_dict.pop('Unique Id1'),
            unique_id2=call_data_dict.pop('Unique Id2'),
            data=call_data_dict
        )
        session.add(call_data)
    session.commit()
    print('stored cached events')
    for row in session.query(SlaStorage).filter(func.date(query_date)).all():
        print(row.id)
        print(src.print_record(row.data, cls=MyEncoder, indent=4))


if __name__ == '__main__':
    from sys import argv

    test(ReportUtilities.valid_dt(argv[1]) if len(argv) > 1 else datetime.today().date())
