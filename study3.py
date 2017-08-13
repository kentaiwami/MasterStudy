import study
import MeCab
import CaboCha
from xml.etree import ElementTree
import re
import json
import csv
import math


test_sentence = '以前、Trelloで行おうと決めてからずっと放置してしまっていたタスク管理について、ようやく着手することができた'
# test_sentence = '上田さん土手さん創生会議の関係性を知ることができた'
# test_sentence = '少しだらだらと長引きすぎた'


def create_data():
    worksheet_list = study.get_worksheet_list('15RsrnLlocEQhGd-m27nXL8CuJcTwIs3rG8mO1VGx6Gs')

    f = open("前期2.json", "w")

    out_put_dict = {}

    for worksheet in worksheet_list:
        print(worksheet.title)

        one_day_dict = {}

        for col in range(3, worksheet.col_count+1):
            day = worksheet.cell(2, col).value
            k = worksheet.cell(3, col).value
            p = worksheet.cell(4, col).value
            t = worksheet.cell(5, col).value
            o = worksheet.cell(7, col).value

            format_dict = {}

            for cell_doc, format_id in zip([k, p, t, o], ['K', 'P', 'T', 'O']):
                cell_doc_list = re.split('[。.．\n]', cell_doc)

                cell_doc_list = [x.replace('\n', '') for x in cell_doc_list]
                cell_doc_list = [x for x in cell_doc_list if x is not '']

                format_dict[format_id] = cell_doc_list

            one_day_dict[day] = format_dict

        out_put_dict[worksheet.title] = one_day_dict

    json.dump(out_put_dict, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.close()


def search_all_sentence(dict_data):
    end_of_sentence_all_dict = {}
    c = CaboCha.Parser("-u original.dic")
    sentence_dict = {}

    # 学生のループ
    for student_number in dict_data.keys():

        student_dict = {}

        # 日付のループ
        for day in dict_data[student_number].keys():

            # KPTOのループ
            kpto = {}
            for format_id in dict_data[student_number][day].keys():

                sentence_list = []

                for sentence in dict_data[student_number][day][format_id]:
                    # TEST
                    # sentence = test_sentence

                    c_tree = c.parse(sentence)
                    c_xml = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))
                    end_chunk = c_xml.find(".//chunk[@link='-1']")

                    if len(c_xml.findall(".//chunk")) == 0:
                        continue

                    # print(c_tree.toString(CaboCha.FORMAT_XML))
                    # 文末からの係り受け抽出
                    # last_chunk_relation_sentence = search_end_chunk_relation(c_xml, end_chunk)
                    # print(last_chunk_relation_sentence)

                    # 名詞句の取り出し
                    noun_list = get_noun(c_xml)

                    # 文末の抽出
                    last_tok, one_day_last_tok_origin_list, end_of_sentence_all_dict = get_end_of_sentence(end_chunk, end_of_sentence_all_dict)

                    sentence_list.append({'sentence': sentence,
                                          'end_of_sentence': last_tok,
                                          'original_pattern': one_day_last_tok_origin_list,
                                          'noun': noun_list})
                    # print(sentence_list)
                    # exit(-1)
                kpto[format_id] = sentence_list

            student_dict[day] = kpto

        sentence_dict[student_number] = student_dict

    # f = open('output_data2.json', 'w')
    # json.dump(sentence_dict, f, ensure_ascii=False, indent=2, sort_keys=True)
    # f.close()
    # print(sorted(end_of_sentence_all_dict.items(), key=lambda x: x[1], reverse=True))
    return sentence_dict


def get_noun(c_xml):
    noun_list = []
    for chunk in c_xml.findall(".//chunk"):
        for tok in chunk.findall(".//tok"):
            tok_split = tok.attrib['feature'].split(',')
            if tok_split[0] == '名詞' and tok_split[1] != '非自立' and tok_split[1] != '接尾':
                noun_list.append(tok.text)

    return noun_list


