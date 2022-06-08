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
LOGGING_LEVEL = logging.ERROR


# MODES
CLIENT_MODE_SEND = 'send'
CLIENT_MODE_LISTEN = 'listen'
DEFAULT_CLIENT_MODE = CLIENT_MODE_LISTEN


# ACTIONS
PRESENCE = 'presence'
PROBE = 'probe'
MESSAGE = 'message'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
EXIT = 'exit'


# MSG_KEYS
ACTION = 'action'
RESPONSE = 'response'
EXIT = 'exit'
ERROR = 'error'
TIME = 'time'
USER = 'user'
SENDER = 'from'
RECEIVER = 'to'
ACCOUNT_NAME = 'account_name'
MESSAGE_TEXT = 'message_text'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
ADD_CONTACT = 'add'
REMOVE_CONTACT = 'remove'
USERS_REQUEST = 'get_users'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 202
RESPONSE_202 = {
    RESPONSE: 202,
    LIST_INFO: None
}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}