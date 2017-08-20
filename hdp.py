import CaboCha
from xml.etree import ElementTree
from gensim import models
import gensim


cabocha = CaboCha.Parser("-u original.dic")


def extractKeyword(sentence):
    """textを形態素解析して、名詞のみのリストを返す"""
    c_tree = cabocha.parse(sentence)
    c_xml = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))

    keywords = []

    for chunk in c_xml.findall(".//chunk"):
        for tok in chunk.findall(".//tok"):
            tok_split = tok.attrib['feature'].split(',')

            if tok_split[0] == '動詞' or tok_split[0] == '形容詞':
                keywords.append(tok_split[6])
            elif tok_split[0] == '名詞' and tok_split[1] != '非自立' and tok_split[1] != '接尾':
                keywords.append(tok.text)

    return keywords


def splitDocument(sentence_list):
    """文章集合を受け取り、名詞のみ空白区切りの文章にして返す"""
    splitted_documents = []
    for d in sentence_list:
        keywords = extractKeyword(d)
        splitted_documents.append(' '.join(keywords))
    return splitted_documents


def create_file(sentence_list):
    # 空白区切りの文字列を入れるリスト
    splitted_documents = splitDocument(sentence_list)

    f = open('all_student_wakachi', 'w')
    for x in splitted_documents:
        f.write(str(x) + "\n")
    f.close()


def main(sentence_list):
    create_file(sentence_list)

    # ドキュメントからLDAなどの分析用コーパスを作成
    corpus = gensim.corpora.TextCorpus('all_student_wakachi')

    # HDPモデルの推定
    model = models.hdpmodel.HdpModel(
        corpus,
        id2word=corpus.dictionary,
        alpha=0.1)

    # 各文書のトピックの重みを保存
    topics = [model[c] for c in corpus]

    test = 'リピーターにするための手段を考えるなど、目標を達成するための細かいプロセスを考えることができた'
    index = sentence_list.index(test)
    # indexes = [i for i, x in enumerate(sentence_list) if x == test]

    target_topic = topics[index][0]

    print('---------------------------------')
    print('sentence: ', test)
    print('index: ', index)
    print('topic: ', target_topic)
    topicdata = model.print_topics(-1)
    print('topic detail: ', topicdata[target_topic[0]])

    # 各トピックごとの単語の抽出（topicsの引数を-1にすることで、ありったけのトピックを結果として返してくれます。）
    # print(model.print_topics(num_topics=20, num_words=10))

    # 文書ごとに割り当てられたトピックの確率をCSVで出力
    # mixture = [dict(model[x]) for x in corpus]
    # pandas.DataFrame(mixture).to_csv("topic_for_corpus.csv")

    # トピックごとの上位10語をCSVで出力
    # topicdata = model.print_topics(-1)
    # print('topic detail: ', topicdata[target_topic[0]])
    # pandas.DataFrame(topicdata).to_csv("topic_detail.csv")
