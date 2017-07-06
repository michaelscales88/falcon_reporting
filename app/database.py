from redpanda.orm import sessionmaker
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session

from app import app
from app.report.models import _Base, Timestamp

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base(cls=(_Base, Timestamp))
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


def rebase():
    Base.metadata.create_all(bind=engine)
