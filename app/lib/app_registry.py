from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.models.custom_model import model_factory
from app.lib.query_decoder import QueryDecoder


class SessionRegistry(object):
    _registry = {}

    def get(self, url, **kwargs):
        if url not in self._registry:
            mapped_cls = kwargs.pop('cls', None)    # get the custom mapped class
            engine = create_engine(url, **kwargs)
            if mapped_cls:
                mapped_cls.metadata.create_all(engine)  # This creates the declarative base tables
            session_factory = sessionmaker(bind=engine)
            Session = scoped_session(session_factory)
            self._registry[url] = Session
        return self._registry[url]


class ModelRegistry(object):
    _registry = {}
    _decoder = QueryDecoder()

    def get(self, table_name, records, **kwargs):
        if table_name not in self._registry:
            model = self._decoder.decode_result(table_name, records)
            self._registry[table_name] = model
        return self._registry[table_name]

    def __getitem__(self, table_name):
        return self._registry[table_name] if table_name in self._registry.keys() else None
