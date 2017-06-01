from sqlalchemy import Column, String, Integer
from sqlalchemy_utils import Timestamp


from sqlalchemy.ext.declarative import declarative_base


class BaseMixin(object):
    id = Column(Integer, primary_key=True)


def apply_mixins(cls, attribs):
    for name, value in attribs.items():        # bind as class attributes before inst
        setattr(cls, name, value)
    return cls


class MixedModel(object):
    pass


Base = declarative_base(cls=BaseMixin)


def test():
    table_info = {
        '__tablename__': 'sla_report',
        '__table_args__': {
            'autoload': False
        }
    }
    columns = {
        'string': Column('string', String(20)),
        'integer': Column('integer', Integer())
    }
    my_mixin = apply_mixins(MixedModel, columns)
    obj = type('Sample', (Base, my_mixin), table_info)                 # this works
    print(obj)
    print(obj.__base__)
    print(obj.__tablename__)
    print(obj.__table_args__)
    print(obj.__table__.c.keys())
    print(obj, dir(obj))


if __name__ == '__main__':
    test()
