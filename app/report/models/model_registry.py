# from sqlalchemy.ext.automap import automap_base
from app.report.src.registry import Registry


class ModelRegistry(Registry):

    def __init__(self):
        self._needs_init = True

    @property
    def needs_init(self):
        return self._needs_init

    # Model registry holds metadata about db models
    def init_register(self, base, engine):
        print(base)
        print('init register')
        base.metadata.create_all(engine)
        for c in base._decl_class_registry.values():
            print(c)
        # Base = automap_base()
        # Base.prepare(engine, reflect=True)
        # for model in base.classes:
        #     print(model.__name__, '__searchable__' in dir(model))
        #     print(model.to_dict())
        #     if not model.__name__ == 'user':
        #         self._registry[model.__name__] = model
        self._needs_init = False

    def __getitem__(self, model_name):
        try:
            return self._registry[model_name]
        except KeyError:
            return None

    def __setitem__(self, model_name, model):
        print('setting register')
        self._registry[model_name] = model

    def print_register(self, base, engine):
        base.metadata.create_all(engine)
        for c in base._decl_class_registry.values():
            print(c)
