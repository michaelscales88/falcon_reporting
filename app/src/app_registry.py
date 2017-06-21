from json import dumps

from redpanda import create_engine
from redpanda.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from app.src.query_decoder import QueryDecoder


class Registry(object):

    _registry = {}

    def __repr__(self):
        return dumps(self._registry, indent=4, default=str)

    def __getitem__(self, item_in_reg):
        return self._registry[item_in_reg] if item_in_reg in self._registry.keys() else None  # can't use .get atm


class SessionRegistry(Registry):
    _registry = {}

    def get(self, url, **kwargs):
        if url not in self._registry:
            mapped_cls = kwargs.pop('cls', None)        # get the custom mapped class
            engine = create_engine(url, **kwargs)
            if mapped_cls:
                mapped_cls.metadata.create_all(engine)  # This creates the declarative base tables
            session_factory = sessionmaker(bind=engine)
            Session = scoped_session(session_factory)
            self._registry[url] = Session
        return self._registry[url]


class ModelRegistry(Registry):
    _registry = {}
    _decoder = QueryDecoder()

    def get(self, table_name, records, **kwargs):
        if table_name not in self._registry:
            model = self._decoder.decode_result(table_name, records)
            self._registry[table_name] = model
        return self._registry[table_name]

    # def __getitem__(self, item_in_reg):
    #     return self._registry[item_in_reg] if item_in_reg in self._registry.keys() else None  # can't use .get atm
