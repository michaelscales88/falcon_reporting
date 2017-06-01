from sqlalchemy import Column, String, Integer
from sqlalchemy_utils import Timestamp
from functools import wraps


from sqlalchemy.ext.declarative import declarative_base


# Base = declarative_base()


class BaseMixin(object):
    id = Column(Integer, primary_key=True)


# def apply_mixins(cls):                        # not working
#     @wraps(cls)
#     def wrapper(*args, **kwds):               # ideally this allows me to pass defaults within a scope
#         default = kwds.get('defaults', {})
#         for name, value in default.items():
#             setattr(cls, name, value)
#         return cls
#
#     return wrapper

def apply_mixins(cls):                          # this works
    defaults = {
        'string': Column('string', String(20)),
        'integer': Column('integer', Integer())
    }
    for name, value in defaults.items():        # bind as class attributes before inst
        setattr(cls, name, value)
    return cls


def add_default(cls, name, defaults):           # attempt to add defaults and push/pop
    setattr(cls, name, defaults)
    return cls


@apply_mixins
class SomeMixin(object):
    pass


Base = declarative_base(cls=BaseMixin)


def test():
    table_info = {
        '__tablename__': 'sla_report',
        '__table_args__': {
            'autoload': False
        }
    }
    defaults = {
        'string': Column('string', String(20)),
        'integer': Column('integer', Integer())
    }
    obj = type('Sample', (Base, SomeMixin), table_info)                 # this works
    # obj = type('Sample', (Base, SomeMixin(defaults)), table_info)     # this doesn't
    print(obj)
    print(obj.__base__)
    print(obj.__tablename__)
    print(obj.__table_args__)
    print(obj.__table__.c.keys())
    print(obj, dir(obj))


if __name__ == '__main__':
    test()
