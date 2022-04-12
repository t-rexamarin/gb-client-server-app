"""
1. Задание на закрепление знаний по модулю CSV.
Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
и формирующий новый «отчетный» файл в формате CSV.
Для этого:
a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
каждого параметра поместить в соответствующий список. Должно получиться четыре
списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
функции создать главный список для хранения данных отчета — например, main_data
— и поместить в него названия столбцов отчета в виде списка: «Изготовитель
системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data (также для
каждого файла);

b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
функции реализовать получение данных через вызов функции get_data(), а также
сохранение подготовленных данных в соответствующий CSV-файл;

c. Проверить работу программы через вызов функции write_to_csv().
"""

import csv

from chardet import detect
from re import compile, match


def get_data():
    main_data = []
    files = [
        'info_1.txt',
        'info_2.txt',
        'info_3.txt'
    ]
    req_lines = [
        'Изготовитель системы',
        'Название ОС',
        'Код продукта',
        'Тип системы'
    ]
    main_data.append(req_lines)

    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    req_lines_values = [
        os_prod_list,
        os_name_list,
        os_code_list,
        os_type_list
    ]

    for file in files:
        with open(file, 'rb') as file_obj:
            content = file_obj.read()
        charset = detect(content)['encoding']
        with open(file, 'r', encoding=charset) as file_obj:
            lines = file_obj.readlines()
            for line in lines:
                for index, req_line in enumerate(req_lines):
                    reg_ex = compile(r'(?P<name>{})(:+\s)(?P<value>.+)'.format(req_line))
                    result = match(reg_ex, line)
                    if result:
                        req_lines_values[index].append(result.group('value').strip())

    for req_lines_value in req_lines_values:
        main_data.append(req_lines_value)
    return main_data


def write_to_csv():
    data = get_data()
    with open('task_1.csv', 'w') as file_obj:
        file_writer = csv.writer(file_obj)
        file_writer.writerow(data[0])  # headers
        for row in zip(data[1], data[2], data[3], data[4]):
            file_writer.writerow(row)

    with open('task_1.csv') as file_obj:
        print(file_obj.read())


write_to_csv()
