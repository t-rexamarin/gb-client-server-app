import logging
from socket import *
from common.common import Common, port_check, address_check
from common.decos import Log
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MAX_CONNECTIONS
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
        server.listen(self.connections)
        SERVER_LOGGER.debug(f'Запуск сервера на {self.url}:{self.port}')
        return server

    @Log()
    def process_client_message(self, message):
        """
        Обработка клиентского сообщения
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
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
    """
    # запуск сокета
    # проверки порта и адреса
    listen_port = port_check(argv)
    listen_address = address_check(argv)

    # запускаем сервер
    if listen_port and listen_address:
        server = Server(listen_port, listen_address, MAX_CONNECTIONS)
        try:
            server_running = server.start()
        except Exception as e:
            print(e)  # не знаю, что тут может быть, поэтому так
            exit(1)

    while True:
        client, client_address = server_running.accept()

        try:
            msg_from_client = server.get_msg(client)
            response = server.process_client_message(msg_from_client)
            server.send_msg(client, response)
            client.close()
            SERVER_LOGGER.debug('Сообщенеи клиента успешно обработано')
        except ValueError:
            SERVER_LOGGER.debug('Принято некорректное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()
