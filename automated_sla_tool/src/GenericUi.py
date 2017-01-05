import inspect
import sys
import traceback
import logging
import logging.handlers
import logging.config
from os import path
from time import sleep
from glob import glob
from automated_sla_tool.src.FinishedDecorator import FinishedDecorator as check_set
from automated_sla_tool.src.StackedTracebackDecorator import StackedTracebackDecorator as tb_decorator
# from automated_sla_tool.src.SysLog import SysLog


class GenericUi(object):
    obj_set = False

    # _log_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), r'settings\logging2.conf')
    _logger = None  # SysLog(__name__, file_path=_log_path)
    # _logger.setLevel(logging.INFO)
    # LOG_FILENAME = '.\error_logs\{log}.error'.format(log=__name__)
    # # logging.basicConfig(level=logging.DEBUG)
    # err_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
    #                                                    maxBytes=256,
    #                                                    backupCount=2,
    #                                                    encoding='utf-8')
    # err_handler.setLevel(logging.ERROR)
    # info_handler = logging.StreamHandler()
    # info_handler.setLevel(logging.INFO)
    # _logger.addHandler(err_handler)
    # _logger.addHandler(info_handler)
    # log_file_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), r'settings\logging.conf')
    # logging.config.fileConfig(log_file_path)

    # create logger
    # print(__name__)
    # logger = logging.getLogger(__name__)

    # 'application' code
    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warn('warn message')
    # logger.error('error message')
    # logger.critical('critical message')

    @check_set(obj_set)
    def __init__(self, exclusions=None):
        super().__init__()
        self._finished = False
        self._obj = None
        self._ui = None
        self._safe = False
        self._exclusions = ['__init__', exclusions]

    def run(self):
        while not self.finished:
            try:
                self.display_ui()
            except Exception as e:
                if GenericUi._logger:
                    pass
                else:
                    print(traceback.format_exc())

    # def log(self):
    #     logfiles = glob('%s*' % GenericUi.LOG_FILENAME)
    #     print(logfiles)
    #
    #     for filename in logfiles:
    #         print('\nFile: {f}'.format(f=filename))
    #         outfile = None
    #         with open(filename, 'r', encoding='utf-8') as outfile:
    #             # print(outfile)
    #             for line in outfile:
    #                 print('{line}'.format(line=line.strip()))
    #                 # print('**File not Empty**\n')
    #         if outfile is None:
    #             print('**File Empty**\n')

    @property
    def finished(self):
        return self._finished

    @property
    def object(self):
        return self._obj

    @object.setter
    @check_set(obj_set)
    def object(self, raw_obj):
        obj = raw_obj
        obj_ui = {
            **dict(inspect.getmembers(obj, predicate=inspect.ismethod)),
            **{'Quit': self.exit,
               'Setmode Safe': self.toggle_safe_mode
               }  # 'log': self.log
        }
        for e in self._exclusions:
            obj_ui.pop(e, None)
        self._obj = obj
        self._ui = obj_ui
        GenericUi.obj_set = True

    def clear_obj(self):
        self._obj = None
        self._ui = None
        GenericUi.obj_set = False

    def display_ui(self):
        return self.exc_fnc_safe_mode() if self._safe else self.exc_fnc()

    def exc_fnc(self):
        selection = dict(enumerate(sorted(self._ui.keys()), start=1))
        self.display_selection(selection)
        func = self._ui[selection[int(input('Make a selection: '))]]
        return func()

    def toggle_safe_mode(self):
        self._safe = not self._safe

    def exit(self):
        self._finished = True

    @tb_decorator()
    def exc_fnc_safe_mode(self):
        return self.exc_fnc()

    def display_selection(self, selection):
        print('GenericUI: {0}\n'
              'Current Mode: {1}'.format(self._obj,
                                         ('Not Active', 'Safe Active')[self._safe]), flush=True)
        print("\n".join(['{k}: {v}'.format(k=k, v=v) for k, v in sorted(selection.items())]))

    def __del__(self):
        print('quitting')
