import argparse
import json
import threading
import time
import logging
from socket import *
from common.common import Common, port_check
# from common.common import address_check
from sys import argv, exit
from socket import socket
from common.decos import Log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, DEFAULT_CLIENT_MODE, MESSAGE, CLIENT_MODE_SEND, CLIENT_MODE_LISTEN, MESSAGE_TEXT, SENDER, RECEIVER, \
    EXIT
from logs import client_log_config
from meta_classes import ClientVerifier


# инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger(client_log_config.LOGGER_NAME)


# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем
class ClientSender(threading.Thread, Common, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        """
        Cоздаёт словарь с сообщением о выходе
        :return:
        :rtype:
        """
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_msg(self):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        :return:
        :rtype:
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        msg = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            RECEIVER: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформировано {MESSAGE} сообщение для {to_user}')

        try:
            self.send_msg(self.sock, msg)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            exit(1)

    def user_interface(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_msg()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.send_msg(self.sock, self.create_exit_message())
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @staticmethod
    def print_help():
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


class ClientReader(threading.Thread, Common, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def process_server_message(self):
        """
        Получение сообщений пришедших с сервера
        """
        while True:
            try:
                message = self.get_msg(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and \
                    RECEIVER in message and \
                    MESSAGE_TEXT in message and \
                    message[RECEIVER] == self.account_name:
                        print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                              f'\n{message[MESSAGE_TEXT]}')
                        CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                    f'\n{message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except:
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break


def create_presence(account_name):
    msg = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для {account_name}')
    return msg


def process_answer(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'{message[RESPONSE]} : {message[ERROR]}'
    raise ValueError


def arg_parser(args):
    """
    Парсер параметром с которыми был запущен клиент
    :return:
    :rtype:
    """
    # nargs='?' - 0 или 1 аргумент
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(args[1:])  # т.к. 0 имя скрипта
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    return server_address, server_port, client_name


def main():
    """Сообщаем о запуске"""
    print('Консольный месседжер. Клиентский модуль.')

    server_address, server_port, client_name = arg_parser(argv)

    # запуск сокета
    # проверки порта
    server_port = port_check(server_port)

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиент - {client_name}')
    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # инициализация сокета
    if server_port and server_address:
        try:
            transport = socket(AF_INET, SOCK_STREAM)
            transport.connect((server_address, server_port))

            # отсылаем серверу сообщение о своем присутствии
            initiation = Common()
            initiation.send_msg(transport, create_presence(client_name))
            answer = process_answer(initiation.get_msg(transport))
            CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print('Установлено соединение с сервером.')
        except json.JSONDecodeError:
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            exit(1)
        except (ConnectionRefusedError, ConnectionError):
            CLIENT_LOGGER.critical(
                f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                f'конечный компьютер отверг запрос на подключение.')
            exit(1)
        else:
            # Если соединение с сервером установлено, запускаем клиенский процесс приёма сообщений
            client_reader = ClientReader(client_name, transport)
            client_reader.daemon = True
            # client_reader.setDaemon(True)
            client_reader.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем
            client_sender = ClientSender(client_name, transport)
            client_sender.daemon = True
            client_sender.start()

            CLIENT_LOGGER.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if client_reader.is_alive() and client_sender.is_alive():
                    continue
                break


if __name__ == '__main__':
    main()
