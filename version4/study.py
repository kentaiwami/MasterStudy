from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
import MeCab
import numpy as np
from scipy import spatial



def word2vec(model):

    # 2単語の類似度
    print(model.similarity('ポスター', 'イーゼル'))

    # 単語の加減乗除
    # out = model.most_similar(positive=["女", '国王'], negative=["男"])
    # for x in out:
    #     print(x[0], x[1])


# def avg_feature_vector(sentence, model, num_features):
#     words = mecab.parse(sentence).replace(' \n', '').split() # mecabの分かち書きでは最後に改行(\n)が出力されてしまうため、除去
#     feature_vec = np.zeros((num_features,), dtype="float64") # 特徴ベクトルの入れ物を初期化
#     for word in words:
#         feature_vec = np.add(feature_vec, model[word])
#     if len(words) > 0:
#         feature_vec = np.divide(feature_vec, len(words))
#     return feature_vec


# def sentence_similarity(sentence_1, sentence_2, model):
#     # 今回使うWord2Vecのモデルは300次元の特徴ベクトルで生成されているので、num_featuresも300に指定
#     sentence_1_avg_vector = avg_feature_vector(sentence_1, model, num_features)
#     sentence_2_avg_vector = avg_feature_vector(sentence_2, model, num_features)
#     # １からベクトル間の距離を引いてあげることで、コサイン類似度を計算
#     return 1 - spatial.distance.cosine(sentence_1_avg_vector, sentence_2_avg_vector)


if __name__ == '__main__':
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")

#     # num_features = 200
#     # word2vec_model = Word2Vec.load('model/shiroyagi/word2vec.gensim.model')
    word2vec_model = KeyedVectors.load_word2vec_format('model/tohoku/model.bin', binary=True)

    f = open('2017/sentence5_10word.txt', 'r')
    sentences = f.readlines()
    f.close()
    sentences = [x.replace('\n', '') for x in sentences]

    target_sents = [
        'システム 案 を 絞る に なる が どの な 基準',
        'で 絞る か について も よく 考え て いき たい'
    ]

    stopword_f = open('2017/stopwords.txt', 'r')
    stopwords = stopword_f.readlines()
    stopword_f.close()
    stopwords = [x.replace('\n', '') for x in stopwords]

    for target_sent in target_sents:
#         re = []
        for sentence in sentences:
#             # Qitaのやり方
#             # result = sentence_similarity(
#             #     target_sent,
#             #     sentence,
#             #     word2vec_model
#             # )
            wakati_target_sent = mecab.parse(target_sent).replace(' \n', '').split()
            wakati_target_sent = [x for x in wakati_target_sent if x not in stopwords]
            wakati_target_sent = ' '.join(wakati_target_sent)

            wakati_sentence = mecab.parse(sentence).replace(' \n', '').split()
            wakati_sentence = [x for x in wakati_sentence if x not in stopwords]
            wakati_sentence = ' '.join(wakati_sentence)

            # WMD
            dis = word2vec_model.wmdistance(wakati_target_sent, wakati_sentence)
            # re.append(dis)

            # print(wakati_target_sent)
            # print(wakati_sentence)


            print(dis)


        # print(target_sent, sum(re)/len(re))
        print('***********************************')
