import MeCab


if __name__ == '__main__':
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    mecab.parse('')

    f = open('2017/sentence.txt', 'r')
    sentences = f.readlines()
    f.close()
    sentences = [x.replace('\n', '') for x in sentences]

    stopword_f = open('2017/stopwords.txt', 'r')
    stopwords = stopword_f.readlines()
    stopword_f.close()
    stopwords = [x.replace('\n', '') for x in stopwords]

    for sentence in sentences:
        # 名詞抽出
        node = mecab.parseToNode(sentence).next
        keywords = []
        print(mecab.parse(sentence))
        while node:
            if node.feature.split(",")[0] == "名詞":
                keywords.append(node.surface)
            node = node.next

        keywords = [x for x in keywords if x not in stopwords]
        # print(keywords)

        s = 0
        e = 10
        while(True):
            hoge = keywords[s:e]
            print(' '.join(hoge))

            if len(hoge) == 0:
                break

            s = e
            e += 10

        print('***********************************')
