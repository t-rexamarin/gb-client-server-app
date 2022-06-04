import socket
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject
from common.settings import *
from common.common import send_msg, get_msg
from logs import client_log_config

sys.path.append('../')

# инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger(client_log_config.LOGGER_NAME)
# объект блокировки для работы с сокетом
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    # сигнал нового сообщения
    new_message = pyqtSignal(str)
    # сигнал потери соединения
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.transport = None  # сокет для работы с сервером
        self.connection_init(ip_address, port)  # установка соединения

        # обновляем таблицы известных пользователей и контактов
        try:
            self.user_list_update()
            self.contact_list_update()
        except OSError as err:
            if err.errno:
                CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                raise ERROR('Потеряно соединение с сервером.')
            CLIENT_LOGGER.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            raise ERROR('Потеряно соединение с сервером.')
        # finally:
        self.running = True  # флаг продолжения работы

    def connection_init(self, ip_address, port):
        """
        Инициализация соединения с сервером
        :param ip_address:
        :type ip_address:
        :param port:
        :type port:
        :return:
        :rtype:
        """
        # инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # таймаут необходим для освобождения сокета
        self.transport.settimeout(5)

        # пробуем подключится, ставим True если удалось
        connected = False
        for i in range(5):
            CLIENT_LOGGER.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip_address, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            CLIENT_LOGGER.critical('Не удалось установить соединение с сервером')
            raise ERROR('Не удалось установить соединение с сервером')

        CLIENT_LOGGER.debug('Установлено соединение с сервером')

        try:
            with socket_lock:
                send_msg(self.transport, self.create_presence())
                self.process_answer(get_msg(self.transport))
        except (OSError, json.JSONDecodeError):
            CLIENT_LOGGER.critical('Потеряно соединение с сервером!')
            raise ERROR('Потеряно соединение с сервером!')
        else:
            CLIENT_LOGGER.info('Соединение с сервером успешно установлено.')

    def create_presence(self):
        """
        Генерирует сообщение-приветствие для сервера
        :return:
        :rtype:
        """
        msg = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для {self.username}')
        return msg

    def process_answer(self, message):
        """
        Обрабатывает сообщение от сервера
        :param message:
        :type message:
        :return:
        :rtype:
        """
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ERROR(f'400 : {message[ERROR]}')
            else:
                CLIENT_LOGGER.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')

        # если это сообщение от пользователя добавляем в базу, даём сигнал о новом сообщении
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and SENDER in message \
                and RECEIVER in message \
                and MESSAGE_TEXT in message \
                and message[RECEIVER] == self.username:
            CLIENT_LOGGER.debug(f'Получено сообщение от пользователя {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        CLIENT_LOGGER.debug(f'Запрос контакт листа для пользователся {self.name}')

        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        CLIENT_LOGGER.debug(f'Сформирован запрос {req}')

        with socket_lock:
            send_msg(self.transport, request)
            answer = get_msg(self.transport)
            CLIENT_LOGGER.debug(f'Получен ответ {answer}')
        if RESPONSE in answer and answer[RESPONSE] == 202:
            for contact in answer[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            CLIENT_LOGGER.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        """
        Обновляет таблицу известных пользователей
        :return:
        :rtype:
        """
        CLIENT_LOGGER.debug(f'Запрос списка известных пользователей {self.username}')

        request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }

        with socket_lock:
            send_msg(self.transport, request)
            answer = get_msg(self.transport)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            self.database.add_users(answer[LIST_INFO])
        else:
            CLIENT_LOGGER.error('Не удалось обновить список известных пользователей.')

    def add_contact(self, contact):
        """
        Сообщает серверу о добавлении нового контакта
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        CLIENT_LOGGER.debug(f'Создание контакта {contact}')

        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }

        with socket_lock:
            send_msg(self.transport, request)
            self.process_answer(get_msg(self.transport))

    def remove_contact(self, contact):
        """
        Удаление клиента на сервере
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        CLIENT_LOGGER.debug(f'Удаление контакта {contact}')

        request = {
            ACTION: EXIT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }

        with socket_lock:
            send_msg(self.transport, request)
            self.process_answer(get_msg(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }

        with socket_lock:
            try:
                send_msg(self.transport, message)
            except OSError:
                pass
        CLIENT_LOGGER.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def send_message(self, to, message):
        """
        Отправка сообщения на сервер
        :param to:
        :type to:
        :param message:
        :type message:
        :return:
        :rtype:
        """
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            RECEIVER: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            send_msg(self.transport, message_dict)
            self.process_server_ans(get_msg(self.transport))
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        CLIENT_LOGGER.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # если не сделать тут задержку, то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)

            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_msg(self.transport)
                except OSError as err:
                    if err.errno:
                        CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    CLIENT_LOGGER.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    CLIENT_LOGGER.debug(f'Принято сообщение с сервера: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)
