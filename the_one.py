from app import db
from app.report.models import Base, User


def make_only_one(user_name, **kwargs):
    Base.metadata.create_all(db.engine)

    uu = User.query.all()
    # sometimes there can be only one
    for u in uu:
        db.session.delete(u)
    db.session.commit()

    u = User(nickname=user_name, email='{name}@admin.com'.format(name=user_name), **kwargs)
    db.session.add(u)
    db.session.commit()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--name')   # name for our user
    parser.add_argument('--kwarg')  # one test keyword for the user table
    args = parser.parse_args()
    name = args.name
    kwarg = args.kwarg.split('=')
    kwarg = {kwarg[0]: kwarg[1]}
    make_only_one(name, **kwarg)

