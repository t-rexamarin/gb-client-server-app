import argparse
import time
import logging
from socket import *
from common.common import Common, port_check
# from common.common import address_check
from sys import argv, exit
from socket import socket
from common.decos import Log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, DEFAULT_CLIENT_MODE, MESSAGE, CLIENT_MODE_SEND, CLIENT_MODE_LISTEN, MESSAGE_TEXT
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
    def create_msg(self, account_name='Guest'):
        msg = {
            ACTION: MESSAGE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            },
            MESSAGE_TEXT: 'user message'
        }
        CLIENT_LOGGER.debug(f'Сформировано {MESSAGE} сообщение для {account_name}')
        return msg

    @Log()
    def process_server_message(self, message):
        """
        Получение сообщений пришедших с сервера
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        if ACTION in message \
                and message[ACTION] == MESSAGE \
                and USER in message \
                and MESSAGE_TEXT in message:
            print(f'С сервера получено сообщение: '
                  f'{message[USER]}:\n'
                  f'{message[MESSAGE_TEXT]}.')
            CLIENT_LOGGER.info(f'С сервера получено сообщение: '
                               f'{message[USER]}:\n'
                               f'{message[MESSAGE_TEXT]}.')
        else:
            CLIENT_LOGGER.error(f'От сервера пришло сообщение с невалидной структурой: {message}.')

    @Log()
    def process_answer(self, message):
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
    parser.add_argument('-m', '--mode', default=DEFAULT_CLIENT_MODE, nargs='?')
    namespace = parser.parse_args(args[1:])  # т.к. 0 имя скрипта
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode
    return server_address, server_port, client_mode


def main():
    server_address, server_port, client_mode = arg_parser(argv)

    # запуск сокета
    # проверки порта и адреса
    server_port = port_check(server_port)
    # server_address = address_check(server_address)

    if server_port and server_address:
        client = Client(server_address, server_port)
        client_running = client.start()

    # подключаемся к серверу
    try:
        client.connect(client_running)
    except ConnectionRefusedError:
        CLIENT_LOGGER.debug(f'На {server_address}:{server_port} сервер не найден.')
        exit(1)
    else:
        # работа с сервером в зависимости от мода
        if client_mode == CLIENT_MODE_SEND:
            print('Режим работы - отправка сообщений.')
            msg_to_server = client.create_msg()
            try:
                client.send_msg(client_running, msg_to_server)
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
            # try:
            #     answer = client.process_answer(client.get_msg(client_running))
            #     # print(answer)
            #     CLIENT_LOGGER.debug(f'Ответ сервера: {answer}')
            # except ValueError:
            #     # print('Не удалось декодировать сообщение сервера.')
            #     CLIENT_LOGGER.debug(f'Не удалось декодировать сообщение сервера.')
        if client_mode == CLIENT_MODE_LISTEN:
            print('Режим работы - прием сообщений.')
            try:
                client.process_server_message(client.get_msg(client_running))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')


if __name__ == '__main__':
    main()
