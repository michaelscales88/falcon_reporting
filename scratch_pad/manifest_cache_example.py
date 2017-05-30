from json import dumps

from falcon_reporting.scratch_pad.manifest_example import manifest_reader


def make_default(columns):
    defaults = {}
    for column_index in sorted(columns.keys()):
        column_data = columns[column_index]
        column_name = column_data['COLUMN']
        default = column_data.get('DEFAULT', None)
        defaults[column_name] = default
    return defaults


def make_cache(data_src_records=()):
    manifest = manifest_reader()
    cache_template = manifest['CACHE_TEMPLATE']
    pk = cache_template['KEYS']['PK']
    sub_key = cache_template['KEYS']['SUB_KEY']
    default = make_default(cache_template['COLUMNS'])
    print(dumps(default, indent=4))
    cached_events = {}
    for record in data_src_records:
        key = record.pop(pk)  # Connect to c_call table
        event_id = record.pop(sub_key)  # Organize events
        cached_event = cached_events.get(
            key,
            default
        )


if __name__ == '__main__':
    make_cache()
