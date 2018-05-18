from gensim.models.word2vec import Word2Vec


def word2vec():
    model_path = 'word2vec.gensim.model'
    model = Word2Vec.load(model_path)

    # 2単語の類似度
    print(model.similarity('国王', '王妃'))
    print(model.similarity('プログラミング', 'ラーメン'))

    # 単語の加減乗除
    out = model.most_similar(positive=["女", '国王'], negative=["男"])
    for x in out:
        print(x[0], x[1])

if __name__ == '__main__':
    word2vec()
