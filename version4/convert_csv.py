import csv
import datetime


def main():
    pt_list = ['P', 'T']
    pt_name_list = ['Problem', 'Try']
    student = '2117009'
    year = '2018'

    for pt in zip(pt_list, pt_name_list):
        output_file = open('2018/convert/{}/{}.csv'.format(student, pt[0]), 'a')
        writer = csv.writer(output_file, lineterminator='\n')

        ave_file = open('2018/output/{}/{}_ave.csv'.format(student, pt[0]), 'r')
        min_file = open('2018/output/{}/{}_min.csv'.format(student, pt[0]), 'r')

        aveReader = list(csv.reader(ave_file))
        minReader = list(csv.reader(min_file))

        if len(aveReader) != len(minReader):
            output_file.close()
            ave_file.close()
            min_file.close()
            raise Exception('Error')

        writer.writerow([pt[1], '{}の記述日'.format(pt[1]), 'ステータス', '関連するKeep', 'Keepの記述日','該当文の選択'])

        # aveminResultsリストの中身
        # [0]:記述日
        # [1]:記述場所
        # [2]:距離
        # [3]:文章
        k_ave_list = []
        k_min_list = []
        target_group_list = []

        latest_target_day = ''
        latest_target_sentence = ''

        for aveminResults in zip(aveReader, minReader):
            if aveminResults[0][2] == '' and len(k_ave_list) != 0:
                target_group_list.append({
                    'keep': merge_keep(k_ave_list, k_min_list),
                    'target_day': latest_target_day,
                    'target_sentence': latest_target_sentence
                })

            if aveminResults[0][2] == '':
                latest_target_day = aveminResults[0][0]
                latest_target_sentence = aveminResults[0][3]
                k_ave_list = []
                k_min_list = []
            else:
                k_ave_list.append({'day': aveminResults[0][0], 'distance': aveminResults[0][2], 'sentence': aveminResults[0][3]})
                k_min_list.append({'day': aveminResults[1][0], 'distance': aveminResults[1][2], 'sentence': aveminResults[1][3]})

        target_group_list.append({
            'keep': merge_keep(k_ave_list, k_min_list),
            'target_day': latest_target_day,
            'target_sentence': latest_target_sentence
        })

        for target_group in sorted(target_group_list, key=lambda x: str2date(x['target_day'], year)):
            writer.writerow([target_group['target_sentence'], target_group['target_day'], '未解決', '', '', 'FALSE'])

            for keep in target_group['keep']:
                writer.writerow(['', '', '', keep['sentence'], keep['day']])

        ave_file.close()
        min_file.close()
        output_file.close()


def merge_keep(k_ave_list, k_min_list):
    results = []
    for k_avemin in zip(k_ave_list, k_min_list):
        if len([x for x in results if x['sentence'] == k_avemin[0]['sentence']]) == 0:
            results.append(k_avemin[0])

        if len([x for x in results if x['sentence'] == k_avemin[1]['sentence']]) == 0:
            results.append(k_avemin[1])

    return results


def str2date(d, year):
    tmp = datetime.datetime.strptime('{}年{}'.format(year, d), '%Y年%m月%d日')
    return datetime.date(tmp.year, tmp.month, tmp.day)


if __name__ == '__main__':
    main()
