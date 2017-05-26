# app/__init__.py
# https://gist.github.com/mattupstate/2046115: extended flask with yaml support
from __future__ import unicode_literals

from flask import render_template, g
from datetime import datetime
from sqlalchemy.exc import OperationalError
from os.path import join

from app.lib.flask_extended import Flask
from app.src.factory import internal_connection
from app.models.flexible_storage import FlexibleStorage

app = Flask(__name__)
app.config.from_pyfile('settings/app.cfg')
app.config.from_yaml(join(app.root_path, 'settings/clients.yml'))
# app.debug = config.DEBUG
# app.secret_key = config.SECRET_KEY

"""
Remove after testing.
"""
app.test_date = datetime.today().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0)
app.config['TEST_STATEMENT'] = app.config['TEST_STATEMENT'].format(date=str(app.test_date.date()))


@app.before_request
def before_request():
    # Set up our dB connection
    g.db = internal_connection(
        app.config['SQLALCHEMY_DATABASE_URI'],
        echo=app.config['SQLALCHEMY_ECHO'],
        cls=FlexibleStorage
    )


@app.teardown_request
def teardown(error):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.errorhandler(OperationalError)     # Give this it's own page eventually
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


from app.views import index
from app.views import records
from app.views import insert
from app.views import reports


app.register_blueprint(index.mod)
app.register_blueprint(records.mod)
app.register_blueprint(insert.mod)
app.register_blueprint(reports.mod)

# TODO extending blueprints: http://flask.pocoo.org/docs/0.12/patterns/appfactories/