from sqlalchemy import func
from flask import g

from app import app
from app.src.call_center import CallCenter
from app.src.query_decoder import QueryDecoder

from app.models.custom_model import model_factory

decoder = QueryDecoder()


def get_connection(date):
    return CallCenter.example(
        date,
        app.config['CLIENTS']
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

    for record in records:
        model = model_registry[model_name]
        session.add(model(**record))
        session.commit()
