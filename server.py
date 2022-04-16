#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from socket import *
from common.common import Common
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_PORT, MAX_CONNECTIONS
from sys import argv, exit


class Server(Common):
    def __init__(self, port, url, connections):
        self.port = port
        self.url = url
        self.connections = connections

    def start(self):
        s = self.socket_init(AF_INET, SOCK_STREAM)
        s.setsockopt(SOL_SOCKET, SOCK_STREAM, 1)  # запуск на занятых портах
        s.bind((self.url, self.port))
        s.listen(self.connections)
        return s

    def process_client_message(self, message):
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and USER in message \
                and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }


def main():
    """
    server.py -p 8889 -a 127.0.0.2
    :return:
    :rtype:
    """

    # считываем параметры
    # порт
    try:
        if '-p' in argv:
            listen_port = int(argv[argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT

        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра "-p" необходимо указать номер порта, на котором будет запущен сервер.')
        exit(1)
    except ValueError:
        print('Порт должен быть в диапазоне от 1024 до 65535.')
        exit(1)

    # адрес
    try:
        if '-a' in argv:
            listen_address = argv[argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print('После параметра "-a" обходимо указать адрес, который будет слушать сервер')
        exit(1)

    # запускаем сервер
    s = Server(listen_port, listen_address, MAX_CONNECTIONS)
    server = s.start()

    while True:
        client, client_address = server.accept()
        try:
            msg_from_client = s.get_msg(client)
            print(msg_from_client)

            response = s.process_client_message(msg_from_client)
            s.send_msg(client, response)
            client.close()
        except ValueError:
            print('Принято некорректное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()
