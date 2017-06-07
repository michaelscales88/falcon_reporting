from flask import render_template, current_app
from flask_restful import Resource
from flask_jsonpify import jsonpify

from app.src.factory import get_page_args, get_pagination


class DataFrameView(Resource):

    # Ajax should look like:
    # type GET
    # dataType: "jsonp",
    # url: "http://localhost:5000/df/1"
    def get(self, id):
        print('called get')
        total_records = current_app.data_src.record_count('sla_report')
        page, per_page, offset = get_page_args()
        df = current_app.data_src.get_frame('sla_report', offset=offset, per_page=per_page)
        # if not df.empty:  # Protect from KeyError if the dB is empty
        #     df.set_index(['call_id', 'event_id'], inplace=True)  # inplace = True saves us from having to bind a new dataframe
        # # pagination = get_pagination(
        # #     page=page,
        # #     per_page=per_page,
        # #     total=total_records,
        # #     record_name='id',
        # #     format_total=True,
        # #     format_number=True,
        # # )
        # # return render_template(
        # #     'index.html',
        # #     page=page,
        # #     per_page=per_page,
        # #     pagination=pagination,
        # #     tables=[frame.to_html(classes='report') for frame in (df,) if not frame.empty],
        # #     titles=['na', *[frame.name for frame in (df,) if not frame.empty]]
        # # )
        return jsonpify(df.to_json())

    def post(self):
        # post modifications to the selections for the dataframe
        # return render_template()
        return 'hello'
