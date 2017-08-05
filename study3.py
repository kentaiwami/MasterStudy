import MeCab
import CaboCha
from xml.etree import ElementTree

def init_data():
    # csv読み込み
    f = open('前期.csv')
    lines2 = f.readlines()
    f.close()

    return lines2


if __name__ == '__main__':
    doc_list = init_data()

    print(len(doc_list))