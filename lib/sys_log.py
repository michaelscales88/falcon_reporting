from logging import RootLogger
from os import getcwd, path, listdir
from .logger_settings import LoggerSettings


class SysLog(RootLogger):
    def __init__(self, parent):
        super().__init__(parent.__class__.__name__)
        self._data = {
            'settings': self.open_settings()
        }
        self.init_settings()

    def init_settings(self):
        for k, v in self._data['settings'].get_config('console_handler').items():
            print(k)
            print(v)
        for k, v in self._data['settings'].get_config('file_handler').items():
            print(k)
            print(v)
        for k, v in self._data['settings'].get_config('formatters').items():
            print(k)
            print(v)

    def open_settings(self):
        return LoggerSettings(self.settings_file)

    @property
    def settings_file(self):
        return path.join(self.settings_directory, '{f_name}.conf'.format(f_name=self.name))

    @property
    def settings_directory(self):
        settings_dir = None
        for part in listdir(getcwd()):
            if path.isdir(part) and 'settings' in listdir(part):
                settings_dir = part
                break
        return path.join(getcwd(), settings_dir, 'settings')
