from flask.views import MethodView
from flask import render_template, current_app
from pyxley import UILayout
from pyxley.filters import SelectButton
from pyxley.charts.mg import LineChart, Figure
# http://pyxley.readthedocs.io/en/latest/basic.html#javascript Pyxley documentation

from app.src.factory import get_page_args, get_pagination


class DataFrameView(MethodView):
    """
    Subclass of flask.views.MethodView
    Intended to provide a single means of displaying pandas Data Frames
    """
    # TODO make this into interactive widget
    # https://blog.ouseful.info/2016/12/29/simple-view-controls-for-pandas-dataframes-using-ipython-widgets/
    # https://github.com/bluenote10/PandasDataFrameGUI
    # input fields: https://stackoverflow.com/questions/41470817/edit-pandas-dataframe-in-flask-html-page
    def get(self):
        total_records = current_app.data_src.record_count('sla_report')
        page, per_page, offset = get_page_args()
        df = current_app.data_src.get_frame('sla_report', offset=offset, per_page=per_page)
        if not df.empty:  # Protect from KeyError if the dB is empty
            df.set_index(['call_id', 'event_id'], inplace=True)  # inplace = True saves us from having to bind a new dataframe
            df.name = 'test'
            df.style.format('<input name="df" value="{}" />')
        pagination = get_pagination(
            page=page,
            per_page=per_page,
            total=total_records,
            record_name='id',
            format_total=True,
            format_number=True,
        )
        return render_template(
            'index.html',
            page=page,
            per_page=per_page,
            pagination=pagination,
            tables=[frame.to_html(classes='report') for frame in (df,) if not frame.empty],
            titles=['na', *[frame.name for frame in (df,) if not frame.empty]]
        )

    def post(self):
        # post modifications to the selections for the dataframe
        # return render_template()
        return 'hello'
