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
            # documentとother_documentで距離計算
            # distancesに計算した距離とidを辞書にして入れていく
            pass

        # distancesをソートして上位3件までスライス
        # documentのidをmappingから探す。
            # keyがなければ、新たにdistancesにあるidを入れていく
            # keyがあれば、valueにdistancesにあるidを追加して上書きしていく


    # この時点でmappingが完了
    # range(0, document_id)でforを回していき、mapping内にkeyがないものを抽出
    # この時点で「その人しか記述していないような内容」を抽出できる。

    # mappingの中身をvalueに格納されたidの個数で降順にソート
    # この時点で、「みんなが書いているような内容」を抽出できる。

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
    # mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    # word2vec_model = KeyedVectors.load_word2vec_format('../model/tohoku/model.bin', binary=True)
    main()
