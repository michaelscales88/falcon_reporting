import pyexcel as pe
import os
import re
from datetime import timedelta, datetime, time, date
from glob import glob
from dateutil.parser import parse
from collections import OrderedDict
from automated_sla_tool.src.UtilityObject import UtilityObject
from automated_sla_tool.src.FinalReport import FinalReport


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            dict.__setitem__(self, key, value)


class FilePile(object):

    def __init__(self, **kwargs):
        self._data = {
            'report_date': kwargs.get('report_date', self.__class__.manual_input(self)),
            'final_report': FinalReport(),
            'manifest': kwargs.get('manifest', self.__class__.get_manifest(self)),
            'utility_obj': UtilityObject(),
            'src_files': kwargs.get('src_files', self.__class__.get_src_files(self)),
        }
        # print(self._data['report_date'])
        # print(isinstance(self.__class__.__name__, SlaFiles))
        # self.dates = report_dates
        # self.fr = FinalReport(report_type=report_type, report_date=self.dates)
        # self.src_files = {}
        # self.req_src_files = []



        # self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # self.active_directory = r'{0}\{1}'.format(self.path, r'active_files')
        # self.converter_arg = r'{0}\{1}'.format(self.path, r'converter\ofc.ini')
        # self.converter_exc = r'{0}\{1}'.format(self.path, r'converter\ofc.exe')
        # self.login_type = r'imap.gmail.com'
        # self.user_name = r'mindwirelessreporting@gmail.com'
        # self.password = r'7b!2gX4bD3'
        # self._manifest = None
        # if isinstance(self.dates, date):
        #     self.util_datetime = datetime.combine(self.dates, time())
        #     self.day_of_wk = self.dates.weekday()
        #     self.src_doc_path = self.open_src_dir()
        # else:
        #     self.util_datetime = None
        #     self.day_of_wk = None

    @property
    def utility_tool(self):
        return self._data['utility_obj']

    @property
    def path(self):
        return self._data['utility_obj'].curr_path()

    @property
    def manifest(self):
        return self._manifest

    @manifest.setter
    def manifest(self, rpt_manifest):
        try:
            self.fr.set_header(rpt_manifest.tgt_header)
            self.fr.set_rows(rpt_manifest.tgt_rows)
        except Exception as e:
            print(e)
        else:
            self._manifest = rpt_manifest

    def manual_input(self):
        raise Exception('No extended method provided')

    def get_src_files(self):
        raise Exception('No extended method provided')

    def get_manifest(self):
        raise Exception('No extended method provided')

    def load_documents(self):
        # TODO abstract this -> *args
        if self.fr.finished:
            return
        else:
            for (f, p) in self.r_loader(self.req_src_files).items():
                try:
                    file = pe.get_book(file_name=p)
                except FileNotFoundError:
                    print("Could not open src documents"
                          "-> {0}.load_documents: {1}".format(self.fr.type, f))
                else:
                    self.src_files[f] = self.filter_chronicall_reports(file)

    def save(self, user_string=None):
        self.set_save_path(self.fr.type)
        self.fr.save_report(user_string)

    '''
    OS Operations
    '''

    def set_save_path(self, report_type):
        save_path = r'{0}\Output\{1}'.format(os.path.dirname(self.path), report_type)
        self.change_dir(save_path)

    def open_src_dir(self):
        file_dir = r'{dir}\{sub}\{yr}\{tgt}'.format(dir=os.path.dirname(self.path),
                                                    sub='Attachment Archive',
                                                    yr=self.dates.strftime('%Y'),
                                                    tgt=self.dates.strftime('%m%d'))
        self.change_dir(file_dir)
        return os.getcwd()

    # def clean_src_loc(self):
    #     # TODO today test this more... doesn't merge/delete original file
    #     import os
    #     filelist = [f for f in os.listdir(self.src_doc_path) if f.endswith((".xlsx", ".xls"))]
    #     spc_ch = ['-', '_']
    #     del_ch = ['%', r'\d+']
    #     for f in filelist:
    #         f_name, ext = os.path.splitext(f)
    #         f_name = re.sub('[{0}]'.format(''.join(spc_ch)), ' ', f_name)
    #         f_name = re.sub('[{0}]'.format(''.join(del_ch)), '', f_name)
    #         f_name = f_name.strip()
    #         os.rename(f, r'{0}{1}'.format(f_name, ext))
    #
    # def r_loader(self, unloaded_files, run2=False):
    #     if run2 is True:
    #         return {}
    #     loaded_files = {}
    #     self.clean_src_loc()
    #     for f_name in reversed(unloaded_files):
    #         src_f = glob(r'{0}\{1}*.xlsx'.format(self.src_doc_path, f_name))
    #         if len(src_f) is 1:
    #             loaded_files[f_name] = src_f[0]
    #             unloaded_files.remove(f_name)
    #         else:
    #             # TODO additional error handling for file names that have not been excluded?
    #             pass
    #     self.download_documents(files=unloaded_files)
    #     return {**loaded_files, **self.r_loader(unloaded_files, True)}

    def download_documents(self, files):
        if self.fr.finished:
            return
        else:
            self.download_chronicall_files(file_list=files)
            src_file_directory = os.listdir(self.src_doc_path)
            for file in src_file_directory:
                if file.endswith(".xls"):
                    self.copy_and_convert(self.src_doc_path, src_file_directory)
                    break

    '''
    Report Utilities
    '''

    def apply_formatters_to_wb(self, wb, filters=(), one_filter=None):
        for sheet in wb:
            self.apply_formatters_to_sheet(sheet, filters, one_filter)

    def apply_formatters_to_sheet(self, sheet, filters=(), one_filter=None):
        for a_filter in filters:
            this_filter = pe.RowValueFilter(a_filter)
            sheet.filter(this_filter)
        if one_filter:
            this_filter = pe.RowValueFilter(one_filter)
            sheet.filter(this_filter)

    def copy_and_convert(self, file_location, directory):
        from shutil import move
        for src_file in directory:
            if src_file.endswith(".xls"):
                src = os.path.join(file_location, src_file)
                des = os.path.join(self.active_directory, src_file)
                move(src, des)

        import subprocess as proc
        proc.run([self.converter_exc, self.converter_arg])
        filelist = [f for f in os.listdir(self.active_directory) if f.endswith(".xls")]
        for f in filelist:
            f = os.path.join(self.active_directory, f)
            os.remove(f)

        for src_file in os.listdir(self.active_directory):
            src = os.path.join(self.active_directory, src_file)
            des = os.path.join(file_location, src_file)
            move(src, des)

    def prepare_sheet_header(self, lst, first_index):
        return_list = [i for i in lst]
        return_list.insert(0, first_index)
        return [return_list]

    def filter_chronicall_reports(self, workbook):
        try:
            del workbook['Summary']
        except KeyError:
            pass
        chronicall_report_filter = pe.RowValueFilter(self.header_filter)
        for sheet in workbook:
            sheet.filter(chronicall_report_filter)
            sheet.name_columns_by_row(0)
            sheet.name_rows_by_column(0)
            try:
                self.chck_rpt_dates(sheet)
            except ValueError:
                workbook.remove_sheet(sheet.name)
        return workbook

    def ts_to_int(self, column):
        rtn_col = []
        for item in column:
            rtn_col.append(self.get_sec(item))
        return rtn_col

    def header_filter(self, row):
        corner_case = re.split('\(| - ', row[0])
        bad_word = corner_case[0].split(' ')[0] not in ('Feature', 'Call', 'Event')
        return True if len(corner_case) > 1 else bad_word

    def chck_rpt_dates(self, sheet):
        first = self.chck_w_in_days(sheet.column['Start Time'][0])
        try:
            last = self.chck_w_in_days(sheet.column['End Time'][-1])
        except ValueError:
            last = True
        if first and last:
            pass
        else:
            raise ValueError

    def collate_wb_to_sheet(self, wb=()):
        headers = ['row_names'] + wb[0].colnames
        sheet_to_replace_wb = pe.Sheet(colnames=headers)
        unique_records = UniqueDict()
        for sheet in wb:
            for i, name in enumerate(sheet.rownames):
                unique_records[name] = sheet.row_at(i)
        for rec in sorted(unique_records.keys()):
            sheet_to_replace_wb.row += [rec] + unique_records[rec]
        sheet_to_replace_wb.name_rows_by_column(0)
        return sheet_to_replace_wb

    '''
    General Utilities
    '''

    # TODO make a typedef decorator

    def return_selection(self, input_opt):
        selection = list(input_opt.values())
        return selection[
            int(
                input(
                    ''.join(['{k}: {i}\n'.format(k=k, i=i) for i, k in enumerate(input_opt)])
                )
            )
        ]

    def chck_w_in_days(self, doc_dt, num_days=1):
        try:
            date_time = parse(doc_dt)
        except ValueError:
            return False
        else:
            if (date_time - self.util_datetime) <= timedelta(days=num_days):
                return True
            else:
                return False

    def download_chronicall_files(self, file_list):
        '''
        Temporary
        self.login_type = r'imap.gmail.com'
        self.user_name = r'mindwirelessreporting@gmail.com'
        self.password = r'7b!2gX4bD3'
        '''
        import email
        import imaplib
        if file_list not in os.listdir(self.src_doc_path):
            try:
                imap_session = imaplib.IMAP4_SSL(self.login_type)
                status, account_details = imap_session.login(self.user_name, self.password)
                if status != 'OK':
                    raise ValueError('Not able to sign in!')

                imap_session.select("Inbox")
                on = "ON " + (self.dates + timedelta(days=1)).strftime("%d-%b-%Y")
                status, data = imap_session.uid('search', on, 'FROM "Chronicall Reports"')
                if status != 'OK':
                    raise ValueError('Error searching Inbox.')

                # Iterating over all emails
                for msg_id in data[0].split():
                    status, message_parts = imap_session.uid('fetch', msg_id, '(RFC822)')
                    if status != 'OK':
                        raise ValueError('Error fetching mail.')

                    mail = email.message_from_bytes(message_parts[0][1])
                    for part in mail.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue
                        file_name = part.get_filename()

                        if bool(file_name):
                            file_path = os.path.join(file_name)
                            if not os.path.isfile(file_path):
                                fp = open(file_path, 'wb')
                                fp.write(part.get_payload(decode=True))
                                fp.close()

                imap_session.close()
                imap_session.logout()

            except Exception as err:
                raise ValueError('Not able to download all attachments. Error: {}'.format(err))
        else:
            print("Files already downloaded.")

    def correlate_list_time_data(self, src_list, list_to_correlate, key):
        return_list = []
        for event in self.find(src_list, key):
            return_list.append(self.get_sec(list_to_correlate[event]))
        return return_list

    def correlate_list_val_data(self, src_list, list_to_correlate, key):
        return_list = []
        for event in self.find(src_list, key):
            return_list.append(list_to_correlate[event])
        return return_list

    def find(self, lst, a):
        return [i for i, x in enumerate(lst) if x == a]

    def is_empty_wb(self, book):
        if type(book) is not pe.Book:
            return
        return book.number_of_sheets() is 0

    def transmit_report(self):
        return self.fr

    def make_summary(self, headers):
        todays_summary = pe.Sheet()
        todays_summary.row += headers
        todays_summary.name_columns_by_row(0)
        return todays_summary

    def add_time(self, dt_t, add_time=None):
        return (datetime.combine(datetime.today(), dt_t) + add_time).time()

    def check_finished(self, report_string=None):
        file_name = r'{0}.xlsx'.format(self.fr.name if report_string is None else report_string)
        the_path = os.path.dirname(self.path)
        the_file = r'{0}\Output\{1}\{2}'.format(the_path, self.fr.type, file_name)
        if os.path.isfile(the_file):
            self.fr.open_report(the_file)
        return self.fr.finished

    def safe_parse(self, dt_time=None, default_date=None, default_rtn=None):
        try:
            return parse(dt_time, default=(default_date if default_date is not None else self.util_datetime))
        except ValueError:
            return default_rtn if default_rtn is not None else self.util_datetime

    def read_time(self, time_object, spc_chr='*'):
        try:
            return_time = time_object.split(spc_chr)[0]
        except AttributeError:
            try:
                return_time = time_object.time()
            except AttributeError:
                return_time = time_object
        else:
            return_time = self.safe_parse(return_time).time()
        return return_time
