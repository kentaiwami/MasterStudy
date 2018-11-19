import MeCab
from gensim.models import KeyedVectors
import json


def main():
    global document_id
    file = open("../2018/後期.json")
    data = json.load(file)
    all_documents = []

    for student_number in data.keys():
        print(student_number)
        for day in data[student_number].keys():

            all_documents += add_document(data[student_number][day]['K'], student_number, day, 'K')
            all_documents += add_document(data[student_number][day]['P'], student_number, day, 'P')
            all_documents += add_document(data[student_number][day]['T'], student_number, day, 'T')



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
