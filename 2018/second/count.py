import os
import json
import correspondence_student_number
import csv


def main():
    file = open(os.path.normpath(os.path.join(base_path, '../後期.json')))
    data = json.load(file)
    results = []

    for student_number in data.keys():
        char_count = 0
        k_count = 0
        p_count = 0
        t_count = 0

        for day in data[student_number].keys():
            char_count += get_char_count_from_sentences(data[student_number][day]['K'])
            char_count += get_char_count_from_sentences(data[student_number][day]['P'])
            char_count += get_char_count_from_sentences(data[student_number][day]['T'])

            k_count += len(data[student_number][day]['K'])
            p_count += len(data[student_number][day]['P'])
            t_count += len(data[student_number][day]['T'])

        results.append({
            'id': student_number,
            'name': correspondence_student_number.get_name(student_number),
            'char': char_count,
            'k': k_count,
            'p': p_count,
            't': t_count
        })

    file.close()

    # ファイル出力
    char_count_file = open(os.path.normpath(os.path.join(base_path, 'output/count/char.csv')), 'w')
    kpt_count_file = open(os.path.normpath(os.path.join(base_path, 'output/count/kpt.csv')), 'w')
    char_count_writer = csv.writer(char_count_file, lineterminator='\n')
    kpt_count_writer = csv.writer(kpt_count_file, lineterminator='\n')

    for result_dict in sorted(results, key=lambda x: x['char'], reverse=True):
        char_count_writer.writerow([result_dict['name'], result_dict['char']])
        kpt_count_writer.writerow([result_dict['name'], result_dict['k'], result_dict['p'], result_dict['t']])

    char_count_file.close()
    kpt_count_file.close()


def get_char_count_from_sentences(sentences):
    count = 0

    for sentence in sentences:
        count += len(sentence)

    return count


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))
    main()
