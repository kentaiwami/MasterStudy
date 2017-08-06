import study
import MeCab
import CaboCha
from xml.etree import ElementTree
import re
import json
import csv

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


def get_end_of_sentence(dict_data):
    c = CaboCha.Parser()
    end_of_sentence_dict = {}
    end_of_sentence_origin_dict = {}

    for student_number in dict_data.keys():

        student_last_tok_dict = {}
        student_last_tok_origin_dict = {}

        for day in dict_data[student_number].keys():

            one_day_last_tok_list = []
            one_day_last_tok_origin_list = []

            for sentence in dict_data[student_number][day]:
                c_tree = c.parse(sentence)
                c_xml = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))
                end_chunk = c_xml.findall(".//chunk[@link='-1']")

                if len(c_xml.findall(".//chunk")) == 0:
                    continue

                tok_list = end_chunk[0].findall(".//tok")
                last_tok = ''
                for tok in tok_list:
                    feature_list = tok.attrib['feature'].split(',')

                    if len(feature_list[6]) != 1:
                        one_day_last_tok_origin_list.append(feature_list[6])

                    last_tok += tok.text

                one_day_last_tok_list.append(last_tok)

            student_last_tok_dict[day] = one_day_last_tok_list
            student_last_tok_origin_dict[day] = one_day_last_tok_origin_list

        end_of_sentence_dict[student_number] = student_last_tok_dict
        end_of_sentence_origin_dict[student_number] =student_last_tok_origin_dict

    return end_of_sentence_dict


if __name__ == '__main__':
    # create_data()

    # データ読み込み
    f = open("前期.json")
    data = json.load(f)

    end_of_sentence_dict = get_end_of_sentence(data)
