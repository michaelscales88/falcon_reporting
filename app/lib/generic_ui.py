import inspect
import traceback
from logging import getLogger
from logging.config import dictConfig
from time import sleep
# from automated_sla_tool.utilities.LoggerSettings import LoggerSettings
# from automated_sla_tool.utilities.FinishedDecorator import FinishedDecorator as check_set
# from automated_sla_tool.utilities.StackedTracebackDecorator import StackedTracebackDecorator as tb_decorator


class GenericUi(object):

    _obj_set = False

    @check_set(_obj_set)
    def __init__(self, exclusions=None):
        super().__init__()
        self._data = {
            'finished': False,
            'object': None,
            'object_ui': None,
            'my_ui': None,
            'safe_mode': False,
            'exclusions': ['__init__', exclusions],
            'logger_settings': LoggerSettings(self.__class__.__name__)
        }
        # for key in self._data['logger_settings'].keys():
        #     print(key)
        #     print(self._data['logger_settings'][key])
        dictConfig(self._data['logger_settings'])
        self._logger = getLogger(self.__class__.__name__)
        self._logger.debug('foo')
        self._logger.info('bar')
        self._logger.warn('baz')
        # self._logger.setLevel(logging.INFO)

    def run(self):
        while not self.finished:
            try:
                self.ui()
            except Exception:
                sleep(.5)
                if self._logger:
                    print('i should make something obvious')
                    self._logger.info(traceback.format_exc())
                    self._logger.warn(traceback.format_exc())
                    print('did i?')
                else:
                    print('i passed')
                    pass

    def ui(self):
        my_ui = {'Quit': self.exit,
                 'Setmode Safe': self.toggle_safe_mode,
                 'Display UI': self.display_ui,
                 'raise':  'value_error'
                 }
        selection = dict(enumerate(sorted(my_ui.keys()), start=1))
        self.display_selection(selection)
        func = my_ui[selection[int(input('Make a selection: '))]]
        if func == 'value_error':
            print('i am raising an error')
            raise ValueError('test')
        return func()

    @property
    def finished(self):
        return self._data['finished']

    @property
    def object(self):
        return self._data['object']

    @object.setter
    @check_set(_obj_set)
    def object(self, raw_obj):
        try:
            self._data['object'] = raw_obj
            self._data['object_ui'] = dict(inspect.getmembers(raw_obj, predicate=inspect.ismethod))
        except Exception as e:
            raise SystemExit('Could not set object -> Aborting {err}'.format(err=e))
        else:
            for e in self._data['exclusions']:
                self._data['object_ui'].pop(e, None)
            GenericUi._obj_set = True

    def clear_obj(self):
        self._data['object'] = None
        self._data['object_ui'] = None
        GenericUi._obj_set = False

    def display_ui(self):
        return self.exc_fnc_safe_mode() if self._data['safe_mode'] else self.exc_fnc()

    def exc_fnc(self):
        selection = dict(enumerate(sorted(self._data['object_ui'].keys()), start=1))
        self.display_selection(selection)
        func = self._data['object_ui'][selection[int(input('Make a selection: '))]]
        return func()

    def toggle_safe_mode(self):
        self._data['safe_mode'] = not self._data['safe_mode']

    def exit(self):
        self._data['finished'] = True

    @tb_decorator()
    def exc_fnc_safe_mode(self):
        return self.exc_fnc()

    def display_selection(self, selection):
        print('GenericUI: {0}\n'
              'Current Mode: {1}'.format(self._data['object'].__class__.__name__,
                                         ('Not Active', 'Safe Active')[self._data['safe_mode']]), flush=True)
        print("\n".join(['{k}: {v}'.format(k=k, v=v) for k, v in sorted(selection.items())]))

    def show_logger_settings(self):
        for k, v in self._data['logger_settings'].get_config('console_handler').items():
            print(k)
            print(v)
        for k, v in self._data['logger_settings'].get_config('file_handler').items():
            print(k)
            print(v)
        for k, v in self._data['logger_settings'].get_config('formatters').items():
            print(k)
            print(v)

    def __del__(self):
        print('quitting')

    def __getitem__(self, item):
        return self._data.get(item, None)
