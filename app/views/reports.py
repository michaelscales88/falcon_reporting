from flask import render_template, g, Blueprint, current_app, request, jsonify
from pandas import DataFrame
from sqlalchemy import func
import flask_excel as excel


from app.models.custom_model import model_factory
from app.models.flexible_storage import FlexibleStorage
from app.src.factory import internal_connection
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
    record_set = g.db.query(FlexibleStorage).order_by(FlexibleStorage.id).filter(func.date(current_app.test_date)).all()
    test_report = report(record_set)
    test_report.name = str(current_app.test_date.date())
    test_report_rownames = test_report.rownames
    test_report_content = test_report.to_dict()
    # TODO 3: This should likely be its own 'pyexcel' model or something of the like
    data = DataFrame.from_items(
        [col for col in test_report_content.items()]
    )
    data.index = test_report_rownames
    # data.to_sql('sla_report', g.db, if_exists='replace')
    # test_model = custom_model('sla_report')  # This appears to be working. Need many more mixins
    # session = internal_connection(
    #     current_app.config['SQLALCHEMY_DATABASE_URI'],
    #     echo=current_app.config['SQLALCHEMY_ECHO'],
    #     cls=test_model
    # )
    # print(test_model.__table__.columns.keys())
    # for index, call_data_dict in enumerate(test_report_content.items()):
    #     call_data = test_model(
    #         id=index+1,
    #         start=call_data_dict.pop('Start Time'),
    #         end=call_data_dict.pop('End Time'),
    #         unique_id1=call_data_dict.pop('Unique Id1'),
    #         unique_id2=call_data_dict.pop('Unique Id2'),
    #         data=call_data_dict
    #     )
    #     session.add(call_data)
    # session.commit()
    # session.close()
    return display_report(tables=[data.to_html(classes='report')],
                          titles=['na', test_report.name])


@mod.route('/report/run2/')
@mod.route('/report/run2')
def run_report2():
    cached_records = cache(data_src_records, pk='call_id', subkey='event_id')
    return display_report(tables=[data.to_html(classes='report')],
                          titles=['na', test_report.name])


def display_report(**kwargs):
    return render_template(
        'report_viewer.html',
        **kwargs
    )
