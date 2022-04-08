"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""
txt_vars_list = [
    'attribute',
    'класс',
    'функция',
    'type'
    ]


# Вариант 1
# первое что накостылил, т.к. не мог понять, как совместить литерал b и переменную
# а писать каждое слово с префиксом b полная фигня
# у меня python 3.6 и я не могу использовать str.isascii()
def check_non_ascii(string):
    for char in string:
        if 0 <= ord(char) <= 127:
            return 1
        else:
            return 0


for item in txt_vars_list:
    if check_non_ascii(item):
        b = bytes(item, encoding='ascii')
        print(f'"{item}" успешно переведен в байты {b}')
    else:
        print(f'"{item}" не можеть быть переведен в байты {b}')


# Вариант 2
# for item in txt_vars_list:
#     try:
#         b = bytes(item, 'ascii')
#         print(f'"{item}" успешно кодируется в байты - {b}.')
#     except UnicodeEncodeError:
#         print(f'"{item}" невозможно записать в байты без доп. кодирования.')


# Вариант 3
# for item in txt_vars_list:
#     try:
#         print(f'"{item}" успешно кодируется в байты через префикс b\'', eval(f'b"{item}"'))
#     except SyntaxError:
#         print(f'"{item}" невозможно записать в байтовом типе с помощью префикса b')
