import MeCab


if __name__ == '__main__':
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")

    f = open('2017/sentence5.txt', 'r')
    sentences = f.readlines()
    f.close()
    sentences = [x.replace('\n', '') for x in sentences]

    stopword_f = open('2017/stopwords.txt', 'r')
    stopwords = stopword_f.readlines()
    stopword_f.close()
    stopwords = [x.replace('\n', '') for x in stopwords]

    for sentence in sentences:
        wakati_sentence = mecab.parse(sentence).replace(' \n', '').split()
        wakati_sentence = [x for x in wakati_sentence if x not in stopwords]
        wakati_sentence = ' '.join(wakati_sentence)

        print(wakati_sentence)

        wakati_list = wakati_sentence.split(' ')

        s = 0
        e = 10
        while(True):
            hoge = wakati_list[s:e]
            print(' '.join(hoge))

            if len(hoge) == 0:
                break

            s = e
            e += 10

        print('***********************************')