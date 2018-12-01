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
    rare_mapping = {}
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

        sub_mapping[document['id']] = distances

        """
        マッピング
        """
        tmp_distances = distances.copy()

        # 距離が0（同じ文章）を先にピックアップ
        all_zero_distances = [x for x in tmp_distances if x['dis'] == 0.0]

        for zero_distance in all_zero_distances:
            tmp_distances.remove(zero_distance)

        ave_zero_distances = [x for x in tmp_distances if x['dis'] == 0.0]

        for zero_distance in ave_zero_distances:
            tmp_distances.remove(zero_distance)

        # 上位3件をピックアップ
        higher_distances = sorted(tmp_distances, key=lambda x: x['dis'])[:3]

        # 平均値の最小値と全ての最小値から重複除去して記録
        rare_mapping[document['id']] = list(set(
            [x['id'] for x in higher_distances] +
            [x['id'] for x in all_zero_distances] +
            [x['id'] for x in ave_zero_distances]
        ))

    return sub_mapping, rare_mapping


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
    distance_results = {}
    rare_mapping_results = {}
    for callback in callbacks:
        distance_results = {**distance_results, **callback[0]}
        rare_mapping_results = {**rare_mapping_results, **callback[1]}

    # {'10': [{'dis': 12.112, 'id': 1}]...}
    # 全距離から平均値を算出
    tmp_dis_sum = 0.0

    for doc_id in distance_results:
        distance_obj_list = distance_results[doc_id]
        tmp_distance_list = [x['dis'] for x in distance_obj_list]
        tmp_dis_sum += sum(tmp_distance_list)

    dis_ave = tmp_dis_sum / (pow(len(all_documents), 2))

    print('====================')
    print('dis_ave: {}'.format(dis_ave))
    print('====================')


    """
    マッピング作業
    """
    mapping = {}
    for doc_id in distance_results:
        tmp_mapping = []
        for distance_obj in distance_results[doc_id]:
            if distance_obj['dis'] <= dis_ave:
                tmp_mapping.append(distance_obj['id'])

        mapping[doc_id] = tmp_mapping



    """
    マッピングされていないもの（その人しか記述していない内容）と
    たくさんマッピングされているもの（みんなが書いている内容）を抽出する
    """
    mapping_ids = []
    for key in rare_mapping_results:
        mapping_ids += rare_mapping_results[key]

    mapping_ids = list(set(mapping_ids))

    # マッピングされていないidを抽出
    not_mapping_ids = [x for x in range(document_id) if x not in mapping_ids]

    # 学生順、より多くマッピングされている、文字数が少ない順
    sorted_many_mapping = many_mapping_sort(mapping, all_documents)


    """
    結果出力
    """
    output_csv(sorted(not_mapping_ids), sorted_many_mapping, all_documents)


def many_mapping_sort(mapping, all_documents):
    sum_mapping_count = 0

    for doc_id in mapping:
        sum_mapping_count += len(mapping[doc_id])

    ave_mapping_count = sum_mapping_count / len(all_documents)

    tmp = [{'id': int(x), 'map': mapping[x]} for x in mapping if len(mapping[x]) >= ave_mapping_count]

    tmp = sorted(tmp, key=lambda x: len(x['map']), reverse=True)
    tmp = sorted(tmp, key=lambda x: correspondence_student_number.get_name(all_documents[x['id']]['student']))

    return tmp


def output_csv(not_mapping_ids, sorted_many_mapping, all_documents):
    if is_include_self:
        incluse_self_name = '_include_self'
    else:
        incluse_self_name = ''

    if is_limit_hinshi:
        hinshi_name = '_hinshi'
    else:
        hinshi_name = ''


    rare_file = open(os.path.normpath(os.path.join(base_path, 'output/wmd_map/rare{}{}.csv'.format(incluse_self_name, hinshi_name))), 'w')
    many_file = open(os.path.normpath(os.path.join(base_path, 'output/wmd_map/many{}{}.csv'.format(incluse_self_name, hinshi_name))), 'w')

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
    if is_limit_hinshi:
        sentence_wakachi = get_hinshi_wakachi(sentence)
        target_sentence_wakachi = get_hinshi_wakachi(target_sentence)

        if len(sentence_wakachi) == 0:
            sentence_wakachi = mecab.parse(sentence).replace(' \n', '').split()

        if len(target_sentence_wakachi) == 0:
            target_sentence_wakachi = mecab.parse(target_sentence).replace(' \n', '').split()

    else:
        sentence_wakachi = mecab.parse(sentence).replace(' \n', '').split()
        target_sentence_wakachi = mecab.parse(target_sentence).replace(' \n', '').split()

    return word2vec_model.wmdistance(sentence_wakachi, target_sentence_wakachi)



def get_hinshi_wakachi(text):
    ok_hinshi = ['名詞', '形容詞', '動詞']
    mecab.parseToNode('')
    node = mecab.parseToNode(text)

    keywords = []
    while node:
        if node.feature.split(',')[0] in ok_hinshi and node.feature.split(',')[6] != '*':
            keywords.append(node.feature.split(',')[6])

        node = node.next

    return keywords


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
        tmp_is_limit_hinshi = strtobool(sys.argv[2])
    except (ValueError, IndexError):
        raise ValueError

    return tmp_is_include_self, tmp_is_limit_hinshi


if __name__ == '__main__':
    is_include_self, is_limit_hinshi = check_argv()
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
