from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import defaultdict

from app.lib.data_center import DataCenter


def test(query_date):
    pk = 'call_id'
    subkey = 'event_id'
    engine = create_engine('postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall')

    # dc = DataCenter()
    meta = MetaData()
    Session = sessionmaker(bind=engine)
    meta.reflect(bind=engine)
    session = Session()

    statement = '''
    Select Distinct c_call.call_id, c_call.dialed_party_number, c_call.calling_party_number, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''.format(date=str(query_date))

    result = session.execute(statement)
    data_src_records = [dict(zip(row.keys(), row)) for row in result]
    # for table in reversed(meta.sorted_tables):
    #     print(table)

    cached_events = {}
    for record in data_src_records:
        key = record.pop(pk)            # Connect to c_call table
        event_id = record.pop(subkey)   # Organize events
        cached_event = cached_events.get(
            key,
            # {   # This could be a configobj from AppSettings "Call Template"
            #     'Answered': False,                  # Answered occurs in the call ID
            #     'Talking Duration': timedelta(0),
            #     'Start Time': None,                 # MIN time
            #     'End Time': None,                   # MAX time
            #     'Voicemail': False,                 # This needs a time check as well
            #     'Calling Party': None,              # Calling Party @ "ringing" event
            #     'Receiving Party': None,            # Receiving Party @ "ringing" event
            #     'Call Group': None                  # Hunt Group from c_call table
            # }
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
        if not cached_event['Start Time']:   # Set if none
            cached_event['Start Time'] = record['start_time']
        elif cached_event['Start Time'] > record['start_time']:  # or with a new lowest start_time
            cached_event['Start Time'] = record['start_time']

        # MAX end time
        if not cached_event['End Time']:     # Set if none
            cached_event['End Time'] = record['end_time']
        elif cached_event['End Time'] < record['end_time']:      # or with a new highest end_time
            cached_event['End Time'] = record['end_time']

        cached_event['Events'][event_id] = record                # Preserve event order / Serialization breaks

        # Create a summary of the event_types
        event_accum = cached_event['Event Summary'].get(
            record['event_type'],
            timedelta(0)
        )
        event_accum += record['end_time'] - record['start_time']
        cached_event['Event Summary'][record['event_type']] = event_accum

        cached_events[key] = cached_event

    return cached_events


if __name__ == '__main__':
    test(query_date='2017-05-01')
