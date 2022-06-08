import argparse
import configparser
import logging
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from sys import argv

from common.decos import Log
from logs import server_log_config
from common.variables import *
from server.core import MessageProcessor
from server.database import ServerStorage


# инициализация серверного логгера
from server.main_window import MainWindow

SERVER_LOGGER = logging.getLogger(server_log_config.LOGGER_NAME)


@Log()
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
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(argv[1:])  # т.к. 0 имя скрипта
    server_address = namespace.a
    server_port = namespace.p
    gui_flag = namespace.no_gui
    return server_address, server_port, gui_flag


@Log()
def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server.ini')

    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@Log()
def main():
    """
    server.py -p 8889 -a 127.0.0.2
    """
    # загрузка конфигурации сервера
    config = config_load()

    # параметры для запуска сервера
    server_address, server_port, gui_flag = arg_parser(
        config['SETTINGS']['listen_address'],
        config['SETTINGS']['default_port'])
    # параметры для запуска бд
    database = ServerStorage(os.path.join(
        config['SETTINGS']['database_path'],
        config['SETTINGS']['database_file']))

    # запуск сервера
    server = MessageProcessor(server_address, server_port, database)
    server.daemon = True
    server.start()

    # если указан параметр без GUI то запускаем простенький обработчик
    # консольного ввода
    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера. ')
            if command == 'exit':
                server.running = False
                server.join()
                break
    # если не указан запуск без gui, то запускаем gui
    else:
        # создаем графическое окружение для сервера
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        # Запускаем GUI
        server_app.exec_()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()
