from gensim.models.word2vec import Word2Vec
import MeCab
import numpy as np
from scipy import spatial


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


# def mecab_test():

    # print(mecab.parse("彼は昨日、お腹を壊した"))


def avg_feature_vector(sentence, model, num_features):
    words = mecab.parse(sentence).replace(' \n', '').split() # mecabの分かち書きでは最後に改行(\n)が出力されてしまうため、除去
    feature_vec = np.zeros((num_features,), dtype="float32") # 特徴ベクトルの入れ物を初期化
    for word in words:
        feature_vec = np.add(feature_vec, model[word])
    if len(words) > 0:
        feature_vec = np.divide(feature_vec, len(words))
    return feature_vec


def sentence_similarity(sentence_1, sentence_2):
    # 今回使うWord2Vecのモデルは300次元の特徴ベクトルで生成されているので、num_featuresも300に指定
    num_features=50
    sentence_1_avg_vector = avg_feature_vector(sentence_1, word2vec_model, num_features)
    sentence_2_avg_vector = avg_feature_vector(sentence_2, word2vec_model, num_features)
    # １からベクトル間の距離を引いてあげることで、コサイン類似度を計算
    return 1 - spatial.distance.cosine(sentence_1_avg_vector, sentence_2_avg_vector)


if __name__ == '__main__':
    mecab = MeCab.Tagger("-Owakati")
    word2vec_model = Word2Vec.load('word2vec.gensim.model')

    result = sentence_similarity(
        "タスク管理について、ようやく着手することができた",
        "タスク管理にようやく着手できた"
    )
    print(result)
