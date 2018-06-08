import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread as gspread
import json
import time


def get_worksheet_list(doc_id):
    scope = ['https://spreadsheets.google.com/feeds']
    path = os.path.expanduser("key.json")

    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gspread.authorize(credentials)
    gfile = client.open_by_key(doc_id)
    worksheet_list = gfile.worksheets()

    return worksheet_list


def main():
    # 2018
    worksheets = get_worksheet_list('1-Qe_9u3qfniQm61f2QTyH8yP73RFiIz_dJXv7HdhDNM')
    del worksheets[0]
    columns = [chr(i) for i in range(67,67+22)]

    output_json_file = open('2018/前期.json', 'w')
    output_json_dict = {}

    total = len(worksheets) * len(columns)
    current = 0

    for worksheet in worksheets:
        time.sleep(1.3)

        day_dict = {}
        for column in columns:
            kpt = {}
            day = ''

            time.sleep(1.3)
            one_day_cells = worksheet.range('{}2:{}5'.format(column, column))

            for i, kptcell in enumerate(zip(one_day_cells, ['Day', 'K', 'P', 'T'])):
                if i == 0:
                    day = kptcell[0].value
                    continue

                splited = kptcell[0].value.split('\n')
                kpt[kptcell[1]] = list(filter(lambda x: x != '', splited))

            day_dict[day] = kpt

            current += 1
            print('{}/{}'.format(current, total))

        output_json_dict[worksheet.title] = day_dict

    json.dump(output_json_dict, output_json_file, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    output_json_file.close()


if __name__ == '__main__':
    main()
