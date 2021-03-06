from __future__ import unicode_literals

from flask_login import LoginManager
from os import environ
from app.report.src.model_registry import ModelRegistry
from app.src.flask_extended import Flask

app = Flask(__name__, instance_relative_config=True)


# Load default user
app.config.from_object('app.default_config.DevelopmentConfig')

# Load the configuration from the instance folder
app.config.from_pyfile('app.cfg', silent=True)
if not app.debug:
    app.config.from_yaml('clients.yml', silent=True)


# Get a model/session registry
if not app.debug or environ.get('WERKZEUG_RUN_MAIN') == 'true':
    import shutil
    from os.path import join, isdir
    whoosh_dir = join(app.config['BASEDIR'], 'tmp/whoosh/sla_report')
    if isdir(whoosh_dir):
        shutil.rmtree(whoosh_dir)       # fresh index from whoosh prevents errors


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
        'Package failure',
        credentials
    )

    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('app/tmp/{package}.log'.format(package=app.config['PACKAGE_NAME']), 'a', 1 * 1024 * 1024, 10)
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
from . import view
from app.report.views import search, report, index, builder

app.register_blueprint(index.mod)
app.register_blueprint(report.mod)
app.register_blueprint(search.mod)
app.register_blueprint(builder.mod)
