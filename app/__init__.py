from __future__ import unicode_literals
# app/__init__.py
# https://gist.github.com/mattupstate/2046115: extended flask with yaml support

from app.lib.flask_extended import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, g, Blueprint

from flask_restful import Api
from datetime import datetime
from sqlalchemy.exc import OperationalError
from os.path import join


# from app.lib.data_center import DataCenter
# from app.src.factory import internal_connection, run_logger
# from app.models.flexible_storage import FlexibleStorage
# from app.resources.index_resource import IndexView

app = Flask(__name__, instance_relative_config=True)

# Load default settings
app.config.from_object('app.default_config.DevelopmentConfig')

# Load the configuration from the instance folder
app.config.from_pyfile('app.cfg', silent=True)
app.config.from_yaml('clients.yml', silent=True)

# Connection to db
db = SQLAlchemy(app)

# api = Api(app=app)
# api_bp = Blueprint('api', __name__)


# Looks like a name issue when entering unittest the __name__ is falcon.app instead of whatever it wants
# with app.app_context():
    # call set up functions which need to bind to app
    # try:
    #     run_logger(__name__)
    # except FileNotFoundError:
    #     print('failed to open logger')


"""
Remove after testing.
"""
# app.test_date = datetime.today().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0)
# app.config['TEST_STATEMENT'] = app.config['TEST_STATEMENT'].format(date=str(app.test_date.date()))
# app.data_src = DataCenter()     # Holds session registry, metadata, etc -> needs to have a model registry


# @app.before_request
# def before_request():
#     # Set up our dB connection
#     model = app.data_src.model('sla_report')
#     if model:
#         g.db = internal_connection(
#             app.config['SQLALCHEMY_DATABASE_URI'],
#             echo=app.config['SQLALCHEMY_ECHO'],
#             cls=model
#         )
#
#
# @app.teardown_request
# def teardown(error):
#     db = getattr(g, 'db', None)
#     if db:
#         db.remove()     # Close scoped session
#
#
# @app.errorhandler(OperationalError)     # Give this it's own page eventually
# @app.errorhandler(404)
# def not_found(error):
#     return render_template('404.html'), 404
#
#
# from app.views import index
# from app.views import insert
# from app.views import report
# from app.views import builder
#
#
# app.register_blueprint(index.mod)
# app.register_blueprint(insert.mod)
# app.register_blueprint(report.mod)
# app.register_blueprint(builder.mod)
#
#
# api.add_resource(IndexView, '/df/<int:offset>/<int:per_page>')
# app.register_blueprint(api_bp)
#
# # read the SO below -> modify views and how they're being rendered
# # https://stackoverflow.com/questions/15501518/dynamic-navigation-in-flask/15525226#15525226
# # TODO extending blueprints: http://flask.pocoo.org/docs/0.12/patterns/appfactories/