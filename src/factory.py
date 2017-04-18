from re import search, M, I, DOTALL
from glob import glob
from os.path import join, splitext
from datetime import timedelta

from automated_sla_tool.src.ImapConnection import ImapConnection
from automated_sla_tool.src.utilities import valid_dt


class Loader:
    def __init__(self):
        self._conn = None
        self._cwd = None

    @property
    def cwd(self):
        return self._cwd

    @cwd.setter
    def cwd(self, new_wd):
        self._cwd = new_wd

    @property
    def connection(self):
        return self._conn

    @connection.setter
    def connection(self, new_conn):
        self._conn = new_conn

    def load(self, unloaded_files):
        loaded_files = {}
        for f_name in reversed(unloaded_files):
            src_f = glob(r'{f_path}*.*'.format(f_path=join(self.cwd, f_name)))
            if len(src_f) is 1:
                unloaded_files.remove(f_name)
                loaded_files[f_name] = {
                    'path': src_f[0],
                    'ext': splitext(src_f[0])[1][1:]
                }
        return loaded_files

    def load_or_dl(self, unloaded_files):
        print('entering load or dl')
        loaded_files = self.load(unloaded_files)
        print(loaded_files)
        if len(unloaded_files) > 0:
            print('about to download')
            Downloader(parent=self.connection).get_f_list(self.connection.interval + timedelta(days=1),
                                                          unloaded_files)
        for key, values in {**loaded_files, **self.load(unloaded_files)}.items():
            yield key, values['path'], values['ext']


class Downloader(ImapConnection):
    @staticmethod
    def lexer(full_string, pivot):  # create settings option which creates an OrdDict that executes instructions
        if full_string:
            search_object = search('\(([^()]+)\)', full_string, M | I | DOTALL)
            try:
                val1, val2 = search_object.groups()[0].split(pivot)
            except AttributeError:
                val1 = val2 = False
            return val1, val2

    def get_f_list(self, on, f_list):
        matched_f_list = {}
        ids = super().get_ids(on, 'FROM "Chronicall Reports"')
        for f in f_list:
            matched_f_list[f] = ids.get(f, None)
        return matched_f_list

    def get_vm(self, on):
        payload = {}
        ids = super().get_ids(on, 'FROM "vmpro@mindwireless.com"')
        for k, v in ids.items():
            phone_number, client_name = self.lexer(v.pop('subject', None), pivot=' > ')
            if client_name:
                client_data = payload.get(client_name, [])
                a_vm = {
                    'phone_number': phone_number,
                    'time': valid_dt(v['dt'])
                }
                client_data.append(a_vm)
                payload[client_name] = client_data
        return payload
