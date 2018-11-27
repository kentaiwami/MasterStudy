def get_name(student_number):
    table = {
        '1015079': '財部圭太',
        '1016022': '板谷愛美',
        '1016117': '岡田将太朗',
        '1016127': '武信雄平',
        '1016159': '高橋莉奈',
        '1016162': '沼田夏竜'
    }

    if student_number in table:
        return table[student_number]
    else:
        return student_number
