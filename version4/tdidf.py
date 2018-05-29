import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction import DictVectorizer
import MeCab


def test(text):
    tagger = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    tagger.parse('')
    node = tagger.parseToNode(text).next
    keywords = []
    while node:
        if node.feature.split(",")[0] == "名詞":
            keywords.append(node.surface)
        node = node.next

    return [x for x in keywords if x != '']

if __name__ == '__main__':
    f = open('2017/1015216.txt', 'r', encoding='utf-8')
    sentences = f.readlines()
    f.close()
    sentences = [x.replace('\n', '') for x in sentences]

    wakaties = []

    for sent in sentences:
        hoge = test(sent)
        wakaties.append(' '.join(hoge))

    count = CountVectorizer()
    docs = np.array(wakaties)
    bag = count.fit_transform(docs)

    # 彼女という単語が配列の何番目に属しているか．
    # print(count.vocabulary_.get('彼女'))

    # tfidfの設定
    tfidf = TfidfTransformer(use_idf=True, norm='l2', smooth_idf=True)
    # 小数点第4位まで表示する．
    np.set_printoptions(precision=4)
    cnt_voc = count.vocabulary_
    tfidf_array = np.array(tfidf.fit_transform(bag).toarray())

    # ベクトルと単語を対応づけるために必要な処理．
    vec = DictVectorizer()
    vec.fit_transform(cnt_voc).toarray()
    feature = vec.get_feature_names()

    # tfidfの閾値の設定
    threshold = 0.5
    # ヒットした要素の数字を代入する．なぜか二つの配列で渡される．
    hairetsu = np.where(tfidf_array >= threshold)
    # np.uniqueで重複する値を削除する．
    # なぜかnp.whereだと二つの配列が返ってくるので，連結して一つにする．
    hit_word = np.unique(np.append(hairetsu[0], hairetsu[1]))

    print(feature)

    # tfidfで計算された単語を出力する．
    for num in range(0, len(hit_word)):
        print(feature[hit_word[num]])
