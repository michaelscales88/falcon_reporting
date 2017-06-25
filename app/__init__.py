from __future__ import unicode_literals
from os import environ
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.src.flask_extended import Flask
from app.src.app_registry import ModelRegistry


app = Flask(__name__, instance_relative_config=True)


# Load default settings
app.config.from_object('app.default_config.DevelopmentConfig')

# Load the configuration from the instance folder
app.config.from_pyfile('app.cfg', silent=True)
app.config.from_yaml('clients.yml', silent=True)

# Register api
# api = Api(app=app)
# api_bp = Blueprint('api', __name__)

# Connection to db
db = SQLAlchemy(app)

# Get a model/session registry
if not app.debug or environ.get('WERKZEUG_RUN_MAIN') == 'true':

    app.model_registry = ModelRegistry()


# Configure logger
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None

    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

    mail_handler = SMTPHandler(
        (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        'no-reply@' + app.config['MAIL_SERVER'],
        app.config['ADMINS'],
        'microblog failure',
        credentials
    )

    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('app/tmp/falcon_web.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('falcon startup')

# Start the index service
if app.config['ENABLE_SEARCH']:
    from whooshalchemy import IndexService
    si = IndexService(config=app.config)

# Configure login page
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


# Add views
from app.views import app_routing, index, report


app.register_blueprint(index.mod)
app.register_blueprint(report.mod)

# Add api resources
# api.add_resource(IndexView, '/df/<int:offset>/<int:per_page>')

# Register the api
# app.register_blueprint(api_bp)

