from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.models.custom_model import get_model
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

    def get(self, url, **kwargs):
        if url not in self._registry:
            pass
            # columns, table_info
            # model = get_model('Test', columns, table_info)
            # self._registry[url] = model
        return self._registry[url]
