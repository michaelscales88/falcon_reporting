from flask import redirect, url_for


class SaveWidget(object):

    def __init__(self, query_set, column_names):
        self.data = query_set
        self.columns = column_names

    def save(self):
        return redirect(url_for('save', data_set=self.data, column_names=self.columns))
