import argparse
import logging
import select
import time
from socket import *
from common.common import Common, port_check
# from common.common import address_check
from common.decos import Log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MAX_CONNECTIONS, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, RESPONSE_200, RESPONSE_400, EXIT, RECEIVER, SENDER
from sys import argv, exit
from logs import server_log_config


# инициализация серверного логгера
SERVER_LOGGER = logging.getLogger(server_log_config.LOGGER_NAME)


class Server(Common):
    @Log()
    def __init__(self, port, url, connections):
        self.port = port
        self.url = url
        self.connections = connections

    @Log()
    def start(self):
        """
        Запуск сервера
        :return:
        :rtype:
        """
        server = socket(AF_INET, SOCK_STREAM)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # запуск на занятых портах
        server.bind((self.url, self.port))
        server.settimeout(0.5)
        server.listen(self.connections)
        SERVER_LOGGER.debug(f'Запуск сервера на {self.url}:{self.port}')
        return server

    @Log()
    def process_client_message(self, message, messages_list, client, clients, names):
        """
        Обработка клиентского сообщения
        :param message:
        :type message: dict
        :param messages_list:
        :type messages_list:
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
                and USER in message \
                and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                self.send_msg(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                self.send_msg(client, response)
                clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and TIME in message \
                and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and \
            ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            self.send_msg(client, {
                RESPONSE: 400,
                ERROR: 'Bad request'
            })
        return

    @Log()
    def process_message(self, message, names, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        """
        if message[RECEIVER] in names \
            and names[message[RECEIVER]] in listen_socks:
                self.send_msg(names[message[RECEIVER]], message)
                SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[RECEIVER]} '
                    f'от пользователя {message[SENDER]}.')
        elif message[RECEIVER] in names \
            and names[message[RECEIVER]] not in listen_socks:
                raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'Пользователь {message[RECEIVER]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')


def arg_parser(args):
    """
    Парсер параметром с которыми был запущен сервер
    :return:
    :rtype:
    """
    # nargs='?' - 0 или 1 аргумент
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-p', default=DEFAULT_PORT, nargs='?')
    namespace = parser.parse_args(args[1:])  # т.к. 0 имя скрипта
    server_address = namespace.a
    server_port = namespace.p
    return server_address, server_port


def main():
    """
    server.py -p 8889 -a 127.0.0.2
    """
    server_address, server_port = arg_parser(argv)

    # запуск сокета
    # проверки порта и адреса
    server_port = port_check(server_port)
    # listen_address = address_check(argv)  # deprecated

    # запускаем сервер
    if server_port and server_address:
        server = Server(server_port, server_address, MAX_CONNECTIONS)
        try:
            server_running = server.start()
        except Exception as e:
            print(e)  # не знаю, что тут может быть, поэтому так
            exit(1)

    # список клиентов, очередь сообщений
    clients = []
    messages = []

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()

    # работа сервера
    while True:
        try:
            client, client_address = server_running.accept()
        except OSError:
            # timeout вышел, ничего не делаем
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с {client_address}.')
            clients.append(client)

        # объявляем пустые словари
        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                # select(на чтение, на запись, ошибки)
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            # ничего не делать, если какой-то клиент отключился
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                processed_message = server.get_msg(client_with_message)
                # проверка если сериализованные байты не пустые
                if processed_message:
                    try:
                        server.process_client_message(processed_message,
                                                      messages,
                                                      client_with_message,
                                                      clients,
                                                      names)
                    except Exception as e:
                        print(e)
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                           f'отключился от сервера.')
                        clients.remove(client_with_message)

        # если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение
        for i in messages:
            try:
                server.process_message(i, names, send_data_lst)
            except Exception as e:
                print(e)
                SERVER_LOGGER.info(f'Связь с клиентом с именем {i[RECEIVER]} была потеряна')
                clients.remove(names[i[RECEIVER]])
                del names[i[RECEIVER]]
        messages.clear()


if __name__ == '__main__':
    main()
