from app.lib.data_center import DataCenter


data_src = DataCenter()


def query_statement(statement, connection, **kwargs):
    session = data_src.get_session(connection, **kwargs)
    return data_src, session.execute(statement)


def internal_connection(connection, **kwargs):
    return data_src.get_session(connection, **kwargs)

