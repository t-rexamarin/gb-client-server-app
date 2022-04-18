import unittest

from client import Client
from common.settings import DEFAULT_PORT, DEFAULT_IP_ADDRESS, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR
from server import Server


class ClientTests(unittest.TestCase):
    test_client_data = [
        DEFAULT_PORT,
        DEFAULT_IP_ADDRESS
    ]

    def setUp(self) -> None:
        self.test_client = Client(*self.test_client_data)
        self.test_client_started = self.test_client.start()

    def test_client_start(self):
        """
        Проверка запуска клиента
        :return:
        :rtype:
        """
        test_client_family = 'AddressFamily.AF_INET'
        test_client_type = 'SocketKind.SOCK_STREAM'

        self.assertEqual(str(self.test_client_started.family),
                         test_client_family)
        self.assertEqual(str(self.test_client_started.type),
                         test_client_type)

    """
    Не проверяется, т.к. метод connect вернет None
    """
    # def test_client_connect(self):
    #     pass

    def test_msg_structure(self):
        """
        Проверка наличия необходимых ключей в сообщении клиента
        :return:
        :rtype:
        """
        msg_keys = [
            ACTION,
            TIME,
            USER
        ]
        msg_user_keys = [
            ACCOUNT_NAME
        ]

        generated_msg = self.test_client.create_msg()
        for msg_key in msg_keys:
            self.assertIn(msg_key,
                          generated_msg,
                          f'{msg_key} отсутствует в сообщении')
            if msg_key == USER:
                for user_key in msg_user_keys:
                    self.assertIn(user_key,
                                  generated_msg[msg_key],
                                  f'{user_key} отсутствует в {msg_key}')

    def test_create_msg(self):
        """
        Проверка передачи имени пользователя в сообщение
        :return:
        :rtype:
        """
        account_name = 'new_test'
        generated_msg = self.test_client.create_msg(account_name)
        generated_msg_user = generated_msg.get(USER).get(ACCOUNT_NAME)
        self.assertEqual(generated_msg_user,
                         account_name,
                         f'Вернулось некорректное имя пользователя. '
                         f'{generated_msg_user} вместо {account_name}')

    def test_msg_ok(self):
        """
        Проверка ответа на корректное сообщение
        :return:
        :rtype:
        """
        msg_ok = {RESPONSE: 200}
        msg_ok_answer = '200 : OK'
        processed_msg = self.test_client.process_answer(msg_ok)
        self.assertEqual(processed_msg, msg_ok_answer)

    def test_msg_error(self):
        """
        Проверка ответа на НЕкорректное сообщение
        :return:
        :rtype:
        """
        msg_error = {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
        msg_error_answer = f'{msg_error[RESPONSE]} : {msg_error[ERROR]}'
        processed_msg = self.test_client.process_answer(msg_error)
        self.assertEqual(processed_msg, msg_error_answer)

    def tearDown(self) -> None:
        self.test_client_started.close()
