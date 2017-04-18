from datetime import timedelta
from json import dumps


from automated_sla_tool.src.ReportUtilities import ReportUtilities
from automated_sla_tool.src.DataWorker import DataWorker


class DataCenter(object):

    # TODO needs some form of transaction log/manifest
    # TODO push all Report loading and preparing into DataCenter
    # Reports should be able to request data and have DataCenter prepare and make available
    def __init__(self):
        # this would actually be a dB
        # dB should probably be table like:
        # columns: report_type
        # row as date: report, report, report
        # DataWorker can fill the report for any report it knows how to make
        self.matrix = {}    # This should be a list/matrix 365 days by how many reports **linked list**??
        self.json_layer = {}
        self._job = None
        self.util = ReportUtilities()
        self._worker = None

    @property
    def worker(self):
        return self._worker

    @property
    def job(self):
        return self._job
        
    @job.setter
    def job(self, obj):
        if self.job is None:
            # self._job = obj.src_files[r'Cradle to Grave']
            print(obj)
            self._job = obj
            self._worker = DataWorker(target=obj)

    def queue_job(self, next_obj):
        # Idea
        pass

    def cache(self, key):
        try:
            return_dict = {
                row: DataCenter.call(sheet=self[self.job][key], **cmds) for row, cmds in self.worker
                }
        except KeyError:
            self[self.job] = self.get_src(self.job)
            return_dict = {
                row: DataCenter.call(sheet=self[self.job][key], **cmds) for row, cmds in self.worker
                }
        return return_dict
        # return {
        #     row: DataCenter.call(sheet=self.job[key], **cmds) for row, cmds in self.worker
        #     # row: cmds['fn'](self.job[key], **cmds['parameters']) for row, cmds in self.worker
        # }
        # return {
        #     'Call Duration': sum([item for item in self.doc[key].column['Event Duration'] if isinstance(item, timedelta)],
        #                          timedelta(0)),
        #     'Start Time': min(self.doc[key].column['Start Time']),
        #     'End Time': max(self.doc[key].column['End Time']),
        #     'Answered': 'Talking' in self.doc[key].column['Event Type'],
        #     'Talking Duration': sum(
        #         [e_time for e_type, e_time in
        #          zip(self.doc[key].column['Event Type'], self.doc[key].column['Event Duration']) if
        #          e_type == 'Talking' and isinstance(e_time, timedelta)],
        #         timedelta(0)
        #     ),
        #     'Receiving Party': self.util.phone_number(self.doc[key].column['Receiving Party'][0]),
        #     'Calling Party': self.util.phone_number(self.doc[key].column['Calling Party'][0]),
        #     'Call Direction': 1 if self.doc[key].column['Receiving Party'][0] == 'Ringing' else 2
        # }

    # Currently using settings file to control the extension for saving
    # TODO beef this up to identify the extension type from the file type
    # TODO 2: this + dispatched can be staticmethod-ed with a little work on AReport.save()
    def save(self, file, full_path):
        try:
            file.save_as(filename=full_path)
        except FileNotFoundError:
            self.util.make_dir(
                self.util.dir(full_path)
            )
            file.save_as(filename=full_path)
        except OSError:
            print('encountered an issue saving the file')

    # TODO this seems to be building a new worker each time
    @staticmethod
    def call(sheet=None, fn=None, parameters=None, behaviors=()):
        rtn_val = fn(sheet, **parameters)
        for behavior in behaviors:  # This should be simplified
            rtn_val = behavior(rtn_val)
        return rtn_val

    def dispatcher(self, file):
        for target, path in file.settings['Open Targets'].items():
            print('Trying to open:', target)
            self.util.start(path)

    def __repr__(self):
        return str(dumps(self.json_layer, indent=4, default=self.util.datetime_handler))

    def print_record(self, record):
        print(dumps(record, indent=4, default=self.util.datetime_handler))

    # TODO Modify this to use the __iter__ for the current src
    # e.g. return <current doc>.__iter__()
    def __iter__(self):
        for sheet_name in self.job.sheet_names():
            data = self.json_layer.get(
                sheet_name,
                self.cache(sheet_name)
            )
            yield sheet_name, data

    def __getitem__(self, item):
        return self.matrix[item]

    def __setitem__(self, key, value):
        self.matrix[key] = value

    # TODO: this should search Settings for 'Data Sources' and cycle until a data source is successfully retrieved
    def get_src(self, target):
        src_files = {}
        for f_name, file in self.util.load_data(target):
            src_files[f_name] = file
        return src_files['Cradle to Grave']
