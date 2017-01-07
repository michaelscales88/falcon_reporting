from datetime import datetime, timedelta
from automated_sla_tool.src.PGEngine import PGEngine as pg
from automated_sla_tool.src.SqlLiteEngine import SqlLiteEngine as sq


class SqlCommand(object):
    def __init__(self):
        super().__init__()
        self._name = None
        self._cmd = None

    def __repr__(self):
        return self._cmd

    @property
    def cmd(self):
        return self._cmd

    @cmd.setter
    def cmd(self, cmd):
        self._cmd = cmd

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


def main():
    print('starting')
    conn_string = {
        'DATABASE': 'chronicall',
        'UID': 'Chronicall',
        'PWD': 'ChR0n1c@ll1337',
        'SERVER': '10.1.3.17',
        'PORT': '9086'
    }
    tables = [
        # 'c_call',
        # 'c_event',
        'c_feature',
    ]
    commands = []
    raw_commands = {
        k: datetime.today().date() - timedelta(days=1) for k in tables
        }
    for k, v in raw_commands.items():
        cmd = SqlCommand()
        cmd.name = k
        cmd.cmd = (
            '''
            SELECT *
            FROM {t}
            WHERE to_char({t}.start_time, 'YYYY-MM-DD') = '{v}'
            '''.format(t=cmd.name, v=v.strftime('%Y-%m-%d'))
        )
        commands.append(cmd)
    conn = pg(**conn_string)
    print('Starting copying {time}'.format(time=datetime.now().time()), flush=True)
    conn.replicate_to(dest_conn=sq(), sql_commands=commands)
    print('Finished copying {time}'.format(time=datetime.now().time()), flush=True)
    new_conn = sq()
    # print(new_conn.query('c_call'))
    print('Starting read replicate count {time}'.format(time=datetime.now().time()), flush=True)
    # print(new_conn.query('c_event'))
    print(new_conn.query('c_feature'))
    print('Finished read replicate count {time}'.format(time=datetime.now().time()), flush=True)
    print('Starting read replicate {time}'.format(time=datetime.now().time()), flush=True)
    # new_conn.query2('c_event')
    new_conn.query2('c_feature')
    print('Finished read replicate {time}'.format(time=datetime.now().time()), flush=True)
    # print(new_conn.query('c_feature'))
    print('complete')


if __name__ == '__main__':
    main()
