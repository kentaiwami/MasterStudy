import study
import MeCab
import CaboCha
from xml.etree import ElementTree
import re
import csv


def test2():
    worksheet_list = study.get_worksheet_list('15RsrnLlocEQhGd-m27nXL8CuJcTwIs3rG8mO1VGx6Gs')
    c = CaboCha.Parser()
    doc_list = []

    # 前処理
    for worksheet in worksheet_list:
        records = worksheet.get_all_values()
        del records[0]
        del records[0]
        del records[len(records) - 2]

        for i, record in enumerate(records):
            if i in range(0, 3):
                del record[0]
                del record[0]
            else:
                del record[0]

            record = [x for x in record if x is not '']

            for cell in record:
                for doc in cell.splitlines():
                    for one_sentence in re.split('[。.．]', doc):
                        c_tree = c.parse(one_sentence)
                        xml_root = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))

                        if len(one_sentence) != 0 and len(xml_root.findall(".//chunk")) != 1:
                            doc_list.append(one_sentence)


    # ファイル書き込み
    with open("前期.csv", "w") as f:
        writer = csv.writer(f)

        for data_row in doc_list:
            writer.writerow([data_row])

    # csv読み込み
    f = open('前期.csv')
    lines2 = f.readlines()
    f.close()

    doc_list = lines2.copy()

    # 文末の抽出
    last_tok_list = []
    for doc in doc_list:
        c_tree = c.parse(doc)
        xml_root = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))
        # print(c_tree.toString(CaboCha.FORMAT_TREE))
        # print('********************************')
        es = xml_root.findall(".//chunk[@link='-1']")

        if len(xml_root.findall(".//chunk")) == 0:
            continue

        for e in es:
            tok_list = e.findall(".//tok")

            last_tok = ''
            for tok in tok_list:
                last_tok += tok.text
                # print(tok.tag, tok.attrib, tok.text)
            # print(e.tag, e.attrib)

            last_tok_list.append(last_tok)

        # print(last_tok_list)

    # last_tok_list.sort()
    last_tok_dict = {}
    all_count = len(last_tok_list)
    for last_tok in last_tok_list:
        if last_tok in last_tok_dict:
            count = last_tok_dict[last_tok]
            last_tok_dict[last_tok] = count + 1
        else:
            last_tok_dict[last_tok] = 1

    print(sorted(last_tok_dict.items(), key=lambda x: x[1], reverse=True))

    # TODO

    exit(-1)
    for hoge in sorted(last_tok_dict.items(), key=lambda x: x[1], reverse=True):
        c_tree = c.parse(hoge[0])
        xml_root = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))

        # if len(xml_root.findall(".//chunk")) != 1:
        # tagger = MeCab.Tagger("-Owakati")
        # result = tagger.parse(hoge[0])
        print(c_tree.toString(CaboCha.FORMAT_XML), hoge)

        # print(xml_root.findall(".//chunk"), hoge)
        # print(c_tree.toString(CaboCha.FORMAT_TREE), hoge)




def test():
    a_sentence1 = u'発表原稿の細かい言葉の議論に時間をかけすぎた。プロジェクト内の発表なのであまり時間をかけすぎずうまく伝わるようにしたい。'
    a_sentence2 = u'発表原稿の細かい言葉の議論に時間をかけすぎた。'
    a_sentence3 = u'プロジェクト内の発表なのであまり時間をかけすぎずうまく伝わるようにしたい。'

    b_sentence1 = u'予定では、スライドの作成だけでなくチームの活動も行う予定だったが思った以上に長引いて予定どうりにいかなかった。時間がかかりそうなら事前にできそうなことは自分で取り組んでいきたいと感じた。'
    b_sentence2 = u'予定では、スライドの作成だけでなくチームの活動も行う予定だったが思った以上に長引いて予定通りにいかなかった。'
    b_sentence3 = u'時間がかかりそうなら事前にできそうなことは自分で取り組んでいきたいと感じた。'

    use = b_sentence3
    c = CaboCha.Parser()

    c_tree = c.parse(use)
    # print(c.parseToString(use))

    xml_root = ElementTree.fromstring(c_tree.toString(CaboCha.FORMAT_XML))

    es = xml_root.findall(".//chunk[@link='-1']")

    last_tok_list = []
    for e in es:
        tok_list = e.findall(".//tok")

        last_tok = ''
        for tok in tok_list:
            last_tok += tok.text
            # print(tok.tag, tok.attrib, tok.text)
        # print(e.tag, e.attrib)

        last_tok_list.append(last_tok)

    # print(last_tok_list)

    mecab = MeCab.Tagger("-Ochasen")
    mecab.parse("")
    node = mecab.parseToNode(use)

    # 名詞のみ抽出
    word_list = []
    while node:
        if(node.feature.split(',')[0] == '名詞'):
            word_list.append(node.surface)

        node = node.next

    # print(word_list)


if __name__ == '__main__':
    test2()