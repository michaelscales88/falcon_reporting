import operator
import pyexcel as pe
from pyexcel import Sheet, Book
from datetime import time, timedelta, date
from dateutil.parser import parse
from collections import defaultdict, namedtuple, OrderedDict
from automated_sla_tool.src.BucketDict import BucketDict
from automated_sla_tool.src.AReport import AReport
from automated_sla_tool.src.ReportManifest import ReportManifest


# TODO Add feature to run report without call pruning. Ex. Call spike days where too many duplicates are removed


class SlaReport(AReport):

    def __init__(self, report_date=None):
        report_date = report_date if report_date else self.manual_input()
        super().__init__(report_dates=report_date,
                         report_type='sla_report')
        self.file_fmt = r'{0}_Incoming DID Summary'.format(self.dates.strftime("%m%d%Y"))
        self.override = True
        if self.check_finished(report_string=self.file_fmt) and not self.override:
            print('{report}: Complete'.format(report=self.file_fmt))
        else:
            print('Building: {report}'.format(report=self.file_fmt))
            self.req_src_files = [r'Call Details (Basic)', r'Group Abandoned Calls', r'Cradle to Grave']
            self.clients = self.get_client_settings()
            self.clients_verbose = self.make_verbose_dict()
            # TODO move this into .conf file -> make dict extended settings class
            # TODO probably good to force all nonprogramatic lists to conform to OrderedDicts Ex in docs .. isistance(thing, OD)
            headers_w_meta = OrderedDict(
                [
                    ('I/C Presented', self.sum),
                    ('I/C Answered', self.sum),
                    ('I/C Lost', self.sum),
                    ('Voice Mails', self.sum),
                    ('Incoming Answered (%)', {'fn': self.true_div,
                                               'col1': 'I/C Answered',
                                               'col2': 'I/C Presented'}),
                    ('Incoming Lost (%)', {'fn': self.true_div_comb,
                                           'col1': 'I/C Lost',
                                           'col2': 'Voice Mails',
                                           'col3': 'I/C Presented'}),
                    ('Average Incoming Duration', {'fn': self.floor_div_weighted,
                                                   'col1': 'Average Incoming Duration',
                                                   'col2': 'I/C Answered',
                                                   'col3': 'I/C Answered'}),
                    ('Average Wait Answered', {'fn': self.floor_div_weighted,
                                               'col1': 'Average Wait Answered',
                                               'col2': 'I/C Answered',
                                               'col3': 'I/C Answered'}),
                    ('Average Wait Lost', {'fn': self.floor_div_weighted,
                                           'col1': 'Average Wait Lost',
                                           'col2': 'I/C Lost',
                                           'col3': 'I/C Lost'}),
                    ('Calls Ans Within 15', self.sum),
                    ('Calls Ans Within 30', self.sum),
                    ('Calls Ans Within 45', self.sum),
                    ('Calls Ans Within 60', self.sum),
                    ('Calls Ans Within 999', self.sum),
                    ('Call Ans + 999', self.sum),
                    ('Longest Waiting Answered', self.max_val),
                    ('PCA', {'fn': self.true_div_comb,
                             'col1': 'Calls Ans Within 15',
                             'col2': 'Calls Ans Within 30',
                             'col3': 'I/C Presented'})
                ]
            )
            rows_w_meta = OrderedDict(
                [
                    ('{num}'.format(num=num), '{name}'.format(name=info.name)) for num, info in self.clients.items()
                ]
            )
            self.manifest = ReportManifest(
                header=headers_w_meta,
                rows=rows_w_meta
            )
            self.load_documents()
            self.orphaned_voicemails = None
            self.sla_report = {}

    '''
    UI Section
    '''

    def zzfull_run(self):
        if self.fr.finished:
            return
        else:
            self.compile_call_details()
            self.scrutinize_abandon_group()
            self.extract_report_information()
            self.process_report()
            self.save()
            # print(self.fr)
            self.fr.finished = True

    def zztest_run(self):
        if self.fr.finished:
            return
        else:
            self.compile_call_details2()
            self.scrutinize_abandon_group()
            self.extract_report_information()
            self.process_report2()
            self.fr.finished = True

    def zzdisplay_fr(self):
        self.fr.verbose_rows()
        print(self.fr.full_report)
        # self.fr.save_report(tgt=self.fr.full_report_w_fmt(), user_string=self.file_fmt)

    # TODO rethink this to compensate for diff kinds of reports and move to AReport
    def manual_input(self):
        input_opt = OrderedDict(
            [
                ('-4 Days', -4),
                ('-3 Days', -3),
                ('-2 Days', -2),
                ('Yesterday', -1)
            ]
        )
        return date.today() + timedelta(days=self.return_selection(input_opt))

    def load_documents(self):
        super().load_documents()
        call_details_filters = [
            self.inbound_call_filter,
            self.zero_duration_filter,
            self.remove_internal_inbound_filter
        ]
        self.src_files[r'Call Details (Basic)'] = self.collate_wb_to_sheet(wb=self.src_files[r'Call Details (Basic)'])
        self.apply_formatters_to_sheet(sheet=self.src_files[r'Call Details (Basic)'],
                                       filters=call_details_filters)
        self.src_files[r'Group Abandoned Calls'] = self.collate_wb_to_sheet(wb=self.src_files[r'Group Abandoned Calls'])
        self.apply_formatters_to_sheet(sheet=(self.src_files[r'Group Abandoned Calls']),
                                       one_filter=self.answered_filter)
        self.src_files[r'Call Details (Basic)'].name = 'call_details'
        self.src_files[r'Group Abandoned Calls'].name = 'abandon_grp'
        self.src_files[r'Voice Mail'] = defaultdict(list)
        self.get_voicemails()

        for src_file in self.src_files.keys():
            if isinstance(self.src_files[src_file], Sheet):
                for col_name in self.src_files[src_file].colnames:
                    if 'Duration' in col_name:
                        self.src_files[src_file].column[col_name] = self.ts_to_int(self.src_files[src_file].column[col_name])
            elif isinstance(self.src_files[src_file], Book):
                for sheet in self.src_files[src_file]:
                    for col_name in sheet.colnames:
                        if 'Duration' in col_name:
                            sheet.column[col_name] = self.ts_to_int(sheet.column[col_name])

    def compile_call_details2(self):
        if self.fr.finished:
            return
        else:
            hold_events = ('Hold', 'Transfer Hold', 'Park')
            additional_columns = OrderedDict(
                [
                    ('Wait Time', []),
                    ('Hold Time', [])
                ]
            )
            for row_name in self.src_files[r'Call Details (Basic)'].rownames:
                unhandled_call_data = {
                    k: 0 for k in hold_events
                }
                tot_call_duration = self.src_files[r'Call Details (Basic)'][row_name, 'Call Duration']
                talk_duration = self.src_files[r'Call Details (Basic)'][row_name, 'Talking Duration']
                call_id = row_name.replace(':', ' ')
                cradle_sheet = self.src_files[r'Cradle to Grave'][call_id]
                for event_row in cradle_sheet.rownames:
                    event_type = cradle_sheet[event_row, 'Event Type']
                    if event_type in hold_events:
                        unhandled_call_data[event_type] += cradle_sheet[event_row, 'Event Duration']
                raw_time_waited = sum(val for val in unhandled_call_data.values())
                raw_hold_time = tot_call_duration - talk_duration - raw_time_waited
                additional_columns['Wait Time'].append(raw_time_waited)
                additional_columns['Hold Time'].append(raw_hold_time)
            self.src_files[r'Call Details (Basic)'].extend_columns(additional_columns)

    def compile_call_details(self):
        if self.fr.finished:
            return
        else:
            time_not_talking = namedtuple('this_call',
                                          'hold_amount park_amount conference_amount transfer_amount additional_time')
            time_not_talking.__new__.__defaults__ = (0,) * len(time_not_talking._fields)
            additional_times = {
                'Wait Time': [],
                'Hold Time': []
            }
            for row_name in self.src_files[r'Call Details (Basic)'].rownames:
                call_id = row_name.replace(':', ' ')
                sheet = self.src_files[r'Cradle to Grave'][call_id]
                sheet_events = sheet.column['Event Type']
                transfer_hold = 'Transfer Hold' in sheet_events
                had_hold = 'Hold' in sheet_events
                had_park = 'Park' in sheet_events
                had_conference = 'Conference' in sheet_events
                tot_call_duration = self.get_sec(self.src_files[r'Call Details (Basic)'][row_name, 'Call Duration'])
                talk_duration = self.get_sec(self.src_files[r'Call Details (Basic)'][row_name, 'Talking Duration'])
                if (transfer_hold or had_hold or had_park or had_conference) is True:
                    event_durations = sheet.column['Event Duration']
                    this_call = time_not_talking(hold_amount=self.correlate_event_data(sheet_events,
                                                                                       event_durations,
                                                                                       'Hold'),
                                                 park_amount=self.correlate_event_data(sheet_events,
                                                                                       event_durations,
                                                                                       'Park'),
                                                 conference_amount=self.correlate_event_data(sheet_events,
                                                                                             event_durations,
                                                                                             'Conference'),
                                                 transfer_amount=self.correlate_event_data(sheet_events,
                                                                                           event_durations,
                                                                                           'Transfer Hold'))
                    if transfer_hold is True and had_conference is False:
                        transfer_hold_index = sheet_events.index('Transfer Hold')
                        this_call = this_call._replace(
                            additional_time=self.correlate_event_data(sheet_events[transfer_hold_index:],
                                                                      event_durations[transfer_hold_index:],
                                                                      'Talking')
                        )
                    time_not_talking_duration = sum(int(i) for i in this_call)
                    time_not_talking_duration = time_not_talking_duration - this_call.additional_time
                else:
                    time_not_talking_duration = 0
                wait_time = self.convert_time_stamp((tot_call_duration - talk_duration))
                additional_times['Wait Time'].append(wait_time)
                additional_times['Hold Time'].append(self.convert_time_stamp(time_not_talking_duration))
            new_columns = OrderedDict(
                (column, additional_times[column]) for column in reversed(sorted(additional_times.keys()))
            )
            self.src_files[r'Call Details (Basic)'].extend_columns(new_columns)

    def scrutinize_abandon_group(self):
        '''

                :return:
                '''
        if self.fr.finished:
            return
        else:
            self.remove_calls_less_than_twenty_seconds()
            self.remove_duplicate_calls()

    def extract_report_information(self):
        if self.fr.finished:
            return
        else:
            ans_cid_by_client = self.group_cid_by_client(self.src_files[r'Call Details (Basic)'])
            lost_cid_by_client = self.group_cid_by_client(self.src_files[r'Group Abandoned Calls'])
            for client in self.clients.keys():
                self.sla_report[client] = Client(name=client,
                                                 answered_calls=ans_cid_by_client.get(client, []),
                                                 lost_calls=lost_cid_by_client.get(client, []),
                                                 voicemail=self.src_files[r'Voice Mail'].get(self.clients[client].name, []),
                                                 full_service=self.clients[client].full_service)
                if not self.sla_report[client].is_empty():
                    # TODO this could perhaps be a try: ... KeyError...
                    if self.sla_report[client].no_answered() is False:
                        self.sla_report[client].extract_call_details(self.src_files[r'Call Details (Basic)'])
                    if self.sla_report[client].no_lost() is False:
                        self.sla_report[client].extract_abandon_group_details(self.src_files[r'Group Abandoned Calls'])

    #TODO could abstract this into FinalReport transform method
    def process_report(self):
        '''

            :return:
        '''
        if self.fr.finished:
            return
        else:
            headers = [self.dates.strftime('%A %m/%d/%Y'), 'I/C Presented', 'I/C Answered', 'I/C Lost', 'Voice Mails',
                       'Incoming Answered (%)', 'Incoming Lost (%)', 'Average Incoming Duration',
                       'Average Wait Answered',
                       'Average Wait Lost', 'Calls Ans Within 15', 'Calls Ans Within 30', 'Calls Ans Within 45',
                       'Calls Ans Within 60', 'Calls Ans Within 999', 'Call Ans + 999', 'Longest Waiting Answered',
                       'PCA']
            self.fr.row += headers
            self.fr.name_columns_by_row(0)
            total_row = dict((value, 0) for value in headers[1:])
            total_row['Label'] = 'Summary'
            for client in sorted(self.clients.keys()):
                num_calls = self.sla_report[client].get_number_of_calls()
                # answered, lost, voicemails = self.sla_report[client].get_number_of_calls()
                this_row = dict((value, 0) for value in headers[1:])
                this_row['I/C Presented'] = sum(num_calls.values())
                this_row['Label'] = '{0} {1}'.format(client, self.clients[client].name)
                if this_row['I/C Presented'] > 0:
                    ticker_stats = self.sla_report[client].get_call_ticker()
                    this_row['I/C Answered'] = num_calls['answered']
                    this_row['I/C Lost'] = num_calls['lost']
                    this_row['Voice Mails'] = num_calls['voicemails']
                    this_row['Incoming Answered (%)'] = (num_calls['answered'] / this_row['I/C Presented'])
                    this_row['Incoming Lost (%)'] = (
                        (num_calls['lost'] + num_calls['voicemails']) / this_row['I/C Presented'])
                    this_row['Average Incoming Duration'] = self.sla_report[client].get_avg_call_duration()
                    this_row['Average Wait Answered'] = self.sla_report[client].get_avg_wait_answered()
                    if client == 7591:
                        print(self.sla_report[client].get_avg_wait_answered())
                    this_row['Average Wait Lost'] = self.sla_report[client].get_avg_lost_duration()
                    this_row['Calls Ans Within 15'] = ticker_stats[15]
                    this_row['Calls Ans Within 30'] = ticker_stats[30]
                    this_row['Calls Ans Within 45'] = ticker_stats[45]
                    this_row['Calls Ans Within 60'] = ticker_stats[60]
                    this_row['Calls Ans Within 999'] = ticker_stats[999]
                    this_row['Call Ans + 999'] = ticker_stats[999999]
                    this_row['Longest Waiting Answered'] = self.sla_report[client].get_longest_answered()
                    try:
                        this_row['PCA'] = ((ticker_stats[15] + ticker_stats[30]) / num_calls['answered'])
                    except ZeroDivisionError:
                        this_row['PCA'] = 0

                    self.accumulate_total_row(this_row, total_row)
                    self.add_row(this_row)
                else:
                    self.add_row(this_row)
            self.finalize_total_row(total_row)
            self.add_row(total_row)
            self.fr.name_rows_by_column(0)

    def process_report2(self):
        '''

            :return:
        '''
        if self.fr.finished:
            return
        else:
            # TODO extend this for clarity possible client in final_report_clients or something
            for row_name in self.fr.rownames:
                client_number = int(row_name)
                try:
                    num_calls = self.sla_report[client_number].get_number_of_calls()
                except KeyError:
                    pass
                else:
                    ticker_stats = self.sla_report[client_number].get_call_ticker()
                    self.fr[row_name, 'I/C Presented'] = sum(num_calls.values())
                    self.fr[row_name, 'I/C Answered'] = num_calls['answered']
                    self.fr[row_name, 'I/C Lost'] = num_calls['lost']
                    self.fr[row_name, 'Voice Mails'] = num_calls['voicemails']
                    self.fr[row_name, 'Incoming Answered (%)'] = self.safe_div(num_calls['answered'],
                                                                               sum(num_calls.values()))
                    self.fr[row_name, 'Incoming Lost (%)'] = self.safe_div(num_calls['lost'] + num_calls['voicemails'],
                                                                           sum(num_calls.values()))
                    self.fr[row_name, 'Average Incoming Duration'] = self.sla_report[
                        client_number].get_avg_call_duration()
                    self.fr[row_name, 'Average Wait Answered'] = self.sla_report[client_number].get_avg_wait_answered()
                    self.fr[row_name, 'Average Wait Lost'] = self.sla_report[client_number].get_avg_lost_duration()
                    self.fr[row_name, 'Calls Ans Within 15'] = ticker_stats[15]
                    self.fr[row_name, 'Calls Ans Within 30'] = ticker_stats[30]
                    self.fr[row_name, 'Calls Ans Within 45'] = ticker_stats[45]
                    self.fr[row_name, 'Calls Ans Within 60'] = ticker_stats[60]
                    self.fr[row_name, 'Calls Ans Within 999'] = ticker_stats[999]
                    self.fr[row_name, 'Call Ans + 999'] = ticker_stats[999999]
                    self.fr[row_name, 'PCA'] = self.safe_div(ticker_stats[15] + ticker_stats[30],
                                                             num_calls['answered'])
                    self.fr[row_name, 'Longest Waiting Answered'] = self.sla_report[
                        client_number].get_longest_answered()

    def save(self, user_string=None):
        if self.fr.finished:
            return
        else:
            # TODO build this into manifest E.g. tgt delivery
            self.validate_final_report()
            the_file = user_string if user_string else r'{0}_Incoming DID Summary'.format(self.dates.strftime("%m%d%Y"))
            super().save(user_string=the_file)
            network_dir = r'M:\Help Desk\Daily SLA Report\{yr}'.format(yr=self.dates.strftime('%Y'))
            self.change_dir(network_dir)
            try:
                self.fr.save_report(user_string=the_file)
            except OSError:
                print('passing os_error')

    '''
    Report Filters by row
    '''

    def blank_row_filter(self, row):
        result = [element for element in str(row[3]) if element != '']
        return len(result) == 0

    def answered_filter(self, row):
        try:
            answered = row[-5]
        except ValueError:
            answered = False
        return answered

    def inbound_call_filter(self, row):
        return row[0] not in ('Inbound', 'Call Direction')

    def zero_duration_filter(self, row):
        result = [element for element in row[-1] if element != '']
        return len(result) == 0

    def remove_internal_inbound_filter(self, row):
        return row[-2] == row[-3]

    '''
    Final Report Fnc by column
    '''

    def sum(self, col):
        return sum(col)

    def floor_div_weighted(self, col1=(), col2=(), col3=()):
        return self.floor_div(col1=[a * b for a, b in zip(col1, col2)], col2=col3)

    def floor_div(self, col1=(), col2=()):
        try:
            return operator.floordiv(sum(col1), sum(col2))
        except ZeroDivisionError:
            return 0

    def true_div_comb(self, col1=(), col2=(), col3=()):
        return self.true_div(col1=col1 + col2, col2=col3)

    def true_div(self, col1=(), col2=()):
        try:
            return operator.truediv(sum(col1), sum(col2))
        except ZeroDivisionError:
            return 0

    def max_val(self, col):
        return max(col)

    '''
    Utilities Section
    '''

    def remove_duplicate_calls(self):
        internal_parties = self.src_files[r'Group Abandoned Calls'].column['Internal Party']
        external_parties = self.src_files[r'Group Abandoned Calls'].column['External Party']
        start_times = self.src_files[r'Group Abandoned Calls'].column['Start Time']
        end_times = self.src_files[r'Group Abandoned Calls'].column['End Time']
        potential_duplicates = self.find_non_distinct(external_parties)
        for duplicate in potential_duplicates:
            call_index = self.find(external_parties, duplicate)
            first_call = call_index[0]
            first_call_client = internal_parties[first_call]
            first_call_end_time = parse(end_times[first_call])
            for call in range(1, len(call_index)):
                next_call = call_index[call]
                next_call_client = internal_parties[next_call]
                next_call_start_time = parse(start_times[next_call])
                time_delta = next_call_start_time - first_call_end_time
                if time_delta < timedelta(minutes=1) and first_call_client == next_call_client:
                    del self.src_files[r'Group Abandoned Calls'].row[next_call]

    def remove_calls_less_than_twenty_seconds(self):
        call_durations = self.src_files[r'Group Abandoned Calls'].column['Call Duration']
        for call in call_durations:
            if self.get_sec(call) < 20:
                row_index = call_durations.index(call)
                del self.src_files[r'Group Abandoned Calls'].row[row_index]

    def safe_div(self, num, denom):
        rtn_val = 0
        try:
            rtn_val = num / denom
        except ZeroDivisionError:
            pass
        return rtn_val

    def correlate_event_data(self, src_list, list_to_correlate, key):
        event_list = super().correlate_list_time_data(src_list, list_to_correlate, key)
        return sum(v for v in event_list)

    def validate_final_report(self):
        for row in self.fr.rownames:
            ticker_total = 0
            answered = self.fr[row, 'I/C Answered']
            ticker_total += self.fr[row, 'Calls Ans Within 15']
            ticker_total += self.fr[row, 'Calls Ans Within 30']
            ticker_total += self.fr[row, 'Calls Ans Within 45']
            ticker_total += self.fr[row, 'Calls Ans Within 60']
            ticker_total += self.fr[row, 'Calls Ans Within 999']
            ticker_total += self.fr[row, 'Call Ans + 999']
            if answered != ticker_total:
                raise ValueError('Validation error ->'
                                 'ticker total != answered for: '
                                 '{0}'.format(row[0]))

    def add_row(self, a_row):
        self.format_row(a_row)
        self.fr.row += self.return_row_as_list(a_row)

    def format_row(self, row):
        row['Average Incoming Duration'] = self.convert_time_stamp(row['Average Incoming Duration'])
        row['Average Wait Answered'] = self.convert_time_stamp(row['Average Wait Answered'])
        row['Average Wait Lost'] = self.convert_time_stamp(row['Average Wait Lost'])
        row['Longest Waiting Answered'] = self.convert_time_stamp(row['Longest Waiting Answered'])
        row['Incoming Answered (%)'] = '{0:.1%}'.format(row['Incoming Answered (%)'])
        row['Incoming Lost (%)'] = '{0:.1%}'.format(row['Incoming Lost (%)'])
        row['PCA'] = '{0:.1%}'.format(row['PCA'])

    def return_row_as_list(self, row):
        return [row['Label'],
                row['I/C Presented'],
                row['I/C Answered'],
                row['I/C Lost'],
                row['Voice Mails'],
                row['Incoming Answered (%)'],
                row['Incoming Lost (%)'],
                row['Average Incoming Duration'],
                row['Average Wait Answered'],
                row['Average Wait Lost'],
                row['Calls Ans Within 15'],
                row['Calls Ans Within 30'],
                row['Calls Ans Within 45'],
                row['Calls Ans Within 60'],
                row['Calls Ans Within 999'],
                row['Call Ans + 999'],
                row['Longest Waiting Answered'],
                row['PCA']]

    def accumulate_total_row(self, row, tr):
        tr['I/C Presented'] += row['I/C Presented']
        tr['I/C Answered'] += row['I/C Answered']
        tr['I/C Lost'] += row['I/C Lost']
        tr['Voice Mails'] += row['Voice Mails']
        tr['Average Incoming Duration'] += row['Average Incoming Duration'] * row['I/C Answered']
        tr['Average Wait Answered'] += row['Average Wait Answered'] * row['I/C Answered']
        tr['Average Wait Lost'] += row['Average Wait Lost'] * row['I/C Lost']
        tr['Calls Ans Within 15'] += row['Calls Ans Within 15']
        tr['Calls Ans Within 30'] += row['Calls Ans Within 30']
        tr['Calls Ans Within 45'] += row['Calls Ans Within 45']
        tr['Calls Ans Within 60'] += row['Calls Ans Within 60']
        tr['Calls Ans Within 999'] += row['Calls Ans Within 999']
        tr['Call Ans + 999'] += row['Call Ans + 999']
        if tr['Longest Waiting Answered'] < row['Longest Waiting Answered']:
            tr['Longest Waiting Answered'] = row['Longest Waiting Answered']

    def finalize_total_row(self, tr):
        if tr['I/C Presented'] > 0:
            tr['Incoming Answered (%)'] = operator.truediv(tr['I/C Answered'],
                                                           tr['I/C Presented'])
            tr['Incoming Lost (%)'] = operator.truediv(tr['I/C Lost'] + tr['Voice Mails'],
                                                       tr['I/C Presented'])
            tr['PCA'] = operator.truediv(tr['Calls Ans Within 15'] + tr['Calls Ans Within 30'],
                                         tr['I/C Presented'])
            if tr['I/C Answered'] > 0:
                tr['Average Incoming Duration'] = operator.floordiv(tr['Average Incoming Duration'],
                                                                    tr['I/C Answered'])
                tr['Average Wait Answered'] = operator.floordiv(tr['Average Wait Answered'],
                                                                tr['I/C Answered'])
            if tr['I/C Lost'] > 0:
                tr['Average Wait Lost'] = operator.floordiv(tr['Average Wait Lost'],
                                                            tr['I/C Lost'])

    def make_verbose_dict(self):
        return dict((value.name, key) for key, value in self.clients.items())

    def merge_sheets(self, workbook):
        merged_sheet = pe.Sheet()
        abandon_filter = pe.RowValueFilter(self.abandon_group_row_filter)
        first_sheet = True
        for sheet in workbook:
            sheet.filter(abandon_filter)
            if first_sheet:
                merged_sheet.row += sheet
                first_sheet = False
            else:
                sheet.name_columns_by_row(0)
                merged_sheet.row += sheet
        return merged_sheet

    def abandon_group_row_filter(self, row):
        unique_cell = row[0].split(' ')
        return unique_cell[0] != 'Call'

    def find_non_distinct(self, lst):
        icount = {}
        for i in lst:
            icount[i] = icount.get(i, 0) + 1
        return {k: v for k, v in icount.items() if v > 1}

    def group_cid_by_client(self, report):
        report_details = defaultdict(list)
        for row_name in report.rownames:
            try:
                client = int(report[row_name, 'Internal Party'])
            except ValueError:
                client = self.handle_read_value_error(row_name)
            finally:
                report_details[client].append(row_name)
        return report_details

    def handle_read_value_error(self, call_id):
        sheet = self.src_files[r'Cradle to Grave'][call_id.replace(':', ' ')]
        hunt_index = sheet.column['Event Type'].index('Ringing')
        return sheet.column['Receiving Party'][hunt_index]

    def get_voicemails(self):
        voicemail_file_path = r'{0}\{1}'.format(self.src_doc_path,
                                                r'{}voicemail.txt'.format(self.dates.strftime('%m_%d_%Y')))
        try:
            self.read_voicemail_data(voicemail_file_path)
        except FileNotFoundError:
            self.make_voicemail_data()
            self.write_voicemail_data(voicemail_file_path)

    def read_voicemail_data(self, voicemail_file_path):
        with open(voicemail_file_path) as f:
            content = f.readlines()
            for item in content:
                client_info = item.replace('\n', '').split(',')
                self.src_files[r'Voice Mail'][client_info[0]] = client_info[1:]

    def retrieve_voicemail_emails(self):
        from automated_sla_tool.src.Outlook import Outlook
        mail = Outlook(self.dates, self.login_type)
        mail.login(self.user_name, self.password)
        mail.inbox()
        read_ids = mail.read_ids()
        return mail.get_voice_mail_info(read_ids)

    def retrieve_voicemail_cradle(self):
        voice_mail_dict = defaultdict(list)
        for call_id_page in self.src_files[r'Cradle to Grave']:
            try:
                col_index = call_id_page.colnames
                sheet_events = call_id_page.column['Event Type']
            except IndexError:
                pass
            else:
                if 'Voicemail' in sheet_events:
                    voicemail_index = sheet_events.index('Voicemail')
                    real_voicemail = call_id_page[
                                         voicemail_index, col_index.index('Receiving Party')] in self.clients_verbose
                    if real_voicemail:
                        voicemail = {}
                        receiving_party = call_id_page[voicemail_index, col_index.index('Receiving Party')]
                        telephone_number = str(call_id_page[voicemail_index, col_index.index('Calling Party')])[-4:]
                        if telephone_number.isalpha():
                            telephone_number = str(call_id_page[0, col_index.index('Calling Party')])[-4:]
                        call_time = call_id_page[voicemail_index, col_index.index('End Time')]
                        voicemail['call_id'] = call_id_page.name
                        voicemail['number'] = telephone_number
                        voicemail['call_time'] = call_time
                        voice_mail_dict[receiving_party].append(voicemail)
            print('read {} successfully.'.format(call_id_page.name))
        return voice_mail_dict

    def make_voicemail_data(self):
        e_vm = self.retrieve_voicemail_emails()
        c_vm = self.retrieve_voicemail_cradle()
        for client, e_list in e_vm.items():
            c_list = c_vm.get(client, None)
            if c_list is None:
                self.src_files[r'Voice Mail'][client] = ['orphan-{}'.format(i.split(' + ')[0]) for i in e_list]
            else:
                for evoicemail in e_list:
                    email_number, email_time = evoicemail.split(' + ')
                    matched_call = next((l for l in c_list if l['number'] == email_number), None)
                    if matched_call is None:
                        self.src_files[r'Voice Mail'][client].append('orphan-{}'.format(email_number))
                    else:
                        email_datetime = parse(email_time)
                        cradle_datetime = parse(matched_call['call_time'])
                        difference = cradle_datetime - email_datetime
                        if difference < timedelta(seconds=31):
                            self.src_files[r'Voice Mail'][client].append(matched_call['call_id'])

    def write_voicemail_data(self, voicemail_file_path):
        text_file = open(voicemail_file_path, 'w')
        for voicemail_group in self.src_files[r'Voice Mail'].items():
            text_string = '{0},{1}\n'.format(voicemail_group[0], ",".join(voicemail_group[1]))
            text_file.write(text_string)
        text_file.close()

    def get_client_settings(self):
        client = namedtuple('client_settings', 'name full_service')
        settings_file = r'{0}\{1}'.format(self.path, r'settings\report_settings.xlsx')
        settings = pe.get_sheet(file_name=settings_file, name_columns_by_row=0)
        return_dict = OrderedDict()
        is_weekend = self.dates.isoweekday() in (6, 7)
        for row in range(settings.number_of_rows()):
            is_fullservice = self.str_to_bool(settings[row, 'Full Service'])
            if is_weekend:
                if is_fullservice is True:
                    this_client = client(name=settings[row, 'Client Name'],
                                         full_service=is_fullservice)
                    return_dict[settings[row, 'Client Number']] = this_client
            else:
                this_client = client(name=settings[row, 'Client Name'],
                                     full_service=is_fullservice)
                return_dict[settings[row, 'Client Number']] = this_client
        return return_dict


