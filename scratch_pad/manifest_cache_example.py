from datetime import datetime
from json import dumps

from app.src.json_encoders import MyEncoder

from app import app
from app.report.src.factory import query_statement
from scratch_pad.manifest_example import manifest_reader

_connection = 'postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall'

statement = '''
Select Distinct c_call.call_id, c_call.dialed_party_number, c_call.calling_party_number, c_event.*
From c_event
    Inner Join c_call on c_event.call_id = c_call.call_id
where
    to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}' and
    c_call.call_direction = 1
Order by c_call.call_id, c_event.event_id
'''.format(date=str(datetime.today().date()))


class MyCondition(object):

    def __init__(self, column, default=None, condition=None):
        self._name = column
        self._value = default
        self._condition = condition

    @property
    def value(self):
        return self._value

    @property
    def condition(self):
        return self._condition

    @value.setter
    def value(self, new_value):
        if self.condition(new_value):
            self._value = new_value           # If the condition is met we can assign to _value

    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self._condition)


def make_column(columns):
    defaults = {}
    for column_index in sorted(columns.keys()):
        column_data = columns[column_index]
        column_name = column_data['COLUMN']
        default = column_data.get('DEFAULT', None)
        defaults[column_name] = MyCondition(column_name, default=default)
        # this might be condition=fn() with the value and condition built in
    return defaults


def make_cache(records=()):
    manifest = manifest_reader()
    cache_template = manifest['CACHE_TEMPLATE']
    pk = cache_template['KEYS']['PK']
    sub_key = cache_template['KEYS']['SUB_KEY']
    default = make_column(cache_template['COLUMNS'])
    # print(dumps(default, indent=4))
    print(default)
    cached_events = {}
    for record in records:
        key = record.pop(pk)  # Connect to c_call table
        event_id = record.pop(sub_key)  # Organize events
        cached_event = cached_events.get(
            key,
            default
        )
        print(cached_event)
        print(dumps(record, indent=4, cls=MyEncoder))
        break


if __name__ == '__main__':
    with app.app_context():
        src, result = query_statement(statement, _connection)  # Make a connection to the PG dB and execute the query
        data_src_records = [dict(zip(row.keys(), row)) for row in result]
        make_cache(data_src_records)
