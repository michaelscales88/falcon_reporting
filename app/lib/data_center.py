from json import dumps
from platform import system

from app.lib.report_utilities import ReportUtilities
from app.lib.data_worker import DataWorker
from app.lib.session_register import SessionRegistry


# if system() in ('Darwin', 'Linux'):
#     from app.lib.report_utilities import ReportUtilities
#     from app.lib.data_worker import DataWorker
#     from app.lib.session_register import SessionRegistry
# else:
#     from falcon_reporting.app.lib.report_utilities import ReportUtilities
#     from falcon_reporting.app.lib.data_worker import DataWorker
#     from falcon_reporting.app.lib.session_register import SessionRegistry


class DataCenter(object):

    # TODO needs some form of transaction log/manifest
    # TODO push all Report loading and preparing into DataCenter
    # Reports should be able to request data and have DataCenter prepare and make available
    def __init__(self):
        self.matrix = {}
        self.json_layer = {}
        self._job = None
        self._util = ReportUtilities()
        self._worker = DataWorker()
        self._registry = SessionRegistry()

    # Currently using settings file to control the extension for saving
    # TODO beef this up to identify the extension type from the file type
    # TODO 2: this + dispatched can be staticmethod-ed with a little work on AReport.save()
    def save(self, file, full_path):
        try:
            file.save_as(filename=full_path)
        except FileNotFoundError:
            self._util.make_dir(
                self._util.dir(full_path)
            )
            file.save_as(filename=full_path)
        except OSError:
            print('encountered an issue saving the file')

    # TODO this seems to be building a new worker each time
    @staticmethod
    def call(sheet=None, fn=None, parameters=None, behaviors=()):
        rtn_val = fn(sheet, **parameters)
        for behavior in behaviors:  # This might be a good spot for functools.wraps
            rtn_val = behavior(rtn_val)
        return rtn_val

    def dispatcher(self, file):
        for target, path in file.settings['Open Targets'].items():
            print('Trying to open:', target)
            self._util.start(path)

    @staticmethod
    def print_record(record, **kwargs):
        print(dumps(record, **kwargs))

    @staticmethod
    def yield_records(record, **kwargs):
        yield dumps(record, **kwargs)

    def get_session(self, target, **kwargs):
        return self._registry.get(target, **kwargs)

