import argparse
import json
import sys
import threading
import time
import logging
from socket import *
from sys import argv, exit
from socket import socket

from PyQt5.QtWidgets import QApplication

from client.database import ClientDatabase
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog
from client.transport import ClientTransport
from common.decos import Log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, DEFAULT_CLIENT_MODE, MESSAGE, CLIENT_MODE_SEND, CLIENT_MODE_LISTEN, MESSAGE_TEXT, SENDER, RECEIVER, \
    EXIT
from logs import client_log_config
from meta_classes import ClientVerifier


# инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger(client_log_config.LOGGER_NAME)


def arg_parser():
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
    namespace = parser.parse_args(sys.argv[1:])  # т.к. 0 имя скрипта
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    return server_address, server_port, client_name


def main():
    # загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    client_app = QApplication(sys.argv)

    # если имя пользователя не было указано в командной строке, то запрашиваем его
    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        # если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект, иначе выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    database = ClientDatabase()

    try:
        transport = ClientTransport(server_port,
                                    server_address,
                                    database,
                                    client_name)
    except ERROR as err:
        print(err.text)
        exit(1)
    else:
        transport.setDaemon(True)
        transport.start()

        # создаем gui
        main_window = ClientMainWindow(database, transport)
        main_window.make_connection(transport)
        main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
        client_app.exec_()

        # раз графическая оболочка закрылась, закрываем транспорт
        transport.transport_shutdown()
        transport.join()


if __name__ == '__main__':
    main()
