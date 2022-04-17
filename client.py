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
from common.common import Common, port_check, address_check
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
    # запуск сокета
    # проверки порта и адреса
    server_port = port_check(argv)
    server_address = address_check(argv)

    if server_port and server_address:
        c = Client(server_address, server_port)
        client = c.start()

    try:
        c.connect(client)
    except ConnectionRefusedError:
        print(f'На {server_address}:{server_port} сервер не найден.')
        exit(1)

    msg_to_server = c.create_msg()
    c.send_msg(client, msg_to_server)
    try:
        answer = c.process_answer(c.get_msg(client))
        print(answer)
    except ValueError:
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
