import MeCab
from gensim.models import KeyedVectors
import json
import os
import csv


def add_document(sentences, student_number, day, kpt):
    global document_id
    tmp_documents = []

    for i, sentence in enumerate(sentences):
        tmp_documents.append({
            'kpt': kpt,
            'day': day,
            'student': student_number,
            'index': i+1,
            'id': document_id,
            'text': sentence
        })

        document_id += 1

    return tmp_documents


def calc_distance(sentence1, sentence2):
    sentence1_wakachi = mecab.parse(sentence1).replace(' \n', '').split()
    sentence2_wakachi = mecab.parse(sentence2).replace(' \n', '').split()

    return word2vec_model.wmdistance(sentence1_wakachi, sentence2_wakachi)


def main():
    file = open(os.path.normpath(os.path.join(base_path, '前期.json')))
    data = json.load(file)

    for student_number in data.keys():
        p_documents = []
        t_documents = []

        print(student_number)

        for day in data[student_number].keys():
            p_documents += add_document(data[student_number][day]['P'], student_number, day, 'P')
            t_documents += add_document(data[student_number][day]['T'], student_number, day, 'T')

        output(student_number, calc(p_documents), p_documents, 'P')
        output(student_number, calc(t_documents), t_documents, 'T')

    file.close()


def calc(sentences):
    calced_kumiawase = []
    calced_results = []
    sum_distance = 0.0

    for doc1 in sentences:
        for doc2 in sentences:
            if doc1['id'] == doc2['id']:
                continue

            if doc1['id'] > doc2['id']:
                tmp_kumiawase = (doc2['id'], doc1['id'])
            else:
                tmp_kumiawase = (doc1['id'], doc2['id'])

            if tmp_kumiawase in calced_kumiawase:
                continue
            else:
                distance = calc_distance(doc1['text'], doc2['text'])
                calced_results.append({
                    'text1_id': doc1['id'],
                    'text2_id': doc2['id'],
                    'distance': distance
                })
                sum_distance += distance
                calced_kumiawase.append(tmp_kumiawase)

    ave_distance = sum_distance / len(calced_kumiawase)

    calced_results = [x for x in calced_results if x['distance'] <= ave_distance]

    skip_doc_id = []
    merge_results = []

    for calced_result in calced_results:
        doc_id = calced_result['text1_id']

        if doc_id in skip_doc_id:
            continue

        skip_doc_id.append(doc_id)

        hoge = [x for x in calced_results if x['text1_id'] == doc_id]
        hoge = sorted(hoge, key=lambda x: x['distance'])[:3]
        
        merge_results.append({
            'text1': doc_id,
            'mapping': [x['text2_id'] for x in hoge]
        })

    return merge_results


def output(student_number, results, documents, kpt):
    file = open(os.path.normpath(os.path.join(base_path, 'output/{}/{}_jyuhuku.csv'.format(student_number, kpt))),'w')
    writer = csv.writer(file, lineterminator='\n')
    writer.writerow(['doc1_day', 'doc1_index', 'map_day', 'map_index'])

    for result in results:
        document = [x for x in documents if x['id'] == result['text1']][0]
        mapping_ids = [x for x in result['mapping']]

        for mapping_id in mapping_ids:
            mapping_doc = [x for x in documents if x['id'] == mapping_id][0]
            writer.writerow([document['day'], document['index'], mapping_doc['day'], mapping_doc['index']])

    file.close()

if __name__ == '__main__':
    document_id = 0
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    base_path = os.path.dirname(os.path.abspath(__file__))
    word2vec_model = KeyedVectors.load_word2vec_format(
    os.path.normpath(os.path.join(base_path, '../model/tohoku/model.bin')), binary=True)

    main()