def get_end_of_sentence(end_chunk, end_of_sentence_all_dict):
    tok_list = end_chunk.findall(".//tok")
    last_tok = ''
    one_day_last_tok_origin_list = []

    # 文末文の抽出
    for tok in tok_list:
        feature_list = tok.attrib['feature'].split(',')

        if len(feature_list[6]) != 1:
            one_day_last_tok_origin_list.append(feature_list[6])

        last_tok += tok.text

    # 文末の集計
    if last_tok in end_of_sentence_all_dict:
        count = end_of_sentence_all_dict[last_tok]
        count += 1
        end_of_sentence_all_dict[last_tok] = count
    else:
        end_of_sentence_all_dict[last_tok] = 1

    return last_tok, one_day_last_tok_origin_list, end_of_sentence_all_dict


def search_end_chunk_relation(c_xml, end_chunk):
    end_chunk_id = end_chunk.attrib['id']
    chunk_relation_list = c_xml.findall(".//chunk[@link='%s']" % end_chunk_id)

    hoge = ''
    for chunk in chunk_relation_list:
        hoge += ' '
        for tok in chunk.findall(".//tok"):
            hoge += tok.text

    hoge += '*'
    for tok in end_chunk.findall(".//tok"):
        hoge += tok.text
    hoge += '*'

    return hoge


def td_idf(dict_data):
    sentence_list = []

    for student_number in dict_data.keys():
        for day in dict_data[student_number].keys():
            for sentence in dict_data[student_number][day]:
                sentence_list.append(sentence)

    num = len(sentence_list)

    result = []

    for i in range(num):  # 文章の分解
        tagger = MeCab.Tagger("-u original.dic")
        result.append(tagger.parse(sentence_list[i]))

    wordCount = {}
    allCount = {}
    sub_tfstore = {}
    tfcounter = {}
    tfstore = {}
    sub_idf = {}
    idfstore = {}
    merge_idf = {}
    tfidf = {}
    merge_tfidf = {}
    wordList = []
    sum = 0

    for i in range(num):
        wordList.append(result[i].split()[:-1:2])  # wordListに分解された単語要素のみを格納
        # print(wordList)
        # exit(-1)

    for i in range(num):
        for word in wordList[i]:
            allCount[i] = wordCount.setdefault(word, 0)
            wordCount[word] += 1
        allCount[i] = wordCount  # 単語出現回数を文章ごとに格納。tfの分母に相当
        wordCount = {}

    for i in range(num):  # tfの分母を計算
        for word in allCount[i]:
            sum = sum + allCount[i][word]
        sub_tfstore[i] = sum
        sum = 0

    for i in range(num):  # tf値を計算し文章ごとに辞書に格納
        for word in allCount[i]:
            tfcounter[word] = allCount[i][word] * 1.0 / sub_tfstore[i]
        tfstore[i] = tfcounter
        tfcounter = {}

    for i in range(num):
        for word in wordList[i]:
            wordCount.setdefault(word, 0)
        for word in allCount[i]:
            wordCount[word] += 1
        sub_idf = wordCount  # ある単語の文章あたりの出現回数を辞書に格納

    for i in range(num):
        for word in allCount[i]:
            idfstore[word] = math.log(1.0 * math.fabs(num) / math.fabs(sub_idf[word]))
        merge_idf[i] = idfstore
        idfstore = {}

    for i in range(num):  # tfidfの計算
        for word in allCount[i]:
            tfidf[word] = tfstore[i][word] * merge_idf[i][word]
        merge_tfidf[i] = tfidf
        tfidf = {}

    index = sentence_list.index(test_sentence)
    for i in range(num):  # 降順に出力する
        if i != index:
            continue
        for word, count in sorted(merge_tfidf[i].items(), key=lambda x: x[1], reverse=True):
            print('text%d: %-16s %2.3f' % (i + 1, word, count))


if __name__ == '__main__':
    # create_data()

    # データ読み込み
    f = open("前期2.json")
    data = json.load(f)

    # td_idf(data)
    end_of_sentence_dict = search_all_sentence(data)