from datetime import datetime, timedelta
from sqlalchemy import String, TypeDecorator
from json import loads, dumps, JSONEncoder
from decimal import Decimal
from dateutil import parser


from falcon_reporting.app.lib.report_utilities import ReportUtilities


CONVERTERS = {
    'datetime': parser.parse,
    'decimal': Decimal,
    'timedelta': ReportUtilities.to_td
}


class MyEncoder(JSONEncoder):
    """Convert non-serializable data into a value which we can store in our dB"""
    def default(self, obj):
        if isinstance(obj, (datetime,)):
            return {"val": obj.isoformat(), "_spec_type": "datetime"}
        elif isinstance(obj, (Decimal,)):
            return {"val": str(obj), "_spec_type": "decimal"}
        elif isinstance(obj, (timedelta,)):
            return {"val": str(obj), "_spec_type": "timedelta"}
        else:
            return super().default(obj)


def object_hook(obj):
    """Convert json data from its serialized value"""
    _spec_type = obj.get('_spec_type')
    if not _spec_type:
        return obj

    if _spec_type in CONVERTERS:
        return CONVERTERS[_spec_type](obj['val'])
    else:
        raise Exception('Unknown {}'.format(_spec_type))


class JsonEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = String

    def process_bind_param(self, value, dialect):
        return dumps(value, cls=MyEncoder)

    def process_result_value(self, value, dialect):
        return loads(value, object_hook=object_hook)