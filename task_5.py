"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""
import chardet
import subprocess


urls_list = [
    'yandex.ru',
    'youtube.com'
]


def print_func(item):
    ping_proc = subprocess.Popen(['ping', '-c4', item], stdout=subprocess.PIPE)
    for line in ping_proc.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8').strip())


for i in urls_list[:-1]:
    print_func(i)
    print('\n' + '*' * 15 + '\n')
print_func(urls_list[-1])

