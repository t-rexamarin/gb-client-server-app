import argparse
import configparser
import logging
import os
import select
import threading
import time
from socket import *
from common.common import Common, port_check
# from common.common import address_check
from common.decos import Log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MAX_CONNECTIONS, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, RESPONSE_200, RESPONSE_400, EXIT, RECEIVER, SENDER, \
    GET_CONTACTS, RESPONSE_202, LIST_INFO, ADD_CONTACT, USERS_REQUEST, REMOVE_CONTACT
from sys import argv, exit
from logs import server_log_config
from meta_classes import ServerVerifier

# инициализация серверного логгера
from server_db import ServerStorage

SERVER_LOGGER = logging.getLogger(server_log_config.LOGGER_NAME)


# descriptor
class Port:
    def __set_name__(self, owner, name):
        # owner - <class '__main__.Server'>
        # name - port
        self.name = name

    def __set__(self, instance, value):
        if isinstance(value, int):
            min_port, max_port = 1024, 65535
            if not min_port < value < max_port:
                raise TypeError(f'Порт должен быть в диапазоне от {min_port} до {max_port}.')
            # setattr(instance, self.name, value)  # RecursionError
            instance.__dict__[self.name] = value
        else:
            raise TypeError(f'Порт должен быть числом, передано {type(value)}')


class Server(threading.Thread, Common, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, port, url, database):
        # Параментры подключения
        self.port = port
        self.url = url
        self.database = database

        # Список подключённых клиентов
        self.clients = []
        # Список сообщений на отправку
        self.messages = []
        # Словарь содержащий сопоставленные имена и соответствующие им сокеты
        self.names = dict()

        super().__init__()

    def server_init(self):
        """
        Запуск сервера
        :return:
        :rtype:
        """
        transport = socket(AF_INET, SOCK_STREAM)
        transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # запуск на занятых портах
        transport.bind((self.url, self.port))
        transport.settimeout(0.5)
        transport.listen()
        self.server = transport
        SERVER_LOGGER.debug(f'Запуск сервера на {self.url}:{self.port}')

    def run(self):
        """
        Основной цикл программы сервера
        :return:
        :rtype:
        """
        self.server_init()

        while True:
            try:
                client, client_address = self.server.accept()
            except OSError:
                # timeout вышел, ничего не делаем
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соединение с {client_address}.')
                self.clients.append(client)

            # объявляем пустые словари
            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    # select(на чтение, на запись, ошибки)
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients,
                                                                          self.clients,
                                                                          [], 0)
            except OSError:
                # ничего не делать, если какой-то клиент отключился
                pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    processed_message = self.get_msg(client_with_message)
                    # проверка если сериализованные байты не пустые
                    if processed_message:
                        try:
                            self.process_client_message(processed_message,
                                                        client_with_message)
                        except Exception as e:
                            print(e)
                            SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                               f'отключился от сервера.')
                            # когда клиент отключился, разлогиниваем его
                            # удаляя из таблицы активных юзеров
                            for name in self.names:
                                if self.names[name] == client_with_message:
                                    self.database.user_logout(name)
                                    del self.names[name]
                                    break
                            self.clients.remove(client_with_message)

            # если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение
            for msg in self.messages:
                try:
                    self.process_message(msg, send_data_lst)
                except Exception as e:
                    print(e)
                    SERVER_LOGGER.info(f'Связь с клиентом с именем {msg[RECEIVER]} была потеряна')
                    self.clients.remove(self.names[msg[RECEIVER]])
                    # если была ошибка при обработке сообщения, то так же удалить юзера
                    # из таблицы активных
                    self.database.user_logout(msg[RECEIVER])
                    del self.names[msg[RECEIVER]]
            self.messages.clear()

    @Log()
    def process_client_message(self, message, client):
        """
        Обработка клиентского сообщения
        :param message:
        :type message: dict
        :param client:
        :type client:
        :return: словарь-ответ с результатом
        :rtype:
        """
        SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем, если успех
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            account_name = message[USER][ACCOUNT_NAME]
            if account_name not in self.names.keys():
                self.names[account_name] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(account_name, client_ip, client_port)
                self.send_msg(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                self.send_msg(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and RECEIVER in message \
                and SENDER in message \
                and TIME in message \
                and MESSAGE_TEXT in message \
                and self.names[message[SENDER]] == client:
            self.messages.append(message)
            self.database.process_message(message[SENDER], message[RECEIVER])
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and \
                ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # Если запрос листа конактов
        elif ACTION in message \
                and message[ACTION] == GET_CONTACTS \
                and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacs(message[USER])
            self.send_msg(client, response)
        # Если добавление контакта
        elif ACTION in message \
                and message[ACTION] == ADD_CONTACT \
                and ACCOUNT_NAME in message \
                and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            self.send_msg(client, RESPONSE_200)
        # Если это удаление контакта
        elif ACTION in message \
                and message[ACTION] == REMOVE_CONTACT \
                and ACCOUNT_NAME in message \
                and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            self.send_msg(client, RESPONSE_200)
        # Если это запрос известных пользователей
        elif ACTION in message \
                and message[ACTION] == USERS_REQUEST \
                and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.users_list()]
            self.send_msg(client, response)
        # Иначе отдаём Bad request
        else:
            self.send_msg(client, {
                RESPONSE: 400,
                ERROR: 'Bad request'
            })
            return

    @Log()
    def process_message(self, message, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        """
        if message[RECEIVER] in self.names \
                and self.names[message[RECEIVER]] in listen_socks:
            self.send_msg(self.names[message[RECEIVER]], message)
            SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[RECEIVER]} '
                               f'от пользователя {message[SENDER]}.')
        elif message[RECEIVER] in self.names \
                and self.names[message[RECEIVER]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'Пользователь {message[RECEIVER]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')


def print_help():
    print(
    """Поддерживаемые комманды:\n
    users - список известных пользователей\n
    connected - список подключенных пользователей\n
    loghist - история входов пользователя\n
    exit - завершение работы сервера\n
    help - вывод справки по поддерживаемым командам\n""")


def arg_parser(default_address, default_port):
    """
    Парсер параметром с которыми был запущен сервер
    :return:
    :rtype:
    """
    # nargs='?' - 0 или 1 аргумент
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('-p', default=default_port, nargs='?')
    namespace = parser.parse_args(argv[1:])  # т.к. 0 имя скрипта
    server_address = namespace.a
    server_port = namespace.p
    return server_address, server_port


def main():
    """
    server.py -p 8889 -a 127.0.0.2
    """
    # загрузка конфигурации сервера
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))  # директория исполняемого файла
    config.read(f'{dir_path}/server.ini')

    # параметры для запуска сервера
    server_address, server_port = arg_parser(config['SETTINGS']['listen_address'],
                                             config['SETTINGS']['default_port'])
    # параметры для запуска бд
    database = ServerStorage(os.path.join(config['SETTINGS']['database_path'],
                                          config['SETTINGS']['database_file']))

    server = Server(server_port, server_address, database)
    server.daemon = True
    server.start()

    print(f'Сервер запущен на {server_address}:{server_port}')
    print_help()

    while True:
        command = input('Введите команду: ')
        if command == 'exit':
            break
        elif command == 'users':
            # вывод всех известных пользователей
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            # вывод активныйх пользователей
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            # если имя пустое, вернет всех
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
