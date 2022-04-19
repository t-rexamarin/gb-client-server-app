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
import time
from socket import *
from common.common import Common, port_check, address_check
from sys import argv, exit
from socket import socket
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


class Client(Common):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def start(self):
        client = socket(AF_INET, SOCK_STREAM)
        return client

    def connect(self, client):
        client_connect = client.connect((self.addr, self.port))
        return client_connect

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
            return f'{message[RESPONSE]} : {message[ERROR]}'
        raise ValueError


def main():
    # запуск сокета
    # проверки порта и адреса
    server_port = port_check(argv)
    server_address = address_check(argv)

    if server_port and server_address:
        client = Client(server_address, server_port)
        client_running = client.start()

    try:
        client.connect(client_running)
    except ConnectionRefusedError:
        print(f'На {server_address}:{server_port} сервер не найден.')
        exit(1)

    msg_to_server = client.create_msg()
    client.send_msg(client_running, msg_to_server)
    try:
        answer = client.process_answer(client.get_msg(client_running))
        print(answer)
    except ValueError:
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
