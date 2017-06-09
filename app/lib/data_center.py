from flask import current_app
from sqlalchemy.orm import class_mapper, ColumnProperty
from pandas import DataFrame


from app.lib.app_registry import SessionRegistry
from app.lib.app_registry import ModelRegistry


def attribute_names(cls):
    return [prop.key for prop in class_mapper(cls).iterate_properties
            if isinstance(prop, ColumnProperty)]


class DataCenter(object):

    def __init__(self):
        self._session_registry = SessionRegistry()
        self._model_registry = ModelRegistry()

    def model(self, table_name):
        return self._model_registry[table_name]

    def get_session(self, target, **kwargs):
        return self._session_registry.get(target, **kwargs)

    def get_model(self, target, records, **kwargs):
        return self._model_registry.get(target, records, **kwargs)

    def insert_records(self, table_name, records, **kwargs):
        model = self.get_model(table_name, records, **kwargs)
        # print(attribute_names(model))
        conn = self.get_session(
            current_app.config['SQLALCHEMY_DATABASE_URI'],
            echo=current_app.config['SQLALCHEMY_ECHO'],
            cls=model
        )
        for row in records:
            modeled_data = model(**row)
            # print([(qc, type(qc)) for qc in modeled_data.columns])
            conn.add(modeled_data)
        conn.commit()

    def get_records(self, table_name, **kwargs):
        model = self.model(table_name)
        # for c in model.__table__.columns:
        #     print(c)
        if model:
            conn = self.get_session(
                current_app.config['SQLALCHEMY_DATABASE_URI'],
                echo=current_app.config['SQLALCHEMY_ECHO'],
                cls=model
            )
            ids = kwargs.get('ids', [])
            filters = kwargs.get('filter', None)
            offset = kwargs.get('offset', None)
            per_page = kwargs.get('per_page', None)
            if ids:
                query = conn.query(model).order_by(model.id).filter(model.id.in_(ids)).limit(per_page).offset(offset).all()
            elif filters is not None:
                query = conn.query(model).order_by(model.id).filter(filters).all()
            elif offset and per_page:
                query = conn.query(model).order_by(model.id).limit(per_page).offset(offset).all()
            else:
                query = conn.query(model).order_by(model.id).all()
            return [rec for rec in query]
        else:
            return []

    def record_count(self, table_name):
        model = self.model(table_name)
        if model:
            conn = self.get_session(
                current_app.config['SQLALCHEMY_DATABASE_URI'],
                echo=current_app.config['SQLALCHEMY_ECHO'],
                cls=model
            )
            return conn.query(model).count()
        else:
            return 0

    def get_frame(self, table_name, **kwargs):
        model = self.model(table_name)
        if model:
            conn = self.get_session(
                current_app.config['SQLALCHEMY_DATABASE_URI'],
                echo=current_app.config['SQLALCHEMY_ECHO'],
                cls=model
            )
            ids = kwargs.get('ids', [])
            offset = kwargs.get('offset', None)
            filters = kwargs.get('filter', None)
            per_page = kwargs.get('per_page', None)
            if ids:
                query = conn.query(model).order_by(model.id).filter(model.id.in_(ids)).limit(per_page).offset(offset)
            elif filters is not None:
                query = conn.query(model).order_by(model.id).filter(filters)
            elif offset and per_page:
                query = conn.query(model).order_by(model.id.asc()).limit(per_page).offset(offset)
            else:
                query = conn.query(model).order_by(model.id)
            return query.frame()
        else:
            return DataFrame()

    def page_view(self, table_name, **kwargs):
        model = self.model(table_name)
        if model:
            conn = self.get_session(
                current_app.config['SQLALCHEMY_DATABASE_URI'],
                echo=current_app.config['SQLALCHEMY_ECHO'],
                cls=model
            )
            offset = kwargs.get('offset', 0)
            per_page = kwargs.get('per_page', 10)
            if offset > 0:
                print('inside offset > 0')
                query = conn.query(model).order_by(model.id.asc()).offset(offset).limit(per_page)
            else:
                print('inside offset 0')
                query = conn.query(model).order_by(model.id.asc()).limit(per_page)
            return query.frame()
        else:
            return DataFrame()
