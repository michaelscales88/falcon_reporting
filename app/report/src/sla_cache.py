from datetime import timedelta
from dateutil.parser import parse


def cache(data_src_records, pk, subkey):
    cached_events = {}
    for record in data_src_records:
        key = getattr(record, pk)  # Connect to c_call table
        event_id = getattr(record, subkey)  # Organize events
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
            cached_event['Unique Id1'] = getattr(record, 'dialed_party_number')

        if not cached_event['Unique Id2']:  # Set if none
            cached_event['Unique Id2'] = getattr(record, 'calling_party_number')

        # MIN start time
        if not cached_event['Start Time']:  # Set if none
            cached_event['Start Time'] = getattr(record, 'start_time')
        elif cached_event['Start Time'] > getattr(record, 'start_time'):  # or with a new lowest start_time
            cached_event['Start Time'] = getattr(record, 'start_time')

        # MAX end time
        if not cached_event['End Time']:  # Set if none
            cached_event['End Time'] = getattr(record, 'end_time')
        elif cached_event['End Time'] < getattr(record, 'end_time'):  # or with a new highest end_time
            cached_event['End Time'] = getattr(record, 'end_time')

        cached_event['Events'][event_id] = record  # Preserve event order / Serialization breaks

        # Create a summary of the event_types
        event_accum = cached_event['Event Summary'].get(
            getattr(record, 'event_type'),
            timedelta(0)
        )
        try:
            event_accum += getattr(record, 'end_time') - getattr(record, 'start_time')
        except TypeError:
            pass
            # print(record['end_time'], type(record['end_time']))
            # print(record['start_time'], type(record['start_time']))
        cached_event['Event Summary'][getattr(record, 'event_type')] = event_accum
        # print(cached_event['Start Time'], type(cached_event['Start Time']))
        cached_events[key] = cached_event
    # print([values['Event Summary'].keys() for cache, values in cached_events.items()])
    # print([values['Event Summary'].get(4, None) for cache, values in cached_events.items()])
    return cached_events
