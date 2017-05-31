from platform import system

from app.src.factory import manifest_reader

# if system() in ('Darwin', 'Linux'):
#     from app.src.factory import manifest_reader
# else:
#     from falcon_reporting.app.src.factory import manifest_reader


class ReportBuilder:

    def __init__(self, manifest=None):
        # initialize a Report
        self.config = manifest_reader(manifest)
        self._name = self.config['REPORT_NAME']
        self._exit_condition = True

    @property
    def name(self):
        return self._name

    def read(self):
        # Business end once the report is built and the methods to build the report are set up
        return self._exit_condition




