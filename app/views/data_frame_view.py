from flask import current_app, request, abort
from flask_restful import Resource
from flask_jsonpify import jsonify


def get_paginated_list(klass, url, start, limit):
    # check if page exists
    results = klass.query.all()
    count = len(results)
    if count < start:
        abort(404)
    # make response
    obj = {'start': start, 'limit': limit, 'count': count}
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj


class DataFrameView(Resource):

    def get(self, page, per_page):
        total_records = current_app.data_src.record_count('sla_report')
        offset = (page - 1) * per_page
        print('called get', page, per_page, offset)
        df = current_app.data_src.page_view('sla_report', offset=offset, per_page=per_page)
        return jsonify(
            iTotalRecords=total_records,
            iTotalDisplayRecords=per_page,
            aaData=df.to_json(orient='records')
        )

    def get2(self):
        return jsonify(get_paginated_list(
            ,
            '/api/v2/events/page',
            start=request.args.get('start', 1),
            limit=request.args.get('limit', 20)
        ))
