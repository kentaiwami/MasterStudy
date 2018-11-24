import os
import csv


def get_tfidf_ave():
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


def main():
    print(get_tfidf_ave())



if __name__ == '__main__':
    tfidf_file_path = '../2018/tfidf_output/sum_top3.csv'
    wmd_file_path = ['../2018/wmd_map_output/many.csv', '../2018/wmd_map_output/rare.csv']
    main()
