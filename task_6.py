"""
Задание 6.

Создать  НЕ программно (вручную) текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».

Принудительно программно открыть файл в формате Unicode и вывести его содержимое.
Что это значит? Это значит, что при чтении файла вы должны явно указать кодировку utf-8
и файл должен открыться у ЛЮБОГО!!! человека при запуске вашего скрипта.

При сдаче задания в папке должен лежать текстовый файл!

Это значит вы должны предусмотреть случай, что вы по дефолту записали файл в cp1251,
а прочитать пытаетесь в utf-8.

Преподаватель будет запускать ваш скрипт и ошибок НЕ ДОЛЖНО появиться!

Подсказки:
--- обратите внимание, что заполнять файл вы можете в любой кодировке
но открыть нужно ИМЕННО!!! в формате Unicode (utf-8)
--- обратите внимание на чтение файла в режиме rb
для последующей переконвертации в нужную кодировку

НАРУШЕНИЕ обозначенных условий - задание не выполнено!!!
"""
from chardet import detect


TARGET_CHARSET = 'utf-8'
file = 'test_file.txt'

# для проверки открытия файла с другой кодировкой
# второй вариант его перезаписывает в utf-8, надо копировать test_file_charset_ISO-8859-15_wrong.txt
# file = 'test_file_charset_ISO-8859-15.txt'


# Вариант 1
def get_encoding_type(target_file):
    with open(target_file, 'rb') as f:
        first_line = f.readline()
        current_charset = detect(first_line)['encoding']
    return current_charset


file_charset = get_encoding_type(file)
if file_charset != TARGET_CHARSET:
    with open(file, 'rb') as f:
        content = f.read()
        content = content.decode(file_charset).encode(TARGET_CHARSET)
        print(content.decode(TARGET_CHARSET))
        print(f'Файл был перекодирован из {file_charset} в {TARGET_CHARSET}')
else:
    with open(file, 'r', encoding=TARGET_CHARSET) as f:
        content = f.read()
        print(content)


# Вариант 2
# близок к примеру из урока
# мне он не нравится тем, что мы перезаписываем исходный файл
# явно в требованиях это не запрещено, но считаю это не совсем правильным
# with open(file, 'rb') as file_obj:
#     content = file_obj.read()
#     print(content)
#
# charset = detect(content)['encoding']
# text = content.decode(charset)
# with open(file, 'w', encoding=TARGET_CHARSET) as file_obj:
#     file_obj.write(text)
#
# with open(file, 'r', encoding=TARGET_CHARSET) as file_obj:
#     content = file_obj.read()
# print(content)
