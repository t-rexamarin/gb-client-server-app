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
import chardet


TARGET_CHARSET = 'utf-8'


def get_encoding_type(target_file):
    with open(target_file, 'rb') as f:
        first_line = f.readline()
        current_charset = chardet.detect(first_line)['encoding']
    return current_charset


# file = 'test_file.txt'
file = 'test_file_charset_ISO-8859-15.txt'  # для проверки открытия файла с другой кодировкой
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


# - открыть файл
# - проверить кодировку
# - перекодировать файл
# - прочитать