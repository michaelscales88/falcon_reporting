import pyexcel as pe
from datetime import datetime
from collections import OrderedDict


class PyDbTool(object):
    def __init__(self):
        super().__init__()
        self._conn = None
        self._params = {}

    @property
    def name(self):
        return self._params['local_db'] if self._params.get('local_db', None) else self._params.get('DATABASE', 'unknwn')

    def copy_table(self):
        print('No copy_table function provided.', flush=True)

    def transform_pyexcel(self, ptr):
        headers = [column[0] for column in ptr.description]
        rtn_sheet = pe.Sheet()
        rtn_sheet.row += headers
        rtn_sheet.name_columns_by_row(0)
        for rows in ptr.fetchall():
            rtn_sheet.row += list(rows)
        return rtn_sheet

    def get_data(self, sql_command):
        cur = self.exc_cmd(sql_command)
        return OrderedDict([(column[0], column[1]) for column in cur.description]), self.transform_pyexcel(cur)

    def exc_cmd(self, sql_command):
        print(sql_command, flush=True)
        return self._conn.cursor().execute(sql_command)

    def replicate_to(self, dest_conn=None, sql_commands=()):
        if dest_conn:
            for sql_command in sql_commands:
                print('Starting replicate {name} {time}'.format(name=sql_command.name, time=datetime.now().time()), flush=True)
                columns, data = self.get_data(sql_command.cmd)
                data.name = sql_command.name
                dest_conn.copy_tables(columns, data)
                print('returning get_data {name} {time}'.format(name=data.name, time=datetime.now().time()), flush=True)
        else:
            print('No connection to transfer to.')

    def __repr__(self):
        return '\n'.join([v for v in self._params.values()])

    def __del__(self):
        try:
            self._conn.close()
            print(r'Connection to {conn} successfully closed.'.format(conn=self.name))
        except AttributeError:
            print(r'No connection to close.')
