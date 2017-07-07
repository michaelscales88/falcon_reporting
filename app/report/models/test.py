from sqlalchemy import Column, Text, DateTime
from app.database import Base


class Test(Base):
    __searchable__ = ['id2', 'nickname']

    id2 = Column(Text, index=True, unique=True)
    nickname = Column(Text, index=True, unique=True)
    email = Column(Text, index=True, unique=True)
    about_me = Column(Text)
    last_seen = Column(DateTime)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def get(cls, id):
        try:
            return cls.query.get(id)
        except KeyError:
            return None

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname
