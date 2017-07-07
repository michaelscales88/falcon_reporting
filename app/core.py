from datetime import datetime
from urllib.parse import urlparse, urljoin

import flask_excel as excel
# from app.models.base import Base
from app.report.src.call_center import CallCenter
from flask import g, flash, redirect, url_for, abort, request
from pandas import DataFrame, read_sql
from sqlalchemy import func

from app import app
from app.database import rebase
from app.report.models.custom_model import model_factory
from app.report.src.query_decoder import QueryDecoder

# Query decoder identifies metadata about an incoming table/subtable
decoder = QueryDecoder()


# def populate_model():
#     model_registry = getattr(app, 'model_registry', None)
#     if model_registry:
#         model_registry.init_register(Base, db.engine)
#
#
# def print_register():
#     model_registry = getattr(app, 'model_registry', None)
#     if model_registry:
#         model_registry.print_register(Base, db.engine)


def get_connection(date):
    print(app.config['CLIENTS'])
    return CallCenter.example(
        date,
        app.config['CLIENTS']
    )


def get_count(query):
    if query:
        count_q = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_q).scalar()
    else:
        count = 0
    return count


def query_model(model_name, report_date, page, per_page):
    model_registry = getattr(g, 'model_registry', None)
    query = None
    if model_registry and model_registry[model_name]:
        model = model_registry[model_name]
        query = model.query

        if page is None:
            page = 1

        if per_page is None:
            per_page = 20

        offset = (page - 1) * per_page

        if report_date:
            query = query.filter(func.date(report_date))

        if offset > 0:  # only need to offset if we need more than one page?
            query = query.offset(offset)

        if per_page > 0:
            query = query.limit(per_page)

    return query


def insert_records(session, model_name, records):
    model_registry = getattr(g, 'model_registry', None)
    if not model_registry or not model_registry[model_name]:
        name, columns, table_info = decoder.decode_result(model_name, records)  # analyze records to determine col type
        model = model_factory(name, columns, table_info)  # make custom model
        model.metadata.create_all(g.session.bind)  # Make schema and bind to engine
        model_registry[model_name] = model  # save it for later
        decoder.model_info(model)

    model = model_registry[model_name]
    rebase()    # this could be saved for changes only
    records = [convert_to_unicode(record) for record in records]

    if app.config['ENABLE_SEARCH']:
        from app import si
        si.register_class(model)

    for record in records:
        session.add(model(**record))
    session.commit()
    flash(
        'Added {number} records to {model_name}'.format(
            number=len(records),
            model_name=model_name
        )
    )


# def rebase():
#     Base.metadata.create_all(db.engine)


def convert_to_unicode(dictionary):
    """Converts dictionary values to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    encoded_dict = {}
    for k, v in dictionary.items():
        if is_encodable(v):
            encoded_dict[k] = repr(v)
        else:
            encoded_dict[k] = v
    return encoded_dict


def is_encodable(v):
    if isinstance(v, datetime):
        return False
    else:
        return True


def save(frame, file_name, fmt="xlsx"):
    if isinstance(frame, DataFrame):
        if not file_name:
            file_name = frame.name if frame.name else 'default_frame'
        return excel.make_response_from_records(
            frame.to_dict(orient='records'),
            file_name=file_name,
            file_type=fmt
        )


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
        else:
            return abort(400)


def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )


def get_frame(query, name='Default Frame'):
    if query:
        df = read_sql(query.statement, query.session.bind)
    else:
        df = DataFrame()
    df.name = name
    return df
