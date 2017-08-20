from pip._vendor.distlib.compat import raw_input
import study
import MeCab
import CaboCha
from xml.etree import ElementTree
import re
import json
import math
from collections import Counter
import hdp


# test_sentence = '以前、Trelloで行おうと決めてからずっと放置してしまっていたタスク管理について、ようやく着手することができた'
# test_sentence = "文書をまとめたり、今後どのようなものを作るかの内容を決めていく上でチームメンバーと深く話し合うことで、ゲートキーパーの上田さんと土手さんや石別創成会議の関係性について気づかないところがたくさんあることに気づくことができた"
# test_sentence = '上田さん土手さん創生会議の関係性を知ることができた'
# test_sentence = '少しだらだらと長引きすぎた'
test_sentence = 'リピーターにするための手段を考えるなど、目標を達成するための細かいプロセスを考えることができた'


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

    # f = open('output_data.json', 'w')
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


def td_idf(sentence_list):
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
    word_sum = 0

    for i in range(num):
        wordList.append(result[i].split()[:-1:2])  # wordListに分解された単語要素のみを格納

    for i in range(num):
        for word in wordList[i]:
            allCount[i] = wordCount.setdefault(word, 0)
            wordCount[word] += 1
        allCount[i] = wordCount  # 単語出現回数を文章ごとに格納。tfの分母に相当
        wordCount = {}

    for i in range(num):  # tfの分母を計算
        for word in allCount[i]:
            word_sum = word_sum + allCount[i][word]
        sub_tfstore[i] = word_sum
        word_sum = 0

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

    return merge_tfidf

    # for i in range(num):  # 降順に出力する
    #     for word, count in sorted(merge_tfidf[i].items(), key=lambda x: x[1], reverse=True):
    #         print('text%d: %-16s %2.3f' % (i + 1, word, count))


def cut_sentence(tfidf, sentence_list, max_sentence_len):
    c = CaboCha.Parser("-u original.dic")

    # TEST
    # index = sentence_list.index(test_sentence)

    cuted_sentence_list = []

    hoge = 0
    cut_sum = 0

    for i in range(len(tfidf)):
        # TEST
        # sentence = test_sentence
        sentence = sentence_list[i]

        c_tree = c.parse(sentence)
        c_xml = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))
        chunk_list = c_xml.findall(".//chunk")
        chunk_tfidf = {}

        # chunkごとのtfidf値の合計を計算
        for word, count in sorted(tfidf[i].items(), key=lambda x: x[1], reverse=True):
            for chunk_id, chunk in enumerate(chunk_list):
                for tok in chunk.findall(".//tok"):
                    if word == tok.text:
                        if chunk_id in chunk_tfidf:
                            chunk_tfidf[chunk_id] += count
                        else:
                            chunk_tfidf[chunk_id] = count
                        break

        # 係り受けを用いてchunkごとのtfidf値を更新
        for chunk_id, chunk in enumerate(chunk_list):
            link = int(chunk.attrib['link'])

            if link == -1:
                break

            chunk_tfidf[link] += chunk_tfidf[chunk_id]

        # 最大文字数以内になるようにtfidf値が小さい順で文節を削除
        cut_index = 0
        sorted_list = sorted(chunk_tfidf.items(), key=lambda x: x[1])
        cuted_sentence_len = len(sentence)

        flag = False

        last_chunk_id = int(c_xml.find(".//chunk[@link='-1']").attrib['id']) - 3

        while cuted_sentence_len > max_sentence_len:
            flag = True
            cut_chunk_id = sorted_list[cut_index][0]
            c_xml.remove(chunk_list[cut_chunk_id])
            cut_index += 1

            if cut_chunk_id == last_chunk_id:
                hoge += 1


            text = ''
            for chunk in c_xml.findall(".//chunk"):
                for tok in chunk.findall(".//tok"):
                    text += tok.text

            cuted_sentence_len = len(text)

        if flag:
            cut_sum += 1
            text = ''
            for chunk in c_xml.findall(".//chunk"):

                for tok in chunk.findall(".//tok"):
                    text += tok.text
            cuted_sentence_list.append(text)
            print('****************************************')
            # print('origin:', sentence)
            print('cut:', text)
            # print('chunk tfidf: ', sorted_list)
            # c_tree = c.parse(sentence)
            # print(c_tree.toString(CaboCha.FORMAT_XML))
            # print(sorted_list)
            # for word, count in sorted(tfidf[index].items(), key=lambda x: x[1], reverse=True):
            #     print(word, count)
            print('****************************************')

            raw_input('>>>  ')

    # print(hoge)
    # print(cut_sum)
    # print('')
    # print(len(sentence_list))
    return cuted_sentence_list


def get_median_ave_mode(sentence_list):
    c = CaboCha.Parser("-u original.dic")
    sentence_len_list = []
    chunk_len_list = []

    for sentence in sentence_list:
        c_tree = c.parse(sentence)
        c_xml = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))
        chunk_len_list.append(len(c_xml.findall(".//chunk")))

        sentence_len_list.append(len(sentence))

    sentence_len_list.sort(reverse=True)

    # 中央値、平均値、最頻値の計算(文字数)
    if len(sentence_len_list) % 2 == 0:
        char_len_median = sentence_len_list[int(len(sentence_len_list)/2) - 1]
    else:
        char_len_median = (sentence_len_list[int(len(sentence_list) / 2) - 1] + sentence_len_list[int(len(sentence_list) / 2)]) / 2

    char_len_ave = sum(sentence_len_list) / len(sentence_len_list)
    char_len_mode = Counter(sentence_len_list).most_common(1)[0][0]

    # 文節の計算
    if len(chunk_len_list) % 2 == 0:
        chunk_len_median = chunk_len_list[int(len(chunk_len_list)/2) - 1]
    else:
        chunk_len_median = (chunk_len_list[int(len(chunk_len_list)/2) - 1] + chunk_len_list[int(len(chunk_len_list)/2)]) / 2

    chunk_len_ave = sum(chunk_len_list) / len(chunk_len_list)
    chunk_len_mode = Counter(chunk_len_list).most_common(1)[0][0]

    return char_len_median, char_len_ave, char_len_mode, chunk_len_median, chunk_len_ave, chunk_len_mode


def main_function():
    # create_data()

    # データ読み込み
    f = open("前期.json")
    data = json.load(f)


    for student_number in sorted(data.keys()):
        # print('student: ', student_number)
        sentence_list = []

        # 文書リストを作成
        for day in data[student_number].keys():
            for format_id in data[student_number][day].keys():
                for sentence in data[student_number][day][format_id]:
                    sentence_list.append(sentence)

        # 諸事情により、文章を1つも書いていない学生がいるため処理をスキップする
        if len(sentence_list) == 0:
            continue

    # 中央値、平均値、最頻値の計算
    #     s_median, s_ave, s_mode, c_median, c_ave, c_mode = get_median_ave_mode(sentence_list)
    # print('s_median: ', s_median)
    # print('s_ave: ', s_ave)
    # print('s_mode: ', s_mode)

    # print('c_median: ', c_median)
    # print('c_ave: ', c_ave)
    # print('c_mode: ', c_mode)

        # tf-idfの計算
        # merge_tfidf = td_idf(sentence_list)

        # 短縮処理の実行
        # cut_sentence(merge_tfidf, sentence_list, s_ave)


    # raw_input('>>>')

    # end_of_sentence_dict = search_all_sentence(data)


if __name__ == '__main__':
    main_function()
