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


def get_distance(doc1, doc2):
    stopwords = get_stopwords()

    wakati_doc1 = mecab.parse(doc1).replace(' \n', '').split()
    wakati_doc1 = [x for x in wakati_doc1 if x not in stopwords]
    wakati_doc1 = ' '.join(wakati_doc1)

    wakati_doc2 = mecab.parse(doc2).replace(' \n', '').split()
    wakati_doc2 = [x for x in wakati_doc2 if x not in stopwords]
    wakati_doc2 = ' '.join(wakati_doc2)

    # WMD
    dis = word2vec_model.wmdistance(wakati_doc1, wakati_doc2)

    return dis


if __name__ == '__main__':
    file = open("2017/前期.json")
    data = json.load(file)

    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    word2vec_model = KeyedVectors.load_word2vec_format('model/tohoku/model.bin', binary=True)
    main()
