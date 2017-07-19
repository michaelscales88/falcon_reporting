from datetime import timedelta, time
from pyexcel import Sheet
from collections import OrderedDict


def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)


def match(record_list, match_val=None):
    matched_records = []
    for record in record_list:
        # Check match conditions
        match0 = (
            match_val.get('Event Summary').get('4', timedelta(0))
            == record.get('Event Summary').get('4', timedelta(0))
            == timedelta(0)
        )
        match1 = match_val.get('Unique Id2') == record.get('Unique Id2')
        match2 = match_val.get('Unique Id1') == record.get('Unique Id1')
        match3 = (record.get('Start Time') - match_val.get('End Time')) < timedelta(seconds=61)

        all_matched = all(
            [
                match0,
                match1,
                match2,
                match3
            ]
        )

        if all_matched:
            matched_records.append(record.get('id'))

    return matched_records


def sla_report(records, client_list=None):
    print('sla_report')
    output_headers = [
        'I/C Presented',
        'I/C Answered',
        'I/C Lost',
        'Voice Mails',
        'Incoming Answered (%)',
        'Incoming Lost (%)',
        'Average Incoming Duration',
        'Average Wait Answered',
        'Average Wait Lost',
        'Calls Ans Within 15',
        'Calls Ans Within 30',
        'Calls Ans Within 45',
        'Calls Ans Within 60',
        'Calls Ans Within 999',
        'Call Ans + 999',
        'Longest Waiting Answered',
        'PCA'
    ]

    test_output = Sheet(
        colnames=output_headers
    )
    client_list.append('Summary')
    row_names = client_list
    try:
        for row_name in row_names:
            additional_row = OrderedDict()
            additional_row[str(row_name)] = [
                0, 0, 0, 0, 0, 0, timedelta(0), timedelta(0), timedelta(0), 0, 0, 0, 0, 0, 0, timedelta(0), 0
            ]
            test_output.extend_rows(additional_row)
    except KeyError:
        from json import dumps
        print(dumps(client_list, indent=4))
        raise

    # Filter Step
    try:
        records = [records[key] for key in sorted(records.keys())]  # create order of calls
        for x in range(0, len(records)):
            match_record = records[x]
            matches = match(records[x + 1:], match_val=match_record)
            if (
                    len(matches) > 1
                    and (match_record.get('End Time') - match_record.get('Start Time') > timedelta(seconds=20))
                    and match_record.get('Event Summary').get('10', timedelta(0)) == timedelta(0)
            ):
                for a_match in matches:
                    for i, o in enumerate(records):
                        if o.get('id') == a_match:
                            del records[i]
                            break

    except IndexError:
        # x has moved past the end of the list of remaining records
        pass

    # Process Step
    for record in records:
        print('passing records')
        row_name = str(record.get('Unique Id1')).replace("'", '')  # This is how we bind our client user
        print(row_name)
        print(time(hour=7) <= record.get('Start Time').time() <= time(hour=19))
        print(row_name in test_output.rownames)
        if row_name in test_output.rownames and time(hour=7) <= record.get('Start Time').time() <= time(hour=19):
            call_duration = record.get('End Time') - record.get('Start Time')
            talking_time = record.get('Event Summary').get('4', timedelta(0))
            voicemail_time = record.get('Event Summary').get('10', timedelta(0))
            hold_time = sum(
                [record.get('Event Summary').get(event_type, timedelta(0)) for event_type in ('5', '6', '7')],
                timedelta(0)
            )
            wait_duration = call_duration - talking_time - hold_time
            # DO the rest of the output work
            if talking_time > timedelta(0):
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Answered'] += 1
                test_output[row_name, 'Average Incoming Duration'] += talking_time
                test_output[row_name, 'Average Wait Answered'] += wait_duration

                # Adding to Summary
                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'I/C Answered'] += 1
                test_output['Summary', 'Average Incoming Duration'] += talking_time
                test_output['Summary', 'Average Wait Answered'] += wait_duration

                # Qualify calls by duration
                if wait_duration <= timedelta(seconds=15):
                    test_output[row_name, 'Calls Ans Within 15'] += 1
                    test_output['Summary', 'Calls Ans Within 15'] += 1

                elif wait_duration <= timedelta(seconds=30):
                    test_output[row_name, 'Calls Ans Within 30'] += 1
                    test_output['Summary', 'Calls Ans Within 30'] += 1

                elif wait_duration <= timedelta(seconds=45):
                    test_output[row_name, 'Calls Ans Within 45'] += 1
                    test_output['Summary', 'Calls Ans Within 45'] += 1

                elif wait_duration <= timedelta(seconds=60):
                    test_output[row_name, 'Calls Ans Within 60'] += 1
                    test_output['Summary', 'Calls Ans Within 60'] += 1

                elif wait_duration <= timedelta(seconds=999):
                    test_output[row_name, 'Calls Ans Within 999'] += 1
                    test_output['Summary', 'Calls Ans Within 999'] += 1

                else:
                    test_output[row_name, 'Call Ans + 999'] += 1
                    test_output['Summary', 'Call Ans + 999'] += 1

                if wait_duration > test_output[row_name, 'Longest Waiting Answered']:
                    test_output[row_name, 'Longest Waiting Answered'] = wait_duration

                if wait_duration > test_output['Summary', 'Longest Waiting Answered']:
                    test_output['Summary', 'Longest Waiting Answered'] = wait_duration

            elif voicemail_time > timedelta(seconds=20):
                # if record.unique_id1 == test_client:
                #     print('I am a voice mail call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'Voice Mails'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'Voice Mails'] += 1
                test_output['Summary', 'Average Wait Lost'] += call_duration

            elif call_duration > timedelta(seconds=20):
                # if record.unique_id1 == test_client:
                #     print('I am a lost call', record.id)
                test_output[row_name, 'I/C Presented'] += 1
                test_output[row_name, 'I/C Lost'] += 1
                test_output[row_name, 'Average Wait Lost'] += call_duration

                test_output['Summary', 'I/C Presented'] += 1
                test_output['Summary', 'I/C Lost'] += 1
                test_output['Summary', 'Average Wait Lost'] += call_duration

            else:
                print('passed')
                pass

    # Finalize step
    for row_name in test_output.rownames:
        row_name = str(row_name)
        try:
            test_output[row_name, 'Incoming Answered (%)'] = '{0:.1%}'.format(
                test_output[row_name, 'I/C Answered'] / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'Incoming Answered (%)'] = 1.0

        try:
            test_output[row_name, 'Incoming Lost (%)'] = '{0:.1%}'.format(
                (test_output[row_name, 'I/C Lost'] + test_output[row_name, 'Voice Mails'])
                / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'Incoming Lost (%)'] = 0.0

        try:
            test_output[row_name, 'Average Incoming Duration'] = str(
                chop_microseconds(test_output[row_name, 'Average Incoming Duration'] / test_output[row_name, 'I/C Answered'])
            )
        except ZeroDivisionError:
            test_output[row_name, 'Average Incoming Duration'] = '0:00:00'

        try:
            test_output[row_name, 'Average Wait Answered'] = str(
                chop_microseconds(test_output[row_name, 'Average Wait Answered'] / test_output[row_name, 'I/C Answered'])
            )
        except ZeroDivisionError:
            test_output[row_name, 'Average Wait Answered'] = '0:00:00'

        try:
            test_output[row_name, 'Average Wait Lost'] = str(
                chop_microseconds(test_output[row_name, 'Average Wait Lost'] / test_output[row_name, 'I/C Lost'])
            )
        except ZeroDivisionError:
            test_output[row_name, 'Average Wait Lost'] = '0:00:00'

        test_output[row_name, 'Longest Waiting Answered'] = str(
            chop_microseconds(test_output[row_name, 'Longest Waiting Answered'])
        )

        try:
            test_output[row_name, 'PCA'] = '{0:.1%}'.format(
                (test_output[row_name, 'Calls Ans Within 15'] + test_output[row_name, 'Calls Ans Within 30'])
                / test_output[row_name, 'I/C Presented']
            )
        except ZeroDivisionError:
            test_output[row_name, 'PCA'] = 0.0

    return test_output
