from redpanda.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session

from app import app
from app.report.models.base import _Base, Timestamp
from app.report.src.model_registry import ModelRegistry

# This will record declarative models
model_registry = ModelRegistry()

# Rather than using sqlalchemy's default db
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base(cls=(_Base, Timestamp))
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
    

def rebase():
    Base.metadata.create_all(bind=engine)
