from declarative_models.flexible_storage import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class SessionRegistry(object):
    _registry = {}

    def get(self, url, **kwargs):
        if url not in self._registry:
            engine = create_engine(url, **kwargs)
            Session = sessionmaker(bind=engine)
            Base.prepare(engine)
            Base.metadata.createall()
            session = scoped_session(Session)
            self._registry[url] = session
        return self._registry[url]
