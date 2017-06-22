from json import dumps

# from redpanda import create_engine
# from redpanda.orm import sessionmaker
# from sqlalchemy.orm import scoped_session

# from app.src.query_decoder import QueryDecoder
# from app.models.custom_model import model_factory


class Registry(object):

    _registry = {}

    def __repr__(self):
        return dumps(self._registry, indent=4, default=str)


# class SessionRegistry(Registry):
#     _registry = {}
#
#     def get(self, url, **kwargs):
#         if url not in self._registry:
#             mapped_cls = kwargs.pop('cls', None)        # get the custom mapped class
#             engine = create_engine(url, **kwargs)
#             if mapped_cls:
#                 mapped_cls.metadata.create_all(engine)  # This creates the declarative base tables
#             session_factory = sessionmaker(bind=engine)
#             Session = scoped_session(session_factory)
#             self._registry[url] = Session
#         return self._registry[url]


class ModelRegistry(Registry):

    def __getitem__(self, model_name):
        try:
            return self._registry[model_name]
        except KeyError:
            return None

    def __setitem__(self, model_name, model):
        self._registry[model_name] = model
