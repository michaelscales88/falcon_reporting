import pypyodbc as ps
from automated_sla_tool.src.PyDbTool import PyDbTool


class PGEngine(PyDbTool):
    def __init__(self, **parameters):
        super().__init__()
        self.init_params(**parameters)
        self._conn = self.get_conn()
        print('Successful connection to:\n{0}'.format(self))

    def get_conn(self):
        conn_string = ''.join([v for v in self._params.values()])
        return ps.connect(conn_string, timeout=2, unicode_results=True, readonly=True)

    def init_params(self, **kwargs):
        self._params['DRIVER'] = '{0}={1};'.format('DRIVER', kwargs.get('DRIVER', '{PostgreSQL Unicode}'))
        self._params['UID'] = '{0}={1};'.format('UID', kwargs.get('UID', None))
        self._params['PWD'] = '{0}={1};'.format('PWD', kwargs.get('PWD', None))
        self._params['SERVER'] = '{0}={1};'.format('SERVER', kwargs.get('SERVER', None))
        self._params['PORT'] = '{0}={1};'.format('PORT', kwargs.get('PORT', None))
        self._params['DATABASE'] = '{0}={1};'.format('DATABASE', kwargs.get('DATABASE', None))
        self._params['Trusted_Connection'] = '{0}={1};'.format('Trusted_Connection',
                                                               kwargs.get('Trusted_Connection', 'yes'))

    def refresh_connection(self):
        self._conn.close()
        self._conn = self.get_conn()

    def rtn_excel(self, sql_command):
        columns, data = self.get_data(sql_command)
        return data

    def rtn_dict(self, sql_command):
        columns, data = self.get_data(sql_command)
        results = []
        for row in data:
            results.append(dict(zip(columns.keys(), row)))
        return results

    def replicate_to(self, dest_conn=None, sql_commands=()):
        if dest_conn:
            for sql_command in sql_commands:
                columns, data = self.get_data(sql_command.cmd)
                data.name = sql_command.name
                dest_conn.copy_tables(columns, data)
        else:
            print('No connection to transfer to.')

    def get_db_info(self):
        cursor1 = self._conn.cursor()
        cursor2 = self._conn.cursor()

        for i, rows in enumerate(cursor1.tables()):
            if rows['table_type'] == "TABLE":
                print('{i}: {row}'.format(i=i, row=rows['table_name']))
                for fld in cursor2.columns(rows['table_name']):
                    print(fld['table_name'], fld['column_name'])
