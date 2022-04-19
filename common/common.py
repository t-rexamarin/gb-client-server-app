import json
from sys import exit
from .settings import ENCODING, MAX_PACKAGE_LENGTH, DEFAULT_PORT, DEFAULT_IP_ADDRESS


class Common:
    def get_msg(self, message):
        """
        Прием и декодирование сообщения
        :param message:
        :type message:
        :return:
        :rtype:
        """
        msg = message.recv(MAX_PACKAGE_LENGTH)  # Принять не более MAX_PACKAGE_LENGTH байтов данных
        if isinstance(msg, bytes):
            json_response = msg.decode(ENCODING)
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError('Объект не является словарем')
        raise ValueError('Пришли не байты')

    def send_msg(self, socket_, message):
        """
        Кодирование и отправка сообщения
        :param socket_:
        :type socket_:
        :param message:
        :type message: dict
        :return:
        :rtype:
        """
        serialised_message = json.dumps(message)  # переводим в байты
        encoded_message = serialised_message.encode(ENCODING)
        socket_.send(encoded_message)


def port_check(args):
    # порт
    min_port, max_port = 1024, 65535
    try:
        if '-p' in args:
            listen_port = int(args[args.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT

        if listen_port < min_port or listen_port > max_port:
            raise ValueError
    except IndexError:
        print('После параметра "-p" необходимо указать номер порта, на котором будет запущен сервер.')
        # есть у меня сомнения, что неправильно вызывать выход из скрипта в какой то другой функции
        exit(1)
    except ValueError:
        print(f'Порт должен быть в диапазоне от {min_port} до {max_port}.')
        exit(1)
    else:
        return listen_port


def address_check(args):
    # адрес
    try:
        if '-a' in args:
            listen_address = args[args.index('-a') + 1]
        else:
            listen_address = DEFAULT_IP_ADDRESS
    except IndexError:
        print('После параметра "-a" обходимо указать адрес, который будет слушать сервер')
        exit(1)
    else:
        return listen_address
