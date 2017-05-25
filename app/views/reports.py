from flask import render_template, g, Blueprint, current_app
from pandas import DataFrame
from sqlalchemy import func

from app.models.custom_model import custom_model
from app.models.flexible_storage import FlexibleStorage
from app.src.factory import internal_connection
from app.lib.sla_report import report

mod = Blueprint('reports', __name__, template_folder='templates')


# TODO this is ripe for flask-excel extension for upload/download: http://flask-excel.readthedocs.io/en/latest/
# TODO 2: Sheet.save_to_database(session, table[, ...])	Save data in sheet to database table
# # TODO https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html
@mod.route('/run/')
@mod.route('/run')
def run_report():
    record_set = g.db.query(FlexibleStorage).order_by(FlexibleStorage.id).filter(func.date(current_app.test_date)).all()
    test_report = report(record_set)
    test_report.name = 'Bitching Baby'
    test_report_rownames = test_report.rownames
    test_report_content = test_report.to_dict()
    # TODO 3: This should likely be its own 'pyexcel' model or something of the like
    data = DataFrame.from_items(
        [col for col in test_report_content.items()]
    )
    data.index = test_report_rownames
    test_model = custom_model('sla_report')    # This appears to be working. Need many more mixins
    session = internal_connection(
        current_app.config['SQLALCHEMY_DATABASE_URI'],
        echo=current_app.config['SQLALCHEMY_ECHO'],
        cls=test_model
    )
    print(test_model.__table__.columns.keys())
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
    return render_template(
        'report_viewer.html',
        tables=[data.to_html(classes='report')],
        titles=['na', test_report.name]
    )
