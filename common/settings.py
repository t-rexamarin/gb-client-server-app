import logging


# порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777
# ip адрес по умолчанию для сетевого взаимодействия
DEFAULT_IP_ADDRESS = '127.0.0.1'
# максимальная очередь подключений
MAX_CONNECTIONS = 5
# максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# кодировка проекта
ENCODING = 'utf-8'
# уровень логирования
# убыванию CRITICAL -> ERROR -> WARNING -> INFO -> DEBUG -> NOTSET
LOGGING_LEVEL = logging.DEBUG


# ACTIONS
PRESENCE = 'presence'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'


# MSG_KEYS
ACTION = 'action'
RESPONSE = 'response'
ERROR = 'error'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
