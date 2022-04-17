#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции клиента:
    ● сформировать presence-сообщение;
    ● отправить сообщение серверу;
    ● получить ответ сервера;
    ● разобрать сообщение сервера;
    ● параметры командной строки скрипта client.py <addr> [<port>]:
        ○ addr — ip-адрес сервера;
        ○ port — tcp-порт на сервере, по умолчанию 7777.
"""
import json
import time
from socket import *
from common.common import Common
from sys import argv, exit
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT


class Client(Common):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def start(self):
        c = self.socket_init(AF_INET, SOCK_STREAM)
        # c.connect((self.addr, self.port))
        return c

    def connect(self, client):
        return client.connect((self.addr, self.port))

    def create_msg(self, account_name='Guest'):
        msg = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        return msg

    def process_answer(self, message):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return '400 : {}'.format(message[ERROR])
        raise ValueError


def main():
    try:
        if '-p' in argv:
            server_port = int(argv[argv.index('-p') + 1])
        else:
            server_port = DEFAULT_PORT

        if server_port < 1024 or server_port > 65535:
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
            server_address = argv[argv.index('-a') + 1]
        else:
            server_address = DEFAULT_IP_ADDRESS
    except IndexError:
        print('После параметра "-a" обходимо указать адрес, который будет слушать сервер')
        exit(1)

    # запуск сокета
    c = Client(server_address, server_port)
    client = c.start()
    c.connect(client)
    msg_to_server = c.create_msg()
    c.send_msg(client, msg_to_server)
    try:
        answer = c.process_answer(c.get_msg(client))
        print(answer)
    except ValueError:
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
