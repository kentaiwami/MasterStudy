from gensim import corpora
from gensim import models
import math
import json
import datetime
import MeCab
import csv
import correspondence_student_number
import os
import sys
from distutils.util import strtobool


def main():
    documents = get_documents()
    wakachi_documents = [x['wakachi'] for x in documents]

    # gensim用に成形
    texts = list(map(lambda x: x.split(), wakachi_documents))

    # 単語->id変換の辞書作成
    dictionary = corpora.Dictionary(texts)
    print('===単語->idの変換辞書===')
    # pprint(dictionary.token2id)

    # textsをcorpus化
    corpus = list(map(dictionary.doc2bow, texts))
    print('===corpus化されたtexts===')
    # pprint(corpus)

    # tfidf modelの生成
    test_model = models.TfidfModel(corpus, wglobal=new_idf, normalize=False)
    # corpusへのモデル適用
    corpus_tfidf = test_model[corpus]

    # id->単語へ変換
    texts_tfidf = []  # id -> 単語表示に変えた文書ごとのTF-IDF
    for doc in corpus_tfidf:
        text_tfidf = []
        for word in doc:
            text_tfidf.append([dictionary[word[0]], word[1]])
        texts_tfidf.append(text_tfidf)

    # 表示
    print('===結果表示===')
    for i, text in enumerate(texts_tfidf):
        tmp_tfidf_list = [word_tfidf[1] for word_tfidf in text]

        if is_top3:
            tfidf_list = sorted(tmp_tfidf_list, reverse=True)[:3]
        else:
            tfidf_list = tmp_tfidf_list

        documents[i]['sum'] = sum(tfidf_list)
        documents[i]['ave'] = sum(tfidf_list) / len(tfidf_list)
        documents[i]['min'] = min(tfidf_list)
        documents[i]['max'] = max(tfidf_list)

        print(documents[i])


    # ===csvへ出力===
    output_csv(documents)


def output_csv(documents):
    # sum, ave, min, max
    # aveとsumはis_top3の状態では上位100件くらいまでは同じ結果

    mode = 'sum'

    if is_top3:
        name = '_top3'
    else:
        name = ''

    file = open(os.path.normpath(os.path.join(base_path, 'output/tfidf/{}{}.csv'.format(mode, name))), 'w')
    writer = csv.writer(file, lineterminator='\n')
    documents.sort(key=lambda x: x[mode], reverse=True)
    writer.writerow(['student', 'day', 'origin', 'id', 'tfidf', 'KPT'])

    for document in documents:
        student_name = correspondence_student_number.get_name(document['student'])
        writer.writerow([student_name, document['date'], document['origin'], document['id'], document[mode], document['KPT']])
    file.close()


def new_idf(docfreq, totaldocs, log_base=2.0, add=1.0):
    return add + math.log(1.0 * totaldocs / docfreq, log_base)


def get_wakachi(sentence):
    sentence_list = mecab.parse(sentence).replace(' \n', '').split()
    return ' '.join(sentence_list)


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


def check_argv():
    if len(sys.argv) == 1:
        raise ValueError

    try:
        tmp_is_top3 = strtobool(sys.argv[1])
    except ValueError:
        raise ValueError

    return tmp_is_top3


if __name__ == '__main__':
    is_top3 = check_argv()
    document_id = 0
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    base_path = os.path.dirname(os.path.abspath(__file__))
    main()
