from gensim import corpora
from gensim import models
import math
import json
import datetime
import MeCab
import csv


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
        tfidf_list = [word_tfidf[1] for word_tfidf in text]

        documents[i]['sum'] = sum(tfidf_list)
        documents[i]['ave'] = sum(tfidf_list) / len(text)
        documents[i]['min'] = min(tfidf_list)
        documents[i]['max'] = max(tfidf_list)

        print(documents[i])


    # ===csvへ出力===
    output_csv(documents)


def output_csv(documents):
    # sum, ave, min, max
    mode = 'max'

    file = open('../2018/tfidf_output/output_{}.csv'.format(mode), 'w')
    writer = csv.writer(file, lineterminator='\n')
    documents.sort(key=lambda x: x[mode], reverse=True)
    writer.writerow(['student', 'date', 'origin', mode])

    for document in documents:
        writer.writerow([document['student'], document['date'], document['origin'], document[mode]])
    file.close()


def new_idf(docfreq, totaldocs, log_base=2.0, add=1.0):
    return add + math.log(1.0 * totaldocs / docfreq, log_base)


def get_stopwords():
    stopword_f = open('../2018/stopwords.txt', 'r')
    stopwords = stopword_f.readlines()
    stopword_f.close()
    stopwords = [x.replace('\n', '') for x in stopwords]

    return stopwords


def get_wakachi(sentence):
    stopwords = get_stopwords()
    sentence_list = mecab.parse(sentence).replace(' \n', '').split()
    wakachi_list = [x for x in sentence_list if x not in stopwords]

    return ' '.join(wakachi_list)


def get_documents():
    documents = []
    file = open("../2018/後期.json")
    data = json.load(file)

    for student_number in data.keys():
        for day in data[student_number].keys():
            date = datetime.datetime.strptime('2018年' + day, "%Y年%m月%d日")
            documents += [{'wakachi': get_wakachi(keep_sentence), 'origin': keep_sentence, 'student': student_number, 'date': str(date.date())} for keep_sentence in data[student_number][day]['K']]
            documents += [{'wakachi': get_wakachi(problem_sentence), 'origin': problem_sentence, 'student': student_number, 'date': str(date.date())} for problem_sentence in data[student_number][day]['P']]
            documents += [{'wakachi': get_wakachi(try_sentence), 'origin': try_sentence, 'student': student_number, 'date': str(date.date())} for try_sentence in data[student_number][day]['T']]

    print(documents)
    return documents


if __name__ == '__main__':
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    main()
