import MeCab
from gensim.models import KeyedVectors
import json
import csv
import multiprocessing as mp
import time


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
        other_documents = [x for x in all_documents if x['id'] != document['id']]

        for other_document in other_documents:
            distance_result = calc_distance(document['origin'], other_document['origin'])
            distances.append({
                'all': distance_result['all'],
                'ave': distance_result['ave'],
                'id': other_document['id']
            })


        """
        マッピング
        """

        # 距離が0（同じ文章）を先にピックアップ
        all_zero_distances = [x for x in distances if x['all'] == 0.0]

        for zero_distance in all_zero_distances:
            distances.remove(zero_distance)

        ave_zero_distances = [x for x in distances if x['ave'] == 0.0]

        for zero_distance in ave_zero_distances:
            distances.remove(zero_distance)

        # 上位3件をピックアップ
        higher_all_distances = sorted(distances, key=lambda x: x['all'])[:3]
        higher_ave_distances = sorted(distances, key=lambda x: x['ave'])[:3]

        # 平均値の最小値と全ての最小値から重複除去して記録
        sub_mapping[document['id']] = list(set(
            [x['id'] for x in higher_all_distances] +
            [x['id'] for x in higher_ave_distances] +
            [x['id'] for x in all_zero_distances] +
            [x['id'] for x in ave_zero_distances]
        ))

    return sub_mapping


def main():
    global document_id
    file = open("../2018/後期.json")
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

    # より多くマッピングされている順にソート
    sorted_many_mapping = sorted(mapping.items(), key=lambda x: len(x[1]), reverse=True)


    """
    結果出力
    """
    output_csv(not_mapping_ids, sorted_many_mapping, all_documents)

    # デバッグ用にマッピングの結果を出力
    debug_file = open('../2018/wmd_map_output/debug.txt', 'w')
    for key in mapping:
        debug_file.write('{}: {}\n'.format(key, mapping[key]))
    debug_file.close()


def output_csv(not_mapping_ids, sorted_many_mapping, all_documents):
    rare_file = open('../2018/wmd_map_output/rare.csv', 'w')
    many_file = open('../2018/wmd_map_output/many.csv', 'w')

    writer = csv.writer(rare_file, lineterminator='\n')
    writer.writerow(['student', 'date', 'origin', 'id', 'KPT'])

    for not_mapping_id in not_mapping_ids:
        doc = all_documents[not_mapping_id]
        writer.writerow([doc['student'], doc['day'], doc['origin'], doc['id'], doc['KPT']])


    writer = csv.writer(many_file, lineterminator='\n')
    writer.writerow(['student', 'date', 'origin', 'id', 'count', 'KPT'])

    for many_mapping in sorted_many_mapping:
        doc = all_documents[many_mapping[0]]
        writer.writerow([doc['student'], doc['day'], doc['origin'], doc['id'], len(many_mapping[1]), doc['KPT']])

    many_file.close()
    rare_file.close()


def calc_distance(target_sentence, sentence):
    # 分かち書きをしてストップワードを除去
    stopwords = get_stopwords()
    sentence_wakachi = mecab.parse(sentence).replace(' \n', '').split()
    sentence_wakachi = [x for x in sentence_wakachi if x not in stopwords]
    target_sentence_wakachi = mecab.parse(target_sentence).replace(' \n', '').split()
    target_sentence_wakachi = [x for x in target_sentence_wakachi if x not in stopwords]

    all_distances = [] # 全ての距離
    ave_distances = [] # target_sentenceとsentenceの10単語くぎりごとの平均距離

    for target_sentence_ten_word in get_ten_words(target_sentence_wakachi):
        tmp_distances = []

        for sentence_ten_word in get_ten_words(sentence_wakachi):
            dis = word2vec_model.wmdistance(target_sentence_ten_word, sentence_ten_word)
            tmp_distances.append(dis)
            all_distances.append(dis)

        ave_distances.append(sum(tmp_distances) / len(tmp_distances))

    return {'all': min(all_distances), 'ave': min(ave_distances)}


def get_stopwords():
    stopword_f = open('../2018/stopwords.txt', 'r')
    stopwords = stopword_f.readlines()
    stopword_f.close()
    stopwords = [x.replace('\n', '') for x in stopwords]

    return stopwords


def get_ten_words(sentence):
    results = []
    s = 0
    e = 10
    while True:
        if len(sentence[s:e]) == 0:
            break

        results.append(sentence[s:e])

        s = e
        e += 10

    return results


def add_document(kpt_list, student_number, day, kpt):
    global document_id
    tmp_documents = []

    for text in kpt_list:
        tmp_documents.append({
            'id': document_id,
            'origin': text,
            'student': student_number,
            'day': day,
            'KPT': kpt
        })
        document_id += 1

    return tmp_documents


if __name__ == '__main__':
    proc = 16
    process = [chr(i) for i in range(65, 65 + 26)]
    document_id = 0
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    word2vec_model = KeyedVectors.load_word2vec_format('../model/tohoku/model.bin', binary=True)

    start = time.time()

    main()

    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
