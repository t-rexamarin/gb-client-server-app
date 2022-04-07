"""
Задание 1.

Каждое из слов «разработка», «сокет», «декоратор» представить
в буквенном формате и проверить тип и содержание соответствующих переменных.
Затем с помощью онлайн-конвертера преобразовать
в набор кодовых точек Unicode (НО НЕ В БАЙТЫ!!!)
и также проверить тип и содержимое переменных.

Подсказки:
--- 'разработка' - буквенный формат
--- '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430' - набор кодовых точек
--- используйте списки и циклы, не дублируйте функции
"""


def check_if_str_type(item):
    return True if type(item) is str else False


dev_txt = 'разработка'
socket_txt = 'сокет'
decorator_txt = 'декоратор'
txt_vars_list = [dev_txt, socket_txt, decorator_txt]

dev_unicode = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'  # разработка
socket_unicode = '\u0441\u043e\u043a\u0435\u0442'  # сокет
decorator_unicode = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'  # декоратор
txt_unicode_list = [dev_unicode, socket_unicode, decorator_unicode]


for i in txt_vars_list:
    if not check_if_str_type(i):
        print(f'{i} не является строкой и имеет тип {type(i)}.')

for i in txt_unicode_list:
    if not check_if_str_type(i):
        print(f'{i} не является строкой и имеет тип {type(i)}.')


if len(txt_vars_list) == len(txt_unicode_list):
    for i in zip(txt_vars_list, txt_unicode_list):
        first, second = i[0], i[1]
        if isinstance(second, type(first)):
            if first == second:
                print('Строки равны.')
        else:
            print(f'Аргументы {first} и {second} не совпадают по типу. '
                  f'{type(first)} против {type(second)}.')
else:
    print('Входные массивы имеют разную длинну. Проверка будет некорректна.')
