"""
Задание 2.

Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя!!! методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.

Подсказки:
--- b'class' - используйте маркировку b''
--- используйте списки и циклы, не дублируйте функции
"""

class_txt = b'class'
function_txt = b'function'
method_txt = b'method'
bytes_vars_list = [class_txt, function_txt, method_txt]

for i in bytes_vars_list:
    print(f'Тип {type(i)}\n'
          f'Содержимое {i}\n'
          f'Длинна {len(i)}\n'
          f'{"-"*10}')
