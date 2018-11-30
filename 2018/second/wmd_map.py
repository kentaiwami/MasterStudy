import MeCab
from gensim.models import KeyedVectors
import json
import csv
import multiprocessing as mp
import time
import os
import correspondence_student_number
import sys
from distutils.util import strtobool


def wrap_subcalc(args):
    return subcalc(*args)


def subcalc(p, all_documents):
    sub_mapping = {}
    s = int(len(all_documents) * p / proc)
    e = int(len(all_documents) * (p + 1) / proc)
    sliced = all_documents[s:e]
    total = len(sliced)


    for i, document in enumerate(sliced, start=1):
        print('{}: {}%'.format(process[p], int(i/total*100)))

        distances = []

        if is_include_self:
            other_documents = [x for x in all_documents if x['id'] != document['id']]
        else:
            other_documents = [x for x in all_documents if x['student'] != document['student']]

        for other_document in other_documents:
            distance_result = calc_distance(document['origin'], other_document['origin'])

            distances.append({
                'dis': distance_result,
                'id': other_document['id']
            })


        """
        マッピング
        """

        # 距離が0（同じ文章）を先にピックアップ
        all_zero_distances = [x for x in distances if x['dis'] == 0.0]

        for zero_distance in all_zero_distances:
            distances.remove(zero_distance)

        ave_zero_distances = [x for x in distances if x['dis'] == 0.0]

        for zero_distance in ave_zero_distances:
            distances.remove(zero_distance)

        # 上位3件をピックアップ
        higher_distances = sorted(distances, key=lambda x: x['dis'])[:3]

        # 平均値の最小値と全ての最小値から重複除去して記録
        sub_mapping[document['id']] = list(set(
            [x['id'] for x in higher_distances] +
            [x['id'] for x in all_zero_distances] +
            [x['id'] for x in ave_zero_distances]
        ))

    return sub_mapping


def main():
    global document_id
    file = open(os.path.normpath(os.path.join(base_path, '../後期.json')))
    data = json.load(file)
    all_documents = []

    """
    全学生のドキュメントをjsonファイルから読み込んで変数に格納
    """
    for student_number in data.keys():
        print(student_number)
        for day in data[student_number].keys():

            all_documents += add_document(data[student_number][day]['K'], student_number, day, 'K')
            all_documents += add_document(data[student_number][day]['P'], student_number, day, 'P')
            all_documents += add_document(data[student_number][day]['T'], student_number, day, 'T')

    file.close()

    """
    距離を計算してマッピングをする
    """
    pool = mp.Pool(proc)
    args = [(i, all_documents) for i in range(proc)]
    callbacks = pool.map(wrap_subcalc, args)
    pool.close()

    # 結果をマージ
    mapping = {}
    for callback in callbacks:
        mapping = {**mapping, **callback}


    """
    マッピングされていないもの（その人しか記述していない内容）と
    たくさんマッピングされているもの（みんなが書いている内容）を抽出する
    """
    mapping_ids = []
    for key in mapping:
        mapping_ids += mapping[key]

    mapping_ids = list(set(mapping_ids))

    # マッピングされていないidを抽出
    not_mapping_ids = [x for x in range(document_id) if x not in mapping_ids]

    # 学生順、より多くマッピングされている、文字数が少ない順
    hogehoge = many_mapping_sort(mapping, all_documents)


    """
    結果出力
    """
    output_csv(sorted(not_mapping_ids), hogehoge, all_documents)


def many_mapping_sort(mapping, all_documents):
    tmp = [{'id': int(x), 'map': mapping[x]} for x in mapping]

    tmp = sorted(tmp, key=lambda x: len(x['map']), reverse=True)
    tmp = sorted(tmp, key=lambda x: len(all_documents[x['id']]['origin']))
    tmp = sorted(tmp, key=lambda x: correspondence_student_number.get_name(all_documents[x['id']]['student']))

    return tmp


def output_csv(not_mapping_ids, sorted_many_mapping, all_documents):
    if is_include_self:
        name = '_include_self'
    else:
        name = ''

    rare_file = open(os.path.normpath(os.path.join(base_path, 'output/wmd_map/rare{}.csv'.format(name))), 'w')
    many_file = open(os.path.normpath(os.path.join(base_path, 'output/wmd_map/many{}.csv'.format(name))), 'w')

    writer = csv.writer(rare_file, lineterminator='\n')
    writer.writerow(['student', 'date', 'origin', 'id', 'KPT'])

    for not_mapping_id in not_mapping_ids:
        doc = all_documents[not_mapping_id]
        student_name = correspondence_student_number.get_name(doc['student'])
        writer.writerow([student_name, doc['day'], doc['origin'], doc['id'], doc['KPT']])


    writer = csv.writer(many_file, lineterminator='\n')
    writer.writerow(['student', 'date', 'origin', 'count', 'KPT', 'id', 'mappings'])

    for mapping_dict in sorted_many_mapping:
        doc = all_documents[mapping_dict['id']]
        student_name = correspondence_student_number.get_name(doc['student'])
        mappings = [str(x) for x in mapping_dict['map']]
        mappings = ' '.join(mappings)

        writer.writerow([student_name, doc['day'], doc['origin'], len(mapping_dict['map']), doc['KPT'], doc['id'], mappings])

    many_file.close()
    rare_file.close()


def calc_distance(target_sentence, sentence):
    sentence_wakachi = mecab.parse(sentence).replace(' \n', '').split()
    target_sentence_wakachi = mecab.parse(target_sentence).replace(' \n', '').split()

    return word2vec_model.wmdistance(sentence_wakachi, target_sentence_wakachi)


def add_document(kpt_list, student_number, day, kpt):
    global document_id
    tmp_documents = []

    if kpt == 'K':
        output_kpt = 'Keep'
    elif kpt == 'P':
        output_kpt = 'Problem'
    else:
        output_kpt = 'Try'

    for text in kpt_list:
        tmp_documents.append({
            'id': document_id,
            'origin': text,
            'student': student_number,
            'day': day,
            'KPT': output_kpt
        })
        document_id += 1

    return tmp_documents


def check_argv():
    if len(sys.argv) == 1:
        raise ValueError

    try:
        tmp_is_include_self = strtobool(sys.argv[1])
    except ValueError:
        raise ValueError

    return tmp_is_include_self


if __name__ == '__main__':
    is_include_self = check_argv()
    proc = 16
    process = [chr(i) for i in range(65, 65 + 26)]
    document_id = 0
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    base_path = os.path.dirname(os.path.abspath(__file__))
    word2vec_model = KeyedVectors.load_word2vec_format(os.path.normpath(os.path.join(base_path, '../../model/tohoku/model.bin')), binary=True)

    start = time.time()

    main()

    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")