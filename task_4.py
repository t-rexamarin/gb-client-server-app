"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""
txt_vars_list = ['разработка', 'администрирование', 'protocol', 'standard']
encode_list = []

print('Кодировка в байты')
print('-'*10)
for i in txt_vars_list:
    encode_result = i.encode(encoding='utf-8')
    encode_list.append(encode_result)
    print(encode_result, type(encode_result))

print('\n')

print('Кодировка в строку')
print('-'*10)
for n in encode_list:
    decode_result = n.decode(encoding='utf-8')
    print(decode_result, type(decode_result))
