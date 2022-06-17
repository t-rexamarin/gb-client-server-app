import socket
import traceback
import logging
import sys
from logs import server_log_config, client_log_config

sys.path.append('../')

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
    Класс-логер вызванных функций
    """
    def __call__(self, func):
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            LOGGER.debug(f'Была вызвана функция {func.__name__} с параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {func.__module__}. '
                         f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.')
            return result
        return decorated


def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в списке авторизованных клиентов.
    За исключением передачи словаря-запроса на авторизацию.
    Если клиент не авторизован, генерирует исключение TypeError
    :param func:
    :type func:
    :return:
    :rtype:
    """
    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр MessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from pack_server.server import MessageProcessor
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence сообщение.
            # Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
