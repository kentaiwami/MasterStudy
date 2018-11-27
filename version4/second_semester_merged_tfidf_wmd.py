import os
import csv


def get_tfidf_ave():
    """
    全文章のtf-idfの値から平均値を求める
    """

    if not os.path.isfile(tfidf_file_path) or not os.path.isfile(wmd_file_path[0]) or not os.path.isfile(wmd_file_path[1]):
        raise FileNotFoundError


    tfidf_file = open(tfidf_file_path, 'r')
    tfidf_dataReader = csv.reader(tfidf_file)
    tfidf_sum = 0.0

    for i, row in enumerate(tfidf_dataReader):
        if i == 0:
            continue

        tfidf_sum += float(row[4])

    tfidf_file.close()

    return tfidf_sum / i


def get_document_id_less_than_ave(ave):
    """
    平均値よりtf-idf値が少ないdocument_idのリストを取得
    :param ave: 全文章のtf-idf値から算出した平均値
    """

    tfidf_file = open(tfidf_file_path, 'r')
    tfidf_dataReader = csv.reader(tfidf_file)
    document_ids = []

    for i, row in enumerate(tfidf_dataReader):
        if i == 0:
            continue

        if float(row[4]) <= ave:
            document_ids.append(int(row[3]))

    return document_ids


def coordination_wmd(remove_document_ids):
    """
    tf-idfの値が平均値より少ないドキュメントをwmdの結果から削除し、tf-idfの高い順に合わせてwmdの結果を並び替えたリストを返す
    :param remove_document_ids: wmdの結果から削除すべきdocument_id（tf-idfの平均値より低いドキュメント）
    """

    wmd_file = open(wmd_file_path[1], 'r')
    wmd_dataReader = csv.reader(wmd_file)
    wmd_list = []

    """
    wmdの作業用リスト辞書を作成
    """
    for i, row in enumerate(wmd_dataReader):
        if i == 0:
            continue

        wmd_list.append({
            'student': row[0],
            'date': row[1],
            'origin': row[2],
            'id': int(row[3]),
            'KPT': row[4]
        })

    wmd_file.close()


    """
    tfidfの作業用リストを作成
    """
    tmp_tfidf_document_ids = []
    tfidf_file = open(tfidf_file_path, 'r')
    tfidf_dataReader = csv.reader(tfidf_file)

    for i, row in enumerate(tfidf_dataReader):
        if i == 0:
            continue

        tmp_tfidf_document_ids.append(int(row[3]))

    tfidf_file.close()


    """
    tfidfが平均値以下のドキュメントをwmdの結果から削除
    """
    for remove_id in remove_document_ids:
        tmp_result = [x for x in wmd_list if x['id'] == remove_id]

        if len(tmp_result) == 0:
            continue

        wmd_list.remove(tmp_result[0])


    """
    tfidfの順番に沿うようにwmdを並び替え
    """
    sorted_wmd_list = []

    for i, wmd_dict in enumerate(wmd_list, 1):
        if wmd_dict['id'] in tmp_tfidf_document_ids:
            sort_id = tmp_tfidf_document_ids.index(wmd_dict['id'])
        else:
            sort_id = len(wmd_list) + i

        sorted_wmd_list.append({
            'sort_id': sort_id,
            'student': wmd_dict['student'],
            'date': wmd_dict['date'],
            'origin': wmd_dict['origin'],
            'id': wmd_dict['id'],
            'KPT': wmd_dict['KPT']
        })

    sorted_wmd_list = sorted(sorted_wmd_list, key=lambda x: x['sort_id'])

    return sorted_wmd_list


def output_csv(sorted_wmd_list):
    output_file = open('../2018/tfidf_wmd_merge/merged_rare.csv', 'w')
    writer = csv.writer(output_file, lineterminator='\n')
    writer.writerow(['student', 'date', 'origin', 'id', 'KPT', 'sort_id'])

    for wmd_dict in sorted_wmd_list:
        writer.writerow([wmd_dict['student'], wmd_dict['date'], wmd_dict['origin'], wmd_dict['id'], wmd_dict['KPT'], wmd_dict['sort_id']])

    output_file.close()


def main():
    tfidf_ave = get_tfidf_ave()
    remove_document_ids = get_document_id_less_than_ave(tfidf_ave)
    sorted_wmd_list = coordination_wmd(remove_document_ids)
    output_csv(sorted_wmd_list)


if __name__ == '__main__':
    tfidf_file_path = '../2018/tfidf_output/sum_top3.csv'
    wmd_file_path = ['../2018/wmd_map_output/many.csv', '../2018/wmd_map_output/rare.csv']
    main()
