import os
import json
import correspondence_student_number


def main():
    file = open(os.path.normpath(os.path.join(base_path, '../後期.json')))
    data = json.load(file)
    results = {}

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

        results[student_number] = [char_count, k_count, p_count, t_count]

    file.close()

    print('char keep problem try')
    for student_number in results:
        student_name = correspondence_student_number.get_name(student_number)
        print('{}: {} {} {} {}'.format(student_name, results[student_number][0], results[student_number][1], results[student_number][2], results[student_number][3]))


def get_char_count_from_sentences(sentences):
    count = 0

    for sentence in sentences:
        count += len(sentence)

    return count


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))
    main()
