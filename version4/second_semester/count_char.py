import os
import json
import correspondence_student_number


def main():
    file = open(os.path.normpath(os.path.join(base_path, '../../2018/後期.json')))
    data = json.load(file)
    results = {}

    for student_number in data.keys():
        tmp_count = 0

        for day in data[student_number].keys():
            tmp_count += get_char_count_from_sentences(data[student_number][day]['K'])
            tmp_count += get_char_count_from_sentences(data[student_number][day]['P'])
            tmp_count += get_char_count_from_sentences(data[student_number][day]['T'])

        results[student_number] = tmp_count

    file.close()

    for student_number in results:
        print('{}: {}'.format(correspondence_student_number.get_name(student_number), results[student_number]))


def get_char_count_from_sentences(sentences):
    count = 0

    for sentence in sentences:
        count += len(sentence)

    return count


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))
    main()
