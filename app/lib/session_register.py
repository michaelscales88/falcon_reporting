from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class SessionRegistry(object):
    _registry = {}

    def get(self, url, **kwargs):
        if url not in self._registry:
            mapped_cls = kwargs.pop('cls', None)
            engine = create_engine(url, **kwargs)
            if mapped_cls:
                mapped_cls.metadata.create_all(engine)
            session_factory = sessionmaker(bind=engine)
            session = scoped_session(session_factory)
            self._registry[url] = session
        return self._registry[url]

