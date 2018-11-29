from gensim.summarization.bm25 import get_bm25_weights
import os
import MeCab
import json
import datetime
import csv
import correspondence_student_number


def get_documents():
    documents = []
    file = open(os.path.normpath(os.path.join(base_path, '../後期.json')))
    data = json.load(file)

    for student_number in data.keys():
        for day in data[student_number].keys():
            documents += get_kpt_documents(data, student_number, day, 'K')
            documents += get_kpt_documents(data, student_number, day, 'P')
            documents += get_kpt_documents(data, student_number, day, 'T')

    file.close()
    return documents


def get_kpt_documents(data, student_number, day, kpt):
    global document_id
    tmp_documents = []
    date = datetime.datetime.strptime('2018年' + day, "%Y年%m月%d日")

    if kpt == 'K':
        output_kpt = 'Keep'
    elif kpt == 'P':
        output_kpt = 'Problem'
    else:
        output_kpt = 'Try'

    for sentence in data[student_number][day][kpt]:
        tmp_documents.append({
            'wakachi': get_wakachi(sentence),
            'origin': sentence,
            'student': student_number,
            'date': str(date.date()),
            'KPT': output_kpt,
            'id': document_id
        })

        document_id += 1

    return tmp_documents


def get_wakachi(sentence):
    return mecab.parse(sentence).replace(' \n', '').split()


def output_csv(documents):
    mode = 'sum'

    file = open(os.path.normpath(os.path.join(base_path, 'output/bm25/{}.csv'.format(mode))), 'w')
    writer = csv.writer(file, lineterminator='\n')
    documents.sort(key=lambda x: x[mode], reverse=True)
    writer.writerow(['student', 'day', 'origin', 'id', 'bm25', 'KPT'])

    for document in documents:
        student_name = correspondence_student_number.get_name(document['student'])
        writer.writerow([student_name, document['date'], document['origin'], document['id'], document[mode], document['KPT']])
    file.close()


def main():
    documents = get_documents()
    wakachi_documents = [x['wakachi'] for x in documents]
    results = get_bm25_weights(wakachi_documents, n_jobs=1)

    for i, result in enumerate(results):
        documents[i]['sum'] = sum(result)

    output_csv(documents)



if __name__ == '__main__':
    document_id = 0
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    base_path = os.path.dirname(os.path.abspath(__file__))
    main()
