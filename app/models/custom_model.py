from app.models.base import Base


def apply_mixins(cls, column_data):
    for name, value in column_data.items():             # bind as class attributes before inst
        setattr(cls, name, value)
    return cls


class MixedModel(object):
    pass


def model_factory(name, columns, table_info):
    my_mixin = apply_mixins(MixedModel, columns)        # get a mixed model with correct column types
    return type(name, (Base, my_mixin), table_info)     # return Model object
