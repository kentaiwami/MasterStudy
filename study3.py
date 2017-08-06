import study
import MeCab
import CaboCha
from xml.etree import ElementTree
import re
import json


def create_data():
    worksheet_list = study.get_worksheet_list('15RsrnLlocEQhGd-m27nXL8CuJcTwIs3rG8mO1VGx6Gs')

    f = open("前期.json", "w")

    out_put_dict = {}

    for worksheet in worksheet_list:
        print(worksheet.title)

        one_day_dict = {}

        for col in range(3, worksheet.col_count+1):
            day = worksheet.cell(2, col).value
            k = worksheet.cell(3, col).value
            p = worksheet.cell(4, col).value
            t = worksheet.cell(5, col).value
            a = worksheet.cell(7, col).value

            cell_doc_list = []
            for cell_doc in [k, p, t, a]:
                cell_doc_list += re.split('[。.．]', cell_doc)

            cell_doc_list = [x.replace('\n', '') for x in cell_doc_list]
            cell_doc_list = [x for x in cell_doc_list if x is not '']

            one_day_dict[day] = cell_doc_list

        out_put_dict[worksheet.title] = one_day_dict

    json.dump(out_put_dict, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.close()
    print(out_put_dict)


def get_end_of_sentence(doc_list):
    pass


if __name__ == '__main__':
    # create_data()

    # データ読み込み
    f = open("前期.json")
    data = json.load(f)
