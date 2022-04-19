import unittest
from client import Client
from common.settings import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


class ClientTests(unittest.TestCase):
    test_client_data = [
        DEFAULT_PORT,
        DEFAULT_IP_ADDRESS
    ]

    def setUp(self) -> None:
        """
        При запуске каждого тестового метода
        :return:
        :rtype:
        """
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

        test_client_running_family = str(self.test_client_started.family)
        test_client_running_type = str(self.test_client_started.type)

        self.assertEqual(test_client_running_family,
                         test_client_family,
                         f'AddressFamily не совпдают. '
                         f'Должен быть {test_client_family}. Получили {test_client_running_family}.')
        self.assertEqual(test_client_running_type,
                         test_client_type,
                         f'SocketKind не совпдают. '
                         f'Должен быть {test_client_type}. Получили {test_client_running_type}.')

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
                          f'{msg_key} отсутствует в сообщении.')
            if msg_key == USER:
                for user_key in msg_user_keys:
                    self.assertIn(user_key,
                                  generated_msg[msg_key],
                                  f'{user_key} отсутствует в {msg_key}.')

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
                         f'{generated_msg_user} вместо {account_name}.')

    def test_msg_ok(self):
        """
        Проверка ответа на корректное сообщение
        :return:
        :rtype:
        """
        msg_ok = {RESPONSE: 200}
        msg_ok_answer = '200 : OK'
        processed_msg = self.test_client.process_answer(msg_ok)
        self.assertEqual(processed_msg,
                         msg_ok_answer,
                         f'Неполучен положительный ответ на корректное сообщение.')

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
        self.assertEqual(processed_msg,
                         msg_error_answer,
                         f'Неполучена ошибка на НЕкорректное сообщение.')

    def tearDown(self) -> None:
        self.test_client_started.close()
