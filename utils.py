import datetime


def split(text, delim=' '):
    words = []
    word = []
    for l in text:
        if l not in delim:
            word.append(l)
        else:
            if word:
                words.append(''.join(word))
                word = []
    if word:
        words.append(''.join(word))
    return words


months = {
    'Янв': 1,
    'Фев': 2,
    'Мар': 3,
    'Апр': 4,
    'Май': 5,
    'Июн': 6,
    'Июл': 7,
    'Авг': 8,
    'Сен': 9,
    'Окт': 10,
    'Ноя': 11,
    'Дек': 12,
}


def parse_date(date_str):
    y = 2000 + int(date_str[7:9])
    m = months[date_str[3:6]]
    d = int(date_str[0:2])
    h = int(date_str[10:12])
    mn = int(date_str[13:15])
    dt = datetime.datetime(y, m, d, h, mn)
    return dt


def extract_int(value):
    num = '0'
    for c in value:
        if c.isdigit():
            num += c
    return int(num)
