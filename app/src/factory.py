import logging
from logging.handlers import RotatingFileHandler
from flask_paginate import Pagination
from flask import current_app, request
from sqlalchemy import Column, String, Integer


from app.models.custom_model import get_model


def manifest_reader(manifest=None):
    # Test Values
    read_manifest = {
        'REPORT_NAME': 'SLA Report',
        'HEADERS': [
            'I/C Presented',
            'I/C Answered',
            'I/C Lost',
            'Voice Mails',
            'Incoming Answered (%)',
            'Incoming Lost (%)',
            'Average Incoming Duration',
            'Average Wait Answered',
            'Average Wait Lost',
            'Calls Ans Within 15',
            'Calls Ans Within 30',
            'Calls Ans Within 45',
            'Calls Ans Within 60',
            'Calls Ans Within 999',
            'Call Ans + 999',
            'Longest Waiting Answered',
            'PCA'
        ],
        'BEHAVIORS': {
            'I/C Presented': 'Sum',
            'I/C Answered': 'Sum',
            'I/C Lost': 'Sum',
            'Voice Mails': 'Sum',
            'Incoming Answered (%)': 'Percentage',
            'Incoming Lost (%)': 'Percentage',
            'Average Incoming Duration': 'Average',
            'Average Wait Answered': 'Average',
            'Average Wait Lost': 'Average',
            'Calls Ans Within 15': 'Sum',
            'Calls Ans Within 30': 'Sum',
            'Calls Ans Within 45': 'Sum',
            'Calls Ans Within 60': 'Sum',
            'Calls Ans Within 999': 'Sum',
            'Call Ans + 999': 'Sum',
            'Longest Waiting Answered': 'Max/Min',
            'PCA': 'Percentage'
        },
        'CONDITIONS': {
            'I/C Presented': 'Sum',
            'I/C Answered': 'Sum',
            'I/C Lost': 'Sum',
            'Voice Mails': 'Sum',
            'Incoming Answered (%)': 'Percentage',
            'Incoming Lost (%)': 'Percentage',
            'Average Incoming Duration': 'Average',
            'Average Wait Answered': 'Average',
            'Average Wait Lost': 'Average',
            'Calls Ans Within 15': 'Sum',
            'Calls Ans Within 30': 'Sum',
            'Calls Ans Within 45': 'Sum',
            'Calls Ans Within 60': 'Sum',
            'Calls Ans Within 999': 'Sum',
            'Call Ans + 999': 'Sum',
            'Longest Waiting Answered': 'Max/Min',
            'PCA': 'Percentage'
        },
        'SUMMARIZE': True,
    }
    return read_manifest


def run_logger(app_name):
    try:
        # Configure logger
        LOG_FILE_NAME = 'app/logs/{application}.log'.format(application=app_name)
        handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=10000, backupCount=5)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        current_app.logger.addHandler(handler)

        # Include emitted Werkzeug messages in our log file
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)

    except FileNotFoundError:
        from os import path, makedirs
        if not path.exists("logs/"):
            makedirs("logs/", exist_ok=True)

        # Configure logger
        LOG_FILE_NAME = 'app/logs/{application}.log'.format(application=app_name)
        handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=10000, backupCount=5)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        current_app.logger.addHandler(handler)

        # Include emitted Werkzeug messages in our log file
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)


def model_factory(meta_data=None, columns=None):
    table_info = {
        '__tablename__': 'sla_report',
        '__table_args__': {
            'autoload': False
        }
    }
    columns = {
        'string': Column('string', String(20)),
        'integer': Column('integer', Integer())
    }
    return get_model('Sample', columns, table_info)


def query_statement(statement, connection, **kwargs):
    session = current_app.data_src.get_session(connection, **kwargs)
    return current_app.data_src, session.execute(statement)


def internal_connection(connection, **kwargs):
    return current_app.data_src.get_session(connection, **kwargs)


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(
        css_framework=get_css_framework(),
        link_size=get_link_size(),
        show_single_page=show_single_page_or_not(),
        **kwargs
    )


def get_page_args():
    args = request.args.copy()
    args.update(request.view_args.copy())
    page_parameter = args.get('page_parameter', 'page')
    page = int(args.get(page_parameter, 1))
    per_page = args.get('per_page')
    if not per_page:
        per_page = current_app.config.get('PER_PAGE', 10)
    else:
        per_page = int(per_page)

    offset = (page - 1) * per_page
    return page, per_page, offset
