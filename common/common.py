import json
from sys import exit

from .decos import Log
from .settings import ENCODING, MAX_PACKAGE_LENGTH, DEFAULT_PORT, DEFAULT_IP_ADDRESS, DEFAULT_CLIENT_MODE


# class Common:
#     def get_msg(self, message):
#         """
#         Прием и декодирование сообщения
#         :param message:
#         :type message:
#         :return:
#         :rtype:
#         """
#         msg = message.recv(MAX_PACKAGE_LENGTH)  # Принять не более MAX_PACKAGE_LENGTH байтов данных
#         if isinstance(msg, bytes):
#             json_response = msg.decode(ENCODING)
#             if len(json_response) != 0:
#                 response = json.loads(json_response)
#                 if isinstance(response, dict):
#                     return response
#                 raise ValueError('Объект не является словарем')
#             else:
#                 # return
#                 raise ValueError('Пришла пустая строка')
#         raise ValueError('Пришли не байты')
#
#     def send_msg(self, socket_, message):
#         """
#         Кодирование и отправка сообщения
#         :param socket_:
#         :type socket_:
#         :param message:
#         :type message: dict
#         :return:
#         :rtype:
#         """
#         serialised_message = json.dumps(message)  # переводим в байты
#         encoded_message = serialised_message.encode(ENCODING)
#         socket_.send(encoded_message)

def get_msg(client):
    """
    Прием и декодирование сообщения
    :param client:
    :type client:
    :return:
    :rtype:
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


@Log()
def send_msg(socket_, message):
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


def port_check(port):
    # порт
    min_port, max_port = 1024, 65535
    try:
        if port < min_port or port > max_port:
            raise ValueError
    except ValueError:
        print(f'Порт должен быть в диапазоне от {min_port} до {max_port}.')
        exit(1)
    else:
        return port
