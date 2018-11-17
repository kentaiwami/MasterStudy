from gensim import corpora
from gensim import models
from pprint import pprint
import math

def main():
    documents = ['a b c d',
                 'c b c d a',
                 'b b a',
                 'c c',
                 'c b a a a a a a a a d']

    # gensim用に成形
    texts = list(map(lambda x: x.split(), documents))

    # 単語->id変換の辞書作成
    dictionary = corpora.Dictionary(texts)
    print('===単語->idの変換辞書===')
    pprint(dictionary.token2id)

    # textsをcorpus化
    corpus = list(map(dictionary.doc2bow, texts))
    print('===corpus化されたtexts===')
    pprint(corpus)

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
    for text in texts_tfidf:
        print(text)


def new_idf(docfreq, totaldocs, log_base=2.0, add=1.0):
    return add + math.log(1.0 * totaldocs / docfreq, log_base)


if __name__ == '__main__':
    main()
