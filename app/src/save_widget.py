from flask import redirect, url_for
import flask_excel as excel


class SaveWidget(object):

    def __init__(self, data_set):
        self.data = data_set

    def save(self):
        print('save')
        # return redirect(url_for('save', data_set=self.data))
        return excel.make_response_from_records(self.data, 'xlsx')
