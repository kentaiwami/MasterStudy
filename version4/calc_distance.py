import json
import datetime
from gensim.models import KeyedVectors
import MeCab


def main():
    for student_number in data.keys():
        for day in data[student_number].keys():
            date = datetime.datetime.strptime('2017年'+day, "%Y年%m月%d日")
            p_list = data[student_number][day]['P']
            t_list = data[student_number][day]['T']
            k_list = get_keep(student_number, date)

            keep_to_distance(student_number, p_list, k_list, day)
            keep_to_distance(student_number, t_list, k_list, day)

        print('*************************:')
        break


def keep_to_distance(student_number, sentence_list, k_list, day):
    for i, sentence in enumerate(sentence_list, 1):
        for KeepObj in k_list:
            for k_index, Keep in enumerate(KeepObj['keep'], 1):
                print(student_number)
                print('Keep day:', KeepObj['day'])
                print('Keep:', Keep)
                print('Sentence day:', day)
                print('Sentence:', sentence)
                print('Distance', get_distance(sentence, Keep))


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
    for ten_words_sentence in get_ten_words(sentence_list):

        one_sent_dis = []
        for ten_words_keep in get_ten_words(keep_list):

            dis = word2vec_model.wmdistance(ten_words_sentence, ten_words_keep)

            results.append({
                'ten_words_sentence': ten_words_sentence,
                'ten_words_keep': ten_words_keep,
                'distance': dis
            })
            one_sent_dis.append(dis)

        results[-1]['average'] = sum(one_sent_dis) / len(one_sent_dis)

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


if __name__ == '__main__':
    file = open("2017/前期.json")
    data = json.load(file)

    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    word2vec_model = KeyedVectors.load_word2vec_format('model/tohoku/model.bin', binary=True)
    # main()
    sent1 = '分担ごとに作業に取り掛かることで、効率よく作業を進めることが出来たと思う。ポスターはレイアウトの作成が完了し、ヒアリングで得られた意見や要望をまとめることも出来た。'
    sent2 = '町会の方から頂いたご意見や要望の洗い出しと、機能がなぜ必要なのかをスプレッドシートにまとめる。優先度はグループ内で話し合って決めたい。'
    hoge = get_distance(sent1, sent2)