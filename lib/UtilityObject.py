import os
import pyexcel as pe
import re
from glob import glob


class UtilityObject(object):

    def curr_path(self):
        return os.getcwd()

    def str_to_bool(self, bool_str):
        if type(bool_str) is bool:
            return bool_str
        elif bool_str in ('True', 'TRUE', 'true'):
            return True
        elif bool_str in ('False', 'false', 'FALSE'):
            return False
        else:
            raise ValueError("Cannot covert {} to a bool".format(bool_str))

    def get_sec(self, time_string):
        try:
            h, m, s = [int(float(i)) for i in time_string.split(':')]
        except TypeError:
            return 0
        except ValueError:
            try:
                h, m = [int(float(i)) for i in time_string.split(':')]
                s = 0
            except ValueError:
                return 0
        return self.convert_sec(h, m, s)

    def convert_sec(self, h, m, s):
        return (3600 * int(h)) + (60 * int(m)) + int(s)

    def convert_time_stamp(self, convert_seconds):
        minutes, seconds = divmod(convert_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return r"{0}:{1:02d}:{2:02d}".format(hours, minutes, seconds)

    def change_dir(self, the_dir):
        try:
            os.chdir(the_dir)
        except FileNotFoundError:
            try:
                os.makedirs(the_dir, exist_ok=True)
                os.chdir(the_dir)
            except OSError:
                pass

    def load_data(self, file):
        if type(file) is pe.sheets.sheet.Sheet:
            return_file = file
        else:
            return_file = self.open_pe_file(file)
        return_file.name_columns_by_row(0)
        return_file.name_rows_by_column(0)
        return return_file

    def open_pe_file(self, file):
        try:
            return_file = pe.get_sheet(file_name=file)
        except OSError:
            print('OSError ->'
                  'cannot open {}'.format(file))
        else:
            return return_file

    def r_loader(self, unloaded_files, run2=False):
        if run2 is True:
            return {}
        loaded_files = {}
        self.clean_src_loc()
        for f_name in reversed(unloaded_files):
            src_f = glob(r'{0}\{1}*.xlsx'.format(self.src_doc_path, f_name))
            if len(src_f) is 1:
                loaded_files[f_name] = src_f[0]
                unloaded_files.remove(f_name)
            else:
                # TODO additional error handling for file names that have not been excluded?
                pass
        self.download_documents(files=unloaded_files)
        return {**loaded_files, **self.r_loader(unloaded_files, True)}

    def clean_src_loc(self):
        # TODO today test this more... doesn't merge/delete original file
        import os
        filelist = [f for f in os.listdir(self.src_doc_path) if f.endswith((".xlsx", ".xls"))]
        spc_ch = ['-', '_']
        del_ch = ['%', r'\d+']
        for f in filelist:
            f_name, ext = os.path.splitext(f)
            f_name = re.sub('[{0}]'.format(''.join(spc_ch)), ' ', f_name)
            f_name = re.sub('[{0}]'.format(''.join(del_ch)), '', f_name)
            f_name = f_name.strip()
            os.rename(f, r'{0}{1}'.format(f_name, ext))

    def test(self):
        return self.__class__.__module__
