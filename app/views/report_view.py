from flask import render_template, g, Blueprint, current_app, request, jsonify
from pandas import DataFrame
from sqlalchemy import func
import flask_excel as excel


from app.lib.sla_cache import cache
from app.lib.sla_report import report

mod = Blueprint('reports', __name__, template_folder='templates')


@mod.route("/report/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        return jsonify({"result": request.get_array(field_name='file')})
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (csv, tsv, csvz, tsvz only)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''


@mod.route("/report/download", methods=['GET'])
def download_file():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")


@mod.route("/report/export", methods=['GET'])
def export_records():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv", file_name="export_data")


@mod.route('/report/')
@mod.route('/report')
def report_page():
    return render_template(
        'report_viewer.html',
    )


# TODO this is ripe for flask-excel extension for upload/download: http://flask-excel.readthedocs.io/en/latest/
# TODO 2: Sheet.save_to_database(session, table[, ...])	Save data in sheet to database table
# # TODO https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html
@mod.route('/report/run/')
@mod.route('/report/run')
def run_report():
    # df = pd.read_sql(query.statement, query.session.bind)  # this may be the way to read dataframes
    # pd.read_sql(session.query(Complaint).filter(Complaint.id == 2).statement,session.bind)
    # use this https://github.com/amancevice/redpanda/blob/master/notebooks/python35/notebook.ipynb redpandas
    # need to have custom models before this will work though
    # record_set = g.db.query(FlexibleStorage).order_by(FlexibleStorage.id).filter((func.date(current_app.test_date)).all()
    record_set = current_app.data_src.get_records('sla_report', filter=func.date(current_app.test_date))
    test_report = report(cache(record_set, pk='call_id', subkey='event_id'), list(current_app.config['CLIENTS']))
    test_report.name = str(current_app.test_date.date())
    test_report_rownames = test_report.rownames
    test_report_content = test_report.to_dict()
    # TODO 3: This should likely be its own 'pyexcel' model or something of the like
    data = DataFrame.from_items(
        [col for col in test_report_content.items()]
    )
    data.index = test_report_rownames
    return display_report(tables=[data.to_html(classes='report')],
                          titles=['na', test_report.name])


def display_report(**kwargs):
    return render_template(
        'report_viewer.html',
        **kwargs
    )
