import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, Session
from sqlalchemy.sql import default_comparator


class ServerStorage:
    """
    Серверное хранилище
    """
    class Users:
        """
        Сущность юзера
        """
        def __init__(self, username, passwd_hash):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None

    class LoginHistory:
        """
        Сущность истории входов юзера
        """
        def __init__(self, user, date_time, ip, port):
            self.id = None
            self.user = user
            self.date_time = date_time
            self.ip = ip
            self.port = port

    class ActiveUsers:
        """
        Сущность активных юзеров
        """
        def __init__(self, user_id, login_time, ip, port):
            self.id = None
            self.user = user_id
            self.ip = ip
            self.port = port
            self.login_time = login_time

    class UsersContacts:
        """
        Сущность контактов пользователей
        """
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UsersHistory:
        """
        Сущность истории действий
        """
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # по умолчанию Pysqlite запрещает использование одног соединения более чем
        # в одном потоке. check_same_thread = False убирает этот запрет
        self.db_engine = create_engine(f'sqlite:///{path}',  # server_database.db3
                                       echo=False,
                                       pool_recycle=7200,  # автореконект через 7200сек
                                       connect_args={'check_same_thread': False})
        # посредник между БД и таблицами, аналог миграций
        self.metadata = MetaData()

        # таблица пользователей
        users_table = Table(
            'Users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50), unique=True),
            Column('last_login', DateTime),
            Column('passwd_hash', String),
            Column('pubkey', Text)
        )

        # таблица истории входов
        user_login_history_table = Table(
            'Login_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id')),
            Column('date_time', DateTime),
            Column('ip', String(50)),
            Column('port', String(50))
        )

        # таблица активныйх пользователей
        active_users_table = Table(
            'Active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id'), unique=True),
            Column('ip', String(50)),
            Column('port', Integer),
            Column('login_time', DateTime)
        )
        
        # таблица контактов
        contacts_table = Table(
            'Contacts', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id')),
            Column('contact', ForeignKey('Users.id'))
        )
        
        # таблица истории пользователей
        users_history_table = Table(
            'History', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id')),
            Column('sent', Integer),
            Column('accepted', Integer)
        )

        # создание таблиц будет выполнен CREATE TABLE из меты
        self.metadata.create_all(self.db_engine)

        # связываем сущности питона с таблицами базы данных
        mapper(self.Users, users_table)
        mapper(self.LoginHistory, user_login_history_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.UsersContacts, contacts_table)
        mapper(self.UsersHistory, users_history_table)

        # создаем сессию
        # предоставляет интерфейс через который выполняются все запросы
        # которые возвращают и изменяют orm объекты
        self.session = Session(bind=self.db_engine)

        # если в таблице активных пользователей есть записи, то их необходимо удалить
        # когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port, key):
        """
        Выполняется при входе пользователя, записывает в базу факт входа
        :param username:
        :type username:
        :param ip:
        :type ip:
        :param port:
        :type port:
        :return:
        :rtype:
        """
        # print(username, ip, port)
        # запрос в таблицу пользователей на наличие там пользователя с таким именем
        result = self.session.query(self.Users).filter_by(name=username)

        # если пользователь есть, то обновляем дату последнего входа
        # и проверяем корректность ключа. Если клиент прислал новый ключ,
        # сохраняем его
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        # если нет, добавляем нового пользователя в таблицу
        else:
            raise ValueError('Пользователь не зарегистрирован.')
            # # в таблицу уходит экземпляр класса Users
            # user = self.Users(username)
            # self.session.add(user)
            # self.session.commit()  # коммитим чтобы присвоился id
            # user_in_history = self.UsersHistory(user.id)
            # self.session.add(user_in_history)  # добавляем его в историю. коммит в конце метода

        # создаем запись о новом активном юзере
        new_active_user = self.ActiveUsers(user_id=user.id,
                                           login_time=datetime.datetime.now(),
                                           ip=ip,
                                           port=port)
        self.session.add(new_active_user)

        # сохраняем данные в историю входов
        history = self.LoginHistory(user=user.id,
                                    date_time=datetime.datetime.now(),
                                    ip=ip,
                                    port=port)
        self.session.add(history)

        # сохраняем изменения в ActiveUsers и UsersHistory
        self.session.commit()

    def user_logout(self, username):
        """
        Фиксация отключения пользователя
        :param username:
        :type username:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=username).first()
        # удаляем юзера из активных
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        """
        Фиксирует передачу сообщения и делает соответствующую пометки в таблице истории пользователей
        :param sender:
        :type sender:
        :param recipient:
        :type recipient:
        :return:
        :rtype:
        """
        # берем id отправителя и получателя
        sender = self.session.query(self.Users).filter_by(name=sender).first().id
        recipient = self.session.query(self.Users).filter_by(name=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def add_contact(self, user, contact):
        """
        Добавляет контакт для пользователя
        :param user:
        :type user:
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=user).first()
        contact = self.session.query(self.Users).filter_by(name=contact).first()
        contact_exists = self.session.query(self.UsersContacts).filter_by(user=user.id,
                                                                          contact=contact.id).count()

        # если второго пользователя нет, или такой контакт уже существует
        if not contact or contact_exists:
            return

        # создаем контакт и сохраняем
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        """
        Удаляет контакт из БД
        :param user:
        :type user:
        :param contact:
        :type contact:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=user).first()
        contact = self.session.query(self.Users).filter_by(name=contact).first()

        # если второго пользователя нет
        if not contact:
            return

        # удаляем контакт
        print(self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    def add_user(self, name, passwd_hash):
        """
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        :param name:
        :type name:
        :param passwd_hash:
        :type passwd_hash:
        :return:
        :rtype:
        """
        user_row = self.Users(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        """
        Метод удаляющий пользователя из базы
        :param name:
        :type name:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.Users).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        """
        Метод получения хэша пароля пользователя
        :param name:
        :type name:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        """
        Метод получения публичного ключа пользователя
        :param name:
        :type name:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        """
        Метод проверяющий существование пользователя
        :param name:
        :type name:
        :return:
        :rtype:
        """
        if self.session.query(self.Users).filter_by(name=name).count():
            return True
        else:
            return False

    def users_list(self):
        """
        Возвращает список известных пользователей со временем последнего входа
        :return:
        :rtype:
        """
        query = self.session.query(
            self.Users.name,
            self.Users.last_login
        )
        # вернется список кортежей
        return query.all()

    def get_contacts(self, username):
        """
        Возвращает список контактов пользователя
        :param username:
        :type username:
        :return:
        :rtype:
        """
        user = self.session.query(self.Users).filter_by(name=username).first()
        # запрашиваем список контактов
        query = self.session.query(self.UsersContacts, self.Users.name).\
            filter_by(user=user.id).join(self.Users, self.UsersContacts.contact == self.Users.id)
        result = [contact[1] for contact in query.all()]
        return result

    def active_users_list(self):
        """
        Возвращает список активных пользователей
        :return:
        :rtype:
        """
        query = self.session.query(
            self.Users.name,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.Users)
        return query.all()

    def login_history(self, username=None):
        """
        Возвращает историю входов по пользователю или всем пользователям
        :param username:
        :type username:
        :return:
        :rtype:
        """
        query = self.session.query(self.Users.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port).join(self.Users)
        # если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.Users.name == username)
        return query.all()

    def message_history(self):
        """
        Возвращает кол-во переданных и полученных сообщений
        :return:
        :rtype:
        """
        query = self.session.query(
            self.Users.name,
            self.Users.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.Users)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('client_1', '192.168.1.4', 8888)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    # print('Активные юзеры\n')
    # print(test_db.active_users_list())
    # test_db.user_logout('client_1')
    # print(test_db.active_users_list())
    # test_db.login_history('client_1')
    # print(test_db.users_list())
    print(test_db.users_list())
    test_db.process_message('client_1', 'client_2')
    print(test_db.message_history())