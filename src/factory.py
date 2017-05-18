from falcon_reporting.lib.data_center import DataCenter


def query_statement(statement, connection):
    data_src = DataCenter()
    session = data_src.make_session(connection)
    return data_src, session.execute(statement)


def internal_connection(connection):
    return DataCenter().make_session(connection)
