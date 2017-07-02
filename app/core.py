from sqlalchemy import func
from flask import g, flash, redirect, url_for
from datetime import datetime
import flask_excel as excel
from pandas import DataFrame

from app import app, db
from app.src.call_center import CallCenter
from app.src.query_decoder import QueryDecoder

from app.models import Base
from app.models.custom_model import model_factory

decoder = QueryDecoder()


def get_connection(date):
    print(app.config['CLIENTS'])
    return CallCenter.example(
        date,
        app.config['CLIENTS']  # if app.config.get('CLIENTS', None) else ['Torie', 'Sean', 'Susan', 'Debbie']
    )


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


def query_model(model_name, report_date, page, per_page):
    model_registry = getattr(g, 'model_registry', None)
    query = offset = total = None
    if model_registry and model_registry[model_name]:
        model = model_registry[model_name]
        query = model.query
        total = get_count(query)

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

    return query, offset, total


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


def rebase():
    Base.metadata.create_all(db.engine)


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


def save(frame, fmt="xlsx"):
    if isinstance(frame, DataFrame):
        return excel.make_response_from_records(frame.to_dict(orient='records'), fmt)
