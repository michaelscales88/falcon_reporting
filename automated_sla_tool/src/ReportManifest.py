class ReportManifest(object):

    default_hdr = ['I\'m', 'default header', 'set my', 'ReportManifest', 'header']
    default_rows = ['I\'m', 'default rows', 'set my', 'ReportManifest', 'rows']

    def __init__(self, **kwargs):
        super().__init__()
        self._tgt_header = kwargs.get('header', ReportManifest.default_hdr)
        self._tgt_rows = kwargs.get('rows', ReportManifest.default_rows)

    @property
    def tgt_header(self):
        return self._tgt_header

    @property
    def tgt_rows(self):
        return self._tgt_rows
