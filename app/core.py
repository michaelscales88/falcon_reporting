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


def get_records(model_name):
    model_registry = getattr(app, 'model_registry', None)
    if model_registry and model_registry[model_name]:
        model = model_registry[model_name]
        print(model.query.all())
        return True
    return False


def insert_records(session, model_name, records):
    model_registry = getattr(app, 'model_registry', None)
    if not model_registry or not model_registry[model_name]:
        name, columns, table_info = decoder.decode_result(model_name, records)  # analyze records to determine col type
        model = model_factory(name, columns, table_info)                        # make custom model
        app.model_registry[model_name] = model                                  # save it for later
        decoder.model_info(model)

    for record in records:
        model = model_registry[model_name]
        session.add(model(**record))
        session.commit()
    print('claiming i added records')




