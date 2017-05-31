from sqlalchemy import Column, String, Integer
from sqlalchemy_utils import Timestamp


from sqlalchemy.ext.declarative import declarative_base


# Base = declarative_base()


class BaseMixin(object):
    id = Column(Integer, primary_key=True)


def apply_mixins(cls):
    # defaults = {
    #     'string': Column('string', String(20)),
    #     'integer': Column('integer', Integer())
    # }
    defaults = {}
    print(cls, dir(cls))
    # # delattr(cls, "bar")
    for name, value in defaults.items():
        setattr(cls, name, value)
    return cls


def add_default(cls, name, defaults):
    setattr(cls, name, defaults)
    return cls


@apply_mixins
class SomeMixin(object):
    pass


Base = declarative_base(cls=BaseMixin)


def test():
    table_info = {'__tablename__': 'sla_report',
                  '__table_args__': {'autoload': False}, }
    defaults = {
        'string': Column('string', String(20)),
        'integer': Column('integer', Integer())
    }
    obj = type('Sample', (Base, add_default(SomeMixin, 'defaults', defaults)), table_info)
    # obj = type('Sample', (Base, SomeMixin), table_info)
    print(obj)
    print(obj.__base__)
    print(obj.__tablename__)
    print(obj.__table_args__)
    print(obj.__table__.c.keys())
    print(obj, dir(obj))

if __name__ == '__main__':
    test()
