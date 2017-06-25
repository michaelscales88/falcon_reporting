import flask_excel as excel


class SaveWidget(object):

    def __init__(self, query_set, column_names):
        self.data = query_set
        self.columns = column_names

    def save(self):
        return excel.make_response_from_query_sets(self.data, self.columns, "xlsx")
