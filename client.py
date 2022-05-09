import argparse
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
    DEFAULT_PORT, DEFAULT_CLIENT_MODE, MESSAGE, CLIENT_MODE_SEND, CLIENT_MODE_LISTEN, MESSAGE_TEXT, SENDER, RECEIVER
from logs import client_log_config


# инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger(client_log_config.LOGGER_NAME)


class Client(Common):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    @Log()
    def start(self):
        client = socket(AF_INET, SOCK_STREAM)
        CLIENT_LOGGER.debug('Старт клиента')
        return client

    @Log()
    def connect(self, client):
        client_connect = client.connect((self.addr, self.port))
        CLIENT_LOGGER.debug(f'Клиент коннектится к {self.addr}:{self.port}')
        return client_connect

    @Log()
    def create_presence(self, account_name='Guest'):
        msg = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для {account_name}')
        return msg

    @Log()
    def create_msg(self, socket, account_name='Guest'):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        :param socket:
        :type socket:
        :param account_name:
        :type account_name:
        :return:
        :rtype:
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        msg = {
            ACTION: MESSAGE,
            SENDER: account_name,
            RECEIVER: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформировано {MESSAGE} сообщение для {to_user}')

        try:
            self.send_msg(socket, msg)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            exit(1)

    @Log()
    def process_server_message(self, socket, username):
        """
        Получение сообщений пришедших с сервера
        """
        while True:
            try:
                message = self.get_msg(socket)
                if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and \
                    RECEIVER in message and \
                    MESSAGE_TEXT in message and \
                    message[RECEIVER] == username:
                        print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                              f'\n{message[MESSAGE_TEXT]}')
                        CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                    f'\n{message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except:
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break

    @Log()
    def process_answer(self, message):
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'{message[RESPONSE]} : {message[ERROR]}'
        raise ValueError

    @Log()
    def user_interface(self, socket, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_msg(socket, account_name=username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
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

    if server_port and server_address:
        client = Client(server_address, server_port)
        client_running = client.start()
        client.connect(client_running)

        client.send_msg(client_running, client.create_presence(account_name=client_name))
        answer = client.process_answer(client.get_msg(client_running))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        # print(f'Установлено соединение с сервером {client_name}.')

        # запускаем клиенский процесс приёма сообщний
        receiver = threading.Thread(target=client.process_server_message, args=(client_running, client_name))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(target=client.user_interface, args=(client_running, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
