
def hoge():
    T = [80, 80, 1000000000, 80, 80, 80, 80, 80, 80, 123456789]
    # T = [3, 4, 7, 7, 6, 6]

    t_col = {}
    for t in T:
        if(t in t_col):
            t_col[t] += 1
        else:
            t_col[t] = 1

    # print(t_col)

    give = len(T) / 2

    t = sorted(t_col.items(), key=lambda x: x[1], reverse=True)

    print(t)
    index = 0

    while(give != 0):
        k, v = t[index]
        if(v != 0):
            t[index] = (k, v-1)
        else:
            index += 1
        give -= 1


    print(len(list(filter(lambda x: x[1] != 0, t))))
    return len(t)


if __name__ == '__main__':
    hoge()