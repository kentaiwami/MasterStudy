import json
from gensim.models import KeyedVectors
import MeCab
import csv
import datetime
import os


def main():
    for student_number in data.keys():
        tmp_file = open(os.path.normpath(os.path.join(base_path, 'output/normal/{}/{}/{}_{}.csv'.format(year, student_number, student_number, 'Problem'))), 'w')
        tmp_file.close()
        tmp_file = open(os.path.normpath(os.path.join(base_path, 'output/normal/{}/{}/{}_{}.csv'.format(year, student_number, student_number, 'Try'))), 'w')
        tmp_file.close()

        for i, day in enumerate(data[student_number].keys()):
            print('{}/{}'.format(i, len(data[student_number].keys())))

            date = datetime.datetime.strptime('{}年'.format(year) + day, "%Y年%m月%d日")
            p_list = data[student_number][day]['P']
            t_list = data[student_number][day]['T']
            k_list = get_keep(student_number, date)

            for problem_text in p_list:
                problem_distances = calc_distance(problem_text, k_list, 'Problem')
                output_csv(student_number, 'Problem', problem_distances, day)

            for try_text in t_list:
                try_distances = calc_distance(try_text, k_list, 'Try')
                output_csv(student_number, 'Try', try_distances, day)


def calc_distance(compare_text, k_list, kpt):
    distances = []
    wakachi_compare_text = mecab.parse(compare_text).replace(' \n', '').split()

    for keep_obj in k_list:
        for keep_text in keep_obj['keep']:
            wakachi_keep_text = mecab.parse(keep_text).replace(' \n', '').split()

            distances.append({
                'dis': word2vec_model.wmdistance(wakachi_compare_text, wakachi_keep_text),
                'keep': keep_text,
                'keep_day': keep_obj['day'],
                kpt: compare_text
            })

    if len(distances) == 0:
        return []

    tmp_distances = [x['dis'] for x in distances]
    ave = sum(tmp_distances) / len(tmp_distances)

    distances = [x for x in distances if x['dis'] <= ave]

    distances = sorted(distances, key=lambda x: x['dis'])

    return distances[:6]


def output_csv(student_number, kpt, distances, date):
    output_file = open(os.path.normpath(os.path.join(base_path, 'output/normal/{}/{}/{}_{}.csv'.format(year, student_number, student_number, kpt))), 'a')
    writer = csv.writer(output_file, lineterminator='\n')

    for distance in distances:
        writer.writerow([student_number, distance[kpt], date, distance['keep'], distance['keep_day'], distance['dis']])

    output_file.close()


def get_keep(student_number, pt_date):
    results = []

    for day in data[student_number].keys():
        k_date = datetime.datetime.strptime('{}年'.format(year) + day, "%Y年%m月%d日")

        if k_date < pt_date:
            continue

        results.append({'day': day, 'keep': data[student_number][day]['K']})

    return results


if __name__ == '__main__':
    year = '2017'

    if year == '2018':
        json_path = '../前期.json'
    else:
        json_path = '../../2017/前期.json'

    base_path = os.path.dirname(os.path.abspath(__file__))
    file = open(os.path.normpath(os.path.join(base_path, json_path)))
    data = json.load(file)
    file.close()

    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -Owakati")
    word2vec_model = KeyedVectors.load_word2vec_format(os.path.normpath(os.path.join(base_path, '../../model/tohoku/model.bin')), binary=True)
    main()
