import datetime
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import mapper, Session
from sqlalchemy.sql import default_comparator


class ClientDatabase:
    class KnownUsers:
        """Отображение таблицы известных пользователей"""
        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageHistory:
        """Отображение таблицы истории сообщений"""
        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        """Отображение списка контактов"""
        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):
        """
        Создаём движок базы данных, поскольку разрешено несколько клиентов одновременно,
        каждый должен иметь свою БД.
        Поскольку клиент мультипоточный необходимо отключить проверки на подключения с
        разных потоков, иначе sqlite3.ProgrammingError
        """
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.db3'
        self.database_engine = create_engine(f'sqlite:///{os.path.join(path, filename)}',
                                             echo=False,
                                             pool_recycle=7200,
                                             connect_args={'check_same_thread': False})
        # метадата для таблиц
        self.metadata = MetaData()

        # таблица известных пользователей
        users_table = Table('known_users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String))

        # таблица истории сообщений
        history_table = Table('messages_history', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('contact', String),
                              Column('direction', String),
                              Column('message', Text),
                              Column('date', DateTime))

        # таблица контактов
        contacts_table = Table('contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('name', String, unique=True))

        # создаем таблицы
        self.metadata.create_all(self.database_engine)

        # связываем сущности питона с таблицами базы данных
        mapper(self.KnownUsers, users_table)
        mapper(self.MessageHistory, history_table)
        mapper(self.Contacts, contacts_table)

        # создаем сессию
        # предоставляет интерфейс через который выполняются все запросы
        # которые возвращают и изменяют orm объекты
        self.session = Session(bind=self.database_engine)

        # очищаем таблицу контактов, т.к. при запуске они подгружаются с сервера
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """
        Добавление контакта
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        contact_exists = self.session.query(self.Contacts).filter_by(name=contact).count()
        if not contact_exists:
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        """
        Метод очищающий таблицу со списком контактов
        :return:
        :rtype:
        """
        self.session.query(self.Contacts).delete()

    def del_contact(self, contact):
        """
        Удаление контакта
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def add_users(self, users_list):
        """
        Добавление известных пользователей
        :param users_list:
        :type users_list:
        :return:
        :rtype:
        """
        # пользователей получаем только с сервера, поэтому чистим таблицу
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """
        Сохранение сообщения
        :param contact:
        :type contact:
        :param direction:
        :type direction:
        :param message:
        :type message:
        :return:
        :rtype:
        """
        message_row = self.MessageHistory(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """
        Получение контактов
        :return:
        :rtype:
        """
        contacts = [contact[0] for contact in self.session.query(self.Contacts.name).all()]
        return contacts

    def get_users(self):
        """
        Получение списка известных пользователей
        :return:
        :rtype:
        """
        users = [user[0] for user in self.session.query(self.KnownUsers.username).all()]
        return users

    def check_user(self, user):
        """
        Проверяет наличие пользователя в известных
        :param user:
        :type user:
        :return:
        :rtype:
        """
        user_exists = self.session.query(self.KnownUsers).filter_by(username=user).count()
        if user_exists:
            return True
        else:
            return False

    def check_contact(self, contact):
        """
        Проверяет наличие пользователя в контактах
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        contact_exists = self.session.query(self.Contacts).filter_by(name=contact).count()
        if contact_exists:
            return True
        else:
            return False

    def get_history(self, contact):
        """
        Возвращает историю переписки
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        query = self.session.query(self.MessageHistory).filter_by(contact=contact)
        result = [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                  for history_row in query.all()]
        return result


if __name__ == '__main__':
    test_db = ClientDatabase('test1')
    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message('test1', 'test2', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('test2', 'test1', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(test_db.get_history('test2'))
    print(test_db.get_history(to_who='test2'))
    print(test_db.get_history('test3'))
    test_db.delete_contact('test4')
    print(test_db.get_contacts())
