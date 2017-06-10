from flask import current_app
from flask_restful import Resource
from flask_jsonpify import jsonpify


class IndexView(Resource):

    def get(self, offset, per_page):
        total_records = current_app.data_src.record_count('sla_report')
        frame = current_app.data_src.page_view('sla_report', offset=offset, per_page=per_page)
        return jsonpify(
            iTotalRecords=total_records,
            iTotalDisplayRecords=total_records,
            aaData=frame.to_json(orient='records')
        )