class Client:
    earliest_call = time(hour=7)
    latest_call = time(hour=20)

    def __init__(self, **kwargs):
        # def __init__(self, name=None,
        #              answered_calls=None,
        #              lost_calls=None,
        #              voicemail=None,
        #              full_service=False):
        self.name = kwargs.get('name', None)
        self.full_service = kwargs.get('full_service', False)
        self.answered_calls = kwargs.get('answered_calls', [])
        self.lost_calls = kwargs.get('lost_calls', [])
        self.voicemails = kwargs.get('voicemail', [])
        self.remove_voicemails()
        self.longest_answered = 0
        self.call_details_duration = timedelta(seconds=0)
        self.abandon_group_duration = timedelta(seconds=0)
        self.wait_answered = []
        self.call_details_ticker = BucketDict(
            {(-1, 15): 0, (15, 30): 0, (30, 45): 0, (45, 60): 0, (60, 999): 0, (999, 999999): 0}
        )

    def __str__(self):
        print('name: {}'.format(self.name))
        print('ans: {}'.format(self.answered_calls))
        print('lost: {}'.format(self.lost_calls))
        print('vm: {}'.format(self.voicemails))

    def remove_voicemails(self):
        '''
        Should never find a voicemail call since they're excluded when Call Details loads
        :return:
        '''
        for voicemail in self.voicemails:
            if voicemail in self.lost_calls:
                self.lost_calls.remove(voicemail)
            if voicemail in self.answered_calls:
                self.answered_calls.remove(voicemail)

    def is_empty(self):
        return len(self.answered_calls) == 0 and len(self.lost_calls) == 0 and len(self.voicemails) == 0

    def no_answered(self):
        return len(self.answered_calls) == 0

    def no_lost(self):
        return len(self.lost_calls) == 0

    def convert_datetime_seconds(self, datetime_obj):
        return 60 * (datetime_obj.hour * 60) + datetime_obj.minute * 60 + datetime_obj.second

    def extract_call_details(self, call_details):
        self.call_details_duration = self.read_report(report=call_details,
                                                      call_group=self.answered_calls,
                                                      call_ticker=self.call_details_ticker,
                                                      wait_answered=self.wait_answered)

    def extract_abandon_group_details(self, abandon_group):
        self.abandon_group_duration = self.read_report(report=abandon_group,
                                                       call_group=self.lost_calls)

    def read_report(self, report=None, call_group=None, call_ticker=None, wait_answered=None):
        duration_counter = timedelta(seconds=0)
        for call_id in reversed(call_group):
            start_time = report[call_id, 'Start Time']
            if self.valid_time(parse(start_time)) or self.full_service:
                duration_datetime = parse(report[call_id, 'Call Duration'])
                converted_seconds = self.convert_datetime_seconds(duration_datetime)
                if report.name == 'call_details' or converted_seconds >= 20:
                    duration_counter += timedelta(seconds=converted_seconds)
                    if call_ticker is not None:
                        hold_duration = parse(report[call_id, 'Wait Time'])
                        if self.name == 7591:
                            print(hold_duration)
                        hold_duration_seconds = self.convert_datetime_seconds(hold_duration)
                        wait_answered.append(hold_duration_seconds)
                        call_ticker.add_range_item(hold_duration_seconds)
                        if hold_duration_seconds > self.longest_answered:
                            self.longest_answered = hold_duration_seconds
                        # if self.name == 7591:
                        #     print('here')
                else:
                    call_group.remove(call_id)
            else:
                call_group.remove(call_id)
        return duration_counter

    def valid_time(self, call_datetime):
        # TODO: call ID are ordered -> check first and last instead of whole call_ID list
        call_time = call_datetime.time()
        return self.earliest_call <= call_time <= self.latest_call

    def get_longest_answered(self):
        return self.longest_answered

    def get_avg_call_duration(self):
        return self.get_avg_duration(current_duration=self.call_details_duration.total_seconds(),
                                     call_group=self.answered_calls)

    def get_avg_lost_duration(self):
        return self.get_avg_duration(current_duration=self.abandon_group_duration.total_seconds(),
                                     call_group=self.lost_calls)

    def get_avg_wait_answered(self):
        if self.name == 7591:
            print(self.wait_answered)
        return self.get_avg_duration(current_duration=sum(self.wait_answered),
                                     call_group=self.wait_answered)

    def get_avg_duration(self, current_duration=None, call_group=None):
        return_value = current_duration
        try:
            return_value //= len(call_group)
        except ZeroDivisionError:
            pass
        return int(return_value)

    def get_number_of_calls(self):
        return {
            'answered': len(self.answered_calls),
            'lost': len(self.lost_calls),
            'voicemails': len(self.voicemails)
        }

    def chop_microseconds(self, delta):
        return delta - timedelta(microseconds=delta.microseconds)

    def get_call_ticker(self):
        return self.call_details_ticker

    def is_full_service(self):
        return self.full_service
