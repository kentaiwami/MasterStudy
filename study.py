import os
import random
import re
import gspread as gspread
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from oauth2client.service_account import ServiceAccountCredentials
import MeCab
import CaboCha


def get_wakachi_list(doc):

    tagger = MeCab.Tagger("-Owakati")
    result = tagger.parse(doc)

    # Make word list
    ws = re.compile(" ")
    words = ws.split(result)
    if words[-1] == u"\n":
        words = words[:-1]

    return words


def get_worksheet_list(doc_id):
    scope = ['https://spreadsheets.google.com/feeds']
    path = os.path.expanduser("key.json")

    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gspread.authorize(credentials)
    gfile = client.open_by_key(doc_id)
    worksheet_list = gfile.worksheets()

    return worksheet_list


def learn_doc2vec(doc_list, save):
    training_docs = []
    for i, doc in enumerate(doc_list):
        sent_tmp = TaggedDocument(words=get_wakachi_list(doc), tags=['d' + str(i)])
        training_docs.append(sent_tmp)

    # 学習実行（パラメータを調整可能）
    # documents:学習データ（TaggedDocumentのリスト）
    # min_count=1:最低1回出現した単語を学習に使用する
    # dm=0:学習モデル=DBOW（デフォルトはdm=1:学習モデル=DM）
    model = Doc2Vec(documents=training_docs, min_count=1, dm=1, size=100)

    if save:
        # 学習したモデルを保存
        model.save('doc2vec.model')
    else:
        # 保存したモデルを読み込む場合
        model = Doc2Vec.load('doc2vec.model')

    return model


def show_result(model, doc_list):
    # 各文書と最も類似度が高い文書を表示（デフォルト値：10個)
    test_number = random.randint(0, len(doc_list) - 1)
    # test_number = len(doc_list)-1
    print(doc_list[test_number])
    print('******************************************************************************************')
    results = model.docvecs.most_similar('d' + str(test_number))
    for result in results:
        doc_number = result[0].replace('d', '')
        print(doc_list[int(doc_number)] + ', ' + str(result[1]))


def study1():
    """
    対象：2017年の週報(前期)
    学習方法：全学生の文を1つのモデルとして学習
    """
    worksheet_list = get_worksheet_list('1KafunKBEgpL5P3N0zDM6u8_Wh5U4djcTrDoaHHq7oBQ')

    doc_list = []
    # 前処理
    for worksheet in worksheet_list:
        records = worksheet.get_all_values()
        del records[0]
        del records[0]
        del records[len(records)-2]

        for i, record in enumerate(records):
            if i in range(0, 3):
                del record[0]
                del record[0]
            else:
                del record[0]

            record = [x for x in record if x is not '']

            for cell in record:
                for doc in cell.splitlines():
                    doc_list.append(doc)

    # for doc in doc_list:
    #     print(doc)

    model = learn_doc2vec(doc_list, True)
    show_result(model, doc_list)


def study2():
    """
    対象：2016年の週報(前期)
    学習方法：全学生の文を1つのモデルとして学習
    """
    worksheet_list = get_worksheet_list('179FfHbHwwwh7PU2nbo3-sd2ZGgaa-JiP4Q-n0YfQ6Gs')

    doc_list = []
    # 前処理

    for worksheet in worksheet_list:
        records = worksheet.get_all_values()

        del records[0]

        tmp_record = []
        for record in records:
            tmp = [x for x in record if x is not '']

            if len(tmp) != 0:
                tmp_record.append(tmp)

        for trs in tmp_record:
            for tr in trs:
                doc_list.append(tr)

    model = learn_doc2vec(doc_list, True)
    show_result(model, doc_list)


def mecab_cabocha_test():
    sentence = '発表原稿の細かい言葉の議論に時間をかけすぎた。プロジェクト内の発表なのであまり時間をかけすぎずうまく伝わるようにしたい。'

    c = CaboCha.Parser()
    print(c.parseToString(sentence))
    tree = c.parse(sentence)
    # print(tree.toString(CaboCha.FORMAT_TREE))
    print(tree.toString(CaboCha.FORMAT_LATTICE))

    m = MeCab.Tagger("-Ochasen")
    print(m.parse(sentence))

if __name__ == '__main__':
    study2()
