from json import dumps
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


from .report_utilities import ReportUtilities
from .data_worker import DataWorker


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
        self._worker = DataWorker()
        self._connection_pool = {}
        self.Session = sessionmaker()

    # @property
    # def worker(self):
    #     return self._worker
    #
    # @property
    # def job(self):
    #     return self._job
    #
    # @job.setter
    # def job(self, obj):
    #     if self.job is None:
    #         self._job = obj
    #
    # def queue_job(self, next_obj):
    #     # Idea
    #     pass
    #
    # def cache(self, key):
    #     try:
    #         return_dict = {
    #             row: DataCenter.call(sheet=self[self.job][key], **cmds) for row, cmds in self.worker[None]
    #             }
    #     except KeyError:
    #         self[self.job] = self.get_src(self.job)
    #         return_dict = {
    #             row: DataCenter.call(sheet=self[self.job][key], **cmds) for row, cmds in self.worker[None]
    #             }
    #     return return_dict
        # return {
        #     row: DataCenter.call(sheet=self.job[key], **cmds) for row, cmds in self.worker
        #     # row: cmds['fn'](self.job[key], **cmds['parameters']) for row, cmds in self.worker
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

    @staticmethod
    def print_record(record, **kwargs):
        print(dumps(record, **kwargs))

    def make_session(self, target):
        connection = self.get_connection(target)
        meta = MetaData()
        self.Session.configure(bind=connection)
        meta.reflect(bind=connection)
        return self.Session()

    def get_connection(self, target):
        """Get an engine configured to make an instance of a Session"""
        connection = self._connection_pool.get(
            target,
            self.make_connection(target)
        )
        return connection

    def make_connection(self, target):
        print('Making a connection to', target)
        self._connection_pool[target] = create_engine(target, echo=True)
        return self._connection_pool[target]
