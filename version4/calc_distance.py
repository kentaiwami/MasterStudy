import json
import datetime
from gensim.models import KeyedVectors
import MeCab


def main():
    for student_number in data.keys():
        # TODO テスト用
        student_number = '1015263'

        for day in data[student_number].keys():
            # TODO テスト用
            # day = '6月16日'

            date = datetime.datetime.strptime('2017年'+day, "%Y年%m月%d日")
            p_list = data[student_number][day]['P']
            t_list = data[student_number][day]['T']
            k_list = get_keep(student_number, date)

            for sent_list in [p_list, t_list]:
                results_average_min, results_distance_min = keep_to_distance(sent_list, k_list)
                results_average_min, results_distance_min = convert_dict_list(results_average_min, results_distance_min)
                flat_k_list = convert_keep_flat(k_list)

                output_results(
                    student_number,
                    flat_k_list,
                    k_list,
                    day,
                    results_average_min,
                    results_distance_min,
                    t_list,
                    3
                )

        break


def keep_to_distance(sentence_list, k_list):
    results_average_min = []
    results_distance_min = []

    for i, sentence in enumerate(sentence_list, 1):
        average_min_list = []
        distance_min_list = []

        for KeepObj in k_list:
            for k_index, Keep in enumerate(KeepObj['keep'], 1):
                distances = get_distance(sentence, Keep)

                # Keep10語ずつの平均値の最小を格納していく
                average_min_distance = min(x['average'] for x in distances)
                average_min_list.append(average_min_distance)

                # Keepと各文の全組み合わせの中から最小値を格納
                records = [x['record'] for x in distances]
                tmp_distance = []

                for record in records:
                    for obj in record:
                        tmp_distance.append(obj['distance'])

                distance_min_list.append(min(tmp_distance))

        results_average_min.append(average_min_list)
        results_distance_min.append(distance_min_list)

    return results_average_min, results_distance_min


def get_keep(student_number, pt_date):
    results = []

    for day in data[student_number].keys():
        k_date = datetime.datetime.strptime('2017年' + day, "%Y年%m月%d日")

        if k_date < pt_date:
            continue

        results.append({'day': day, 'keep': data[student_number][day]['K']})

    return results


def get_stopwords():
    stopword_f = open('2017/stopwords.txt', 'r')
    stopwords = stopword_f.readlines()
    stopword_f.close()
    stopwords = [x.replace('\n', '') for x in stopwords]

    return stopwords


def get_distance(sentence, keep):
    stopwords = get_stopwords()

    # ストップワードを除いた分かち書きリストを生成
    sentence_list = mecab.parse(sentence).replace(' \n', '').split()
    sentence_list = [x for x in sentence_list if x not in stopwords]
    keep_list = mecab.parse(keep).replace(' \n', '').split()
    keep_list = [x for x in keep_list if x not in stopwords]

    results = []
    for ten_words_keep in get_ten_words(keep_list):
        record = []
        tmp_distance = []
        for ten_words_sentence in get_ten_words(sentence_list):

            dis = word2vec_model.wmdistance(ten_words_sentence, ten_words_keep)

            record.append({
                'ten_words_sentence': ten_words_sentence,
                'ten_words_keep': ten_words_keep,
                'distance': dis
            })
            tmp_distance.append(dis)

        results.append({'record': record, 'average': sum(tmp_distance) / len(tmp_distance)})

    return results


def get_ten_words(sentence_list):
    results = []
    s = 0
    e = 10
    while True:
        if len(sentence_list[s:e]) == 0:
            break

        results.append(' '.join(sentence_list[s:e]))

        s = e
        e += 10

    return results


def get_keep_day(keep_list, target_sentence):
    for keep_obj in keep_list:
        for i, keep in enumerate(keep_obj['keep']):
            if keep == target_sentence:
                return i, keep_obj['day']


def convert_dict_list(results_average_min_list, results_distance_min_list):
    # チェック
    if len(results_average_min_list) != len(results_distance_min_list):
        raise Exception('Error')
    for tmp1, tmp2 in zip(results_average_min_list, results_distance_min_list):
        if len(tmp1) != len(tmp2):
            raise Exception('Error')

    new_results_average_min_list = []
    new_results_distance_min_list = []

    for results in zip(results_average_min_list, results_distance_min_list):
        results_average_min = {}
        results_distance_min = {}

        for i, results_distance in enumerate(zip(results[0], results[1])):
            results_average_min[i] = results_distance[0]
            results_distance_min[i] = results_distance[1]

        new_results_average_min_list.append(results_average_min)
        new_results_distance_min_list.append(results_distance_min)

    return new_results_average_min_list, new_results_distance_min_list


def convert_keep_flat(k_list):
    results = []

    for keep_obj in k_list:
        results += keep_obj['keep']

    return results


def output_results(student, flat_k_list, k_list, day, average_min_list, distance_min_list, sentence_list, rank):
    print(student)
    for i, average_min_sentence in enumerate(zip(average_min_list, sentence_list)):
        sliced = sorted(average_min_sentence[0].items(), key=lambda x: x[1])[0:rank]

        for distance_index in sliced:
            keep = flat_k_list[distance_index[0]]
            k_position, k_day = get_keep_day(k_list, keep)
            print('Keep Day:{} Keep Position:{}'.format(k_day, k_position))
            print('Keep:{}'.format(keep))
            print('Sentence Day:{} Sentence Position:{}'.format(day, i))
            print('Sentence:{}'.format(average_min_sentence[1]))
            print('Distance:{}'.format(distance_index[1]))
            print('')

        print('***********************')

    print('-------------------------------------')

    for i, distance_min_sentence in enumerate(zip(distance_min_list, sentence_list)):
        sliced = sorted(distance_min_sentence[0].items(), key=lambda x: x[1])[0:rank]

        for distance_index in sliced:
            keep = flat_k_list[distance_index[0]]
            k_position, k_day = get_keep_day(k_list, keep)
            print('Keep Day:{} Keep Position:{}'.format(k_day, k_position))
            print('Keep:{}'.format(keep))
            print('Sentence Day:{} Sentence Position:{}'.format(day, i))
            print('Sentence:{}'.format(distance_min_sentence[1]))
            print('Distance:{}'.format(distance_index[1]))
            print('')

        print('***********************')


if __name__ == '__main__':
    file = open("2017/前期.json")
    data = json.load(file)

    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    word2vec_model = KeyedVectors.load_word2vec_format('model/tohoku/model.bin', binary=True)
    main()
    # sent1 = '分担ごとに作業に取り掛かることで、効率よく作業を進めることが出来たと思う。ポスターはレイアウトの作成が完了し、ヒアリングで得られた意見や要望をまとめることも出来た。'
    # sent2 = '町会の方から頂いたご意見や要望の洗い出しと、機能がなぜ必要なのかをスプレッドシートにまとめる。優先度はグループ内で話し合って決めたい。'
    # hoge = get_distance(sent1, sent2)