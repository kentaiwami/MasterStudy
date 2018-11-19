import MeCab
from gensim.models import KeyedVectors
import json


def main():
    global document_id
    file = open("../2018/後期.json")
    data = json.load(file)
    all_documents = []
    mapping = {}

    for student_number in data.keys():
        print(student_number)
        for day in data[student_number].keys():

            all_documents += add_document(data[student_number][day]['K'], student_number, day, 'K')
            all_documents += add_document(data[student_number][day]['P'], student_number, day, 'P')
            all_documents += add_document(data[student_number][day]['T'], student_number, day, 'T')

    for document in all_documents:
        distances = []
        other_documents = [x for x in all_documents if x['id'] != document['id']]

        for other_document in other_documents:
            print(other_document, document)

            # documentとother_documentで距離計算
            # distancesに計算した距離とidを辞書にして入れていく
            break
        break

        # distancesをソートして上位3件までスライス
        # documentのidをmappingから探す。
            # keyがなければ、新たにdistancesにあるidを入れていく
            # keyがあれば、valueにdistancesにあるidを追加して上書きしていく


    # この時点でmappingが完了
    # range(0, document_id)でforを回していき、mapping内にkeyがないものを抽出
    # この時点で「その人しか記述していないような内容」を抽出できる。

    # mappingの中身をvalueに格納されたidの個数で降順にソート
    # この時点で、「みんなが書いているような内容」を抽出できる。


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

    return min(all_distances), min(ave_distances)


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
    document_id = 0
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    word2vec_model = KeyedVectors.load_word2vec_format('../model/tohoku/model.bin', binary=True)
    # main()
