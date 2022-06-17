import json
import sys

sys.path.append('../')
from common.decos import Log
from common.variables import *


@Log()
def get_message(client):
    """
    Прием и декодирование сообщения
    :param client:
    :type client:
    :return:
    :rtype:
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    print(encoded_response)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


@Log()
def send_message(socket_, message):
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
