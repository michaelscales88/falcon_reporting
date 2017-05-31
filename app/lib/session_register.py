from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class SessionRegistry(object):
    _registry = {}

    def get(self, url, **kwargs):
        """
        
        :param url: 
        :param kwargs: 
        :return: 
        """
        if url not in self._registry:
            mapped_cls = kwargs.pop('cls', None)    # get the custom mapped class
            engine = create_engine(url, **kwargs)
            if mapped_cls:
                mapped_cls.metadata.create_all(engine)  # This creates the declarative base tables
            session_factory = sessionmaker(bind=engine)
            Session = scoped_session(session_factory)
            self._registry[url] = Session
        return self._registry[url]

