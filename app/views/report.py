import flask_excel as excel
from flask import render_template, Blueprint, g, redirect, url_for
from pandas import DataFrame
from flask_login import login_required

from app import app
from app.src.sla_cache import cache
from app.src.pandas_page import PandasPage
from app.core import query_model


from app.src.sla_report import sla_report


mod = Blueprint('report', __name__, template_folder='templates')


@mod.route('/')
@mod.route('/report', methods=['GET', 'POST'])
@mod.route('/report/<int:page>', methods=['GET', 'POST'])
@login_required
def report(page=1):
    query, offset, total = query_model('sla_report', g.report_date, 0, 0)

    if not query:
        return redirect(url_for('index.index'))

    cached_list = cache(query.all(), pk='call_id', subkey='event_id')
    test_report = sla_report(
        cached_list, 
        client_list=list(app.config['CLIENTS']) if app.config.get('CLIENTS', None) else ['Torie', 'Sean', 'Susan', 'Debbie']
    )
    
    test_report.name = str(g.report_date)
    test_report_content = test_report.to_dict()
    # TODO 3: This should likely be its own 'pyexcel' model or something of the like
    df = DataFrame.from_items(
        [col for col in test_report_content.items()]
    )
    df.name = 'sla_report'
    df.index = [''] + (list(app.config['CLIENTS']) if app.config.get('CLIENTS', None) else ['Torie', 'Sean', 'Susan', 'Debbie'])
    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    return render_template(
        'report.html',
        tables=[pf],
        titles=[pf.frame.name]
    )

# @mod.route("/report/upload", methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         return jsonify({"result": request.get_array(field_name='file')})
#     return '''
#     <!doctype html>
#     <title>Upload an excel file</title>
#     <h1>Excel file upload (csv, tsv, csvz, tsvz only)</h1>
#     <form action="" method=post enctype=multipart/form-data><p>
#     <input type=file name=file><input type=submit value=Upload>
#     </form>
#     '''
#
#
# @mod.route("/report/download", methods=['GET'])
# def download_file():
#     return excel.make_response_from_array([[1, 2], [3, 4]], "csv")
#
#
# @mod.route("/report/export", methods=['GET'])
# def export_records():
#     return excel.make_response_from_array([[1, 2], [3, 4]], "csv", file_name="export_data")
#
# # TODO this is ripe for flask-excel extension for upload/download: http://flask-excel.readthedocs.io/en/latest/
# # TODO 2: Sheet.save_to_database(session, table[, ...])	Save data in sheet to database table
# # # TODO https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html
# @mod.route('/report/run/')
# @mod.route('/report/run')
# def run_report():
#     # df = pd.read_sql(query.statement, query.session.bind)  # this may be the way to read dataframes
#     # pd.read_sql(session.query(Complaint).filter(Complaint.id == 2).statement,session.bind)
#     # use this https://github.com/amancevice/redpanda/blob/master/notebooks/python35/notebook.ipynb redpandas
#     # need to have custom models before this will work though
#     # record_set = g.db.query(FlexibleStorage).order_by(FlexibleStorage.id).filter((func.date(current_app.test_date)).all()
#     record_set = current_app.data_src.get_records('sla_report', filter=func.date(current_app.test_date))
#     test_report = report(cache(record_set, pk='call_id', subkey='event_id'), list(current_app.config['CLIENTS']))
#     test_report.name = str(current_app.test_date.date())
#     test_report_rownames = test_report.rownames
#     test_report_content = test_report.to_dict()
#     # TODO 3: This should likely be its own 'pyexcel' model or something of the like
#     data = DataFrame.from_items(
#         [col for col in test_report_content.items()]
#     )
#     data.index = test_report_rownames
#     return display_report(tables=[data.to_html(classes='report')],
#                           titles=['na', test_report.name])
#
#
# def display_report(**kwargs):
#     return render_template(
#         'report.html',
#         **kwargs
#     )
