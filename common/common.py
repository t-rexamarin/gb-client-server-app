#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from socket import socket
from .settings import ENCODING, MAX_PACKAGE_LENGTH


class Common:
    def socket_init(self, domain, soc_type):
        """
        Инициация сокета
        :param domain:
        :type domain:
        :param soc_type:
        :type soc_type:
        :return:
        :rtype:
        """
        """
        AF_INET (Internet протоколы)
        SOCK_STREAM Этот тип обеспечивает последовательный, надежный, ориентированный 
        на установление двусторонней связи поток байтов
        """
        return socket(domain, soc_type)

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
        :type message: list
        :return:
        :rtype:
        """
        serialised_message = json.dumps(message)  # переводим в байты
        encoded_message = serialised_message.encode(ENCODING)
        socket_.send(encoded_message)

    def close(self, socket_):
        return socket_.close()