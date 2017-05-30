import yaml
from pandas import DataFrame
from json import dumps


def manifest_reader(manifest=None):
    # Test Values
    with open('manifest_example.yml') as f:
        read_manifest = yaml.load(f)

    # read_manifest = {
    #     'REPORT_NAME': 'SLA Report',
    #     'HEADERS': [
    #         'I/C Presented',
    #         'I/C Answered',
    #         'I/C Lost',
    #         'Voice Mails',
    #         'Incoming Answered (%)',
    #         'Incoming Lost (%)',
    #         'Average Incoming Duration',
    #         'Average Wait Answered',
    #         'Average Wait Lost',
    #         'Calls Ans Within 15',
    #         'Calls Ans Within 30',
    #         'Calls Ans Within 45',
    #         'Calls Ans Within 60',
    #         'Calls Ans Within 999',
    #         'Call Ans + 999',
    #         'Longest Waiting Answered',
    #         'PCA'
    #     ],
    #     'BEHAVIORS': {
    #         'I/C Presented': ('Sum', 'int'),
    #         'I/C Answered': ('Sum', 'int'),
    #         'I/C Lost': ('Sum', 'int'),
    #         'Voice Mails': ('Sum', 'int'),
    #         'Incoming Answered (%)': ('Percentage', 'Decimal'),
    #         'Incoming Lost (%)': ('Percentage', 'Decimal'),
    #         'Average Incoming Duration': ('Average', 'time'),
    #         'Average Wait Answered': ('Average', 'time'),
    #         'Average Wait Lost': ('Average', 'time'),
    #         'Calls Ans Within 15': ('Sum', 'int'),
    #         'Calls Ans Within 30': ('Sum', 'int'),
    #         'Calls Ans Within 45': ('Sum', 'int'),
    #         'Calls Ans Within 60': ('Sum', 'int'),
    #         'Calls Ans Within 999': ('Sum', 'int'),
    #         'Call Ans + 999': ('Sum', 'int'),
    #         'Longest Waiting Answered': ('Limit', 'time'),
    #         'PCA': ('Percentage', 'Decimal')
    #     },
    #     'CONDITIONS': {
    #         'I/C Presented': ('event_type', '4', '0'),
    #         'I/C Answered': 'Sum',
    #         'I/C Lost': 'Sum',
    #         'Voice Mails': 'Sum',
    #         'Incoming Answered (%)': 'Percentage',
    #         'Incoming Lost (%)': 'Percentage',
    #         'Average Incoming Duration': 'Average',
    #         'Average Wait Answered': 'Average',
    #         'Average Wait Lost': 'Average',
    #         'Calls Ans Within 15': 'Sum',
    #         'Calls Ans Within 30': 'Sum',
    #         'Calls Ans Within 45': 'Sum',
    #         'Calls Ans Within 60': 'Sum',
    #         'Calls Ans Within 999': 'Sum',
    #         'Call Ans + 999': 'Sum',
    #         'Longest Waiting Answered': 'Max',
    #         'PCA': 'Percentage'
    #     },
    #     'SUMMARIZE': True,
    #     'CACHE_TEMPLATE': None          # Implement cache strategy for storing in internal connection
    # }
    return read_manifest

if __name__ == '__main__':
    data = manifest_reader()
    print(dumps(data, indent=4))


