import unittest

from client import Client
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    MAX_CONNECTIONS, ERROR
from server import Server


class ServerTests(unittest.TestCase):
    test_server_data = [
        DEFAULT_PORT,
        DEFAULT_IP_ADDRESS,
        MAX_CONNECTIONS
    ]

    msg_ok = {
        ACTION: PRESENCE,
        TIME: 21.21,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }

    msg_error = {
        ACTION: 'unknown',
        TIME: 21.21,
        USER: {
            ACCOUNT_NAME: 'Guest'
        }
    }

    msg_response_ok = {RESPONSE: 200}
    msg_response_error = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }

    def setUp(self) -> None:
        """
        При запуске каждого тестового метода
        :return:
        :rtype:
        """
        self.test_server = Server(*self.test_server_data)  # объект класса
        self.test_server_started = self.test_server.start()  # пущенный сокет

    def test_start(self):
        """
        Проверка данных серверного сокета
        :return:
        :rtype:
        """
        test_server_family = 'AddressFamily.AF_INET'
        test_server_type = 'SocketKind.SOCK_STREAM'
        test_server_addr = "('127.0.0.1', 7777)"

        test_server_running_family = str(self.test_server_started.family)
        test_server_running_type = str(self.test_server_started.type)
        test_server_running_addr = str(self.test_server_started.getsockname())

        self.assertEqual(test_server_running_family,
                         test_server_family,
                         f'AddressFamily не совпдают. '
                         f'Должен быть {test_server_family}. Получили {test_server_running_family}.')
        self.assertEqual(test_server_running_type,
                         test_server_type,
                         f'SocketKind не совпдают. '
                         f'Должен быть {test_server_type}. Получили {test_server_running_type}.')
        self.assertEqual(test_server_running_addr,
                         test_server_addr,
                         f'Адрес с портом не совпадают. '
                         f'Должен быть {test_server_addr}. Получили {test_server_running_addr}.')

    def test_process_client_message_ok(self):
        """
        Прием корректного сообщения от клиента. Без запущенного серверного сокета
        :return:
        :rtype:
        """
        server_processed_msg = self.test_server.process_client_message(self.msg_ok)
        self.assertEqual(server_processed_msg, self.msg_response_ok, f'Не получили корректный ответ на сообщение.')

    def test_process_client_message_error(self):
        """
        Прием НЕкорректного сообщения от клиента. Без запущенного серверного сокета
        :return:
        :rtype:
        """
        server_processed_msg = self.test_server.process_client_message(self.msg_error)
        self.assertEqual(server_processed_msg, self.msg_response_error, f'Не получили сообщение об ошибке.')

    def test_get_msg(self):
        """
        Проверка что переданное серверу сообщение после декодирования не изменилось
        :return:
        :rtype:
        """
        test_client_data = [
            DEFAULT_IP_ADDRESS,
            DEFAULT_PORT
        ]
        test_client = Client(*test_client_data)  # создаем экземпляр клиента
        test_client_running = test_client.start()  # стартуем клиент
        test_client.connect(test_client_running)  # коннект клиента
        client, client_address = self.test_server_started.accept()  # прием клиента сервером
        client_msg = test_client.create_msg()  # генерируем сообщение клиента
        test_client.send_msg(test_client_running, client_msg)  # отправляем сообщение клиента
        msg_from_client = self.test_server.get_msg(client)  # полчаем сервером сообщение клиента
        client.close()  # закрываем коннект лкиента

        self.assertEqual(msg_from_client, client_msg, 'Обработанное сервером сообщение не совпадает с тем, что '
                                                      'отослал клиент.')

    def tearDown(self) -> None:
        """
        После каждого тестового метода
        :return:
        :rtype:
        """
        self.test_server_started.close()
