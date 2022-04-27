"""
...в логе должна быть отражена информация:
"<дата-время> Функция func_z() вызвана из функции main"
"""
# import inspect
import traceback
import logging
import sys
from logs import server_log_config, client_log_config


called_source = sys.argv[0]  # приходит абсолютный путь к файлу, как str
called_file = called_source.split('/')[-1]  # берем последний файл в пути
if called_file.find('client') == -1:
    # если не клиент, то пишем в серверные логи
    LOGGER = logging.getLogger(server_log_config.LOGGER_NAME)
else:
    # иначе пишем в клиента
    LOGGER = logging.getLogger(client_log_config.LOGGER_NAME)


class Log:
    """
    класс-логер вызванных функций
    """
    def __call__(self, func):
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            LOGGER.debug(f'Была вызвана функция {func.__name__} с параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {func.__module__}. '
                         f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.')
                         # f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)  # не для python 3.6
            return result
        return decorated
