import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapper, Session


class ServerStorage:
    # сущность юзера
    class Users:
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

    # сущность истории юзера
    class UsersHistory:
        def __init__(self, user, date_time, ip, port):
            self.id = None
            self.user = user
            self.date_time = date_time
            self.ip = ip
            self.port = port

    # сущность активных юзеров
    class ActiveUsers:
        def __init__(self, user_id, login_time, ip, port):
            self.id = None
            self.user = user_id
            self.ip = ip
            self.port = port
            self.login_time = login_time

    def __init__(self):
        self.db_engine = create_engine('sqlite:///server_database.db3', echo=False)
        # посредник между БД и таблицами, аналог миграций
        self.metadata = MetaData()

        # таблица пользователей
        users_table = Table(
            'Users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50), unique=True),
            Column('last_login', DateTime)
        )

        users_history_table = Table(
            'Users_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id')),
            Column('date_time', DateTime),
            Column('ip', String(50)),
            Column('port', String(50))
        )

        active_users_table = Table(
            'Active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id'), unique=True),
            Column('ip', String(50)),
            Column('port', Integer),
            Column('login_time', DateTime)
        )

        # создание таблиц будет выполнен CREATE TABLE из меты
        self.metadata.create_all(self.db_engine)

        # связываем сущности питона с таблицами базы данных
        mapper(self.Users, users_table)
        mapper(self.UsersHistory, users_history_table)
        mapper(self.ActiveUsers, active_users_table)

        # создаем сессию
        # предоставляет интерфейс через который выполняются все запросы
        # которые возвращают и изменяют orm объекты
        self.session = Session(bind=self.db_engine)

        # если в таблице активных пользователей есть записи, то их необходимо удалить
        # когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port):
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
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
        # если нет, добавляем нового пользователя в таблицу
        else:
            # в таблицу уходит экземпляр класса Users
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()

        # создаем запись о новом активном юзере
        new_active_user = self.ActiveUsers(user_id=user.id,
                                           login_time=datetime.datetime.now(),
                                           ip=ip,
                                           port=port)
        self.session.add(new_active_user)

        # сохраняем данные в историю входов
        history = self.UsersHistory(user=user.id,
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
                                   self.UsersHistory.date_time,
                                   self.UsersHistory.ip,
                                   self.UsersHistory.port).join(self.Users)
        # если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.Users.name == username)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('client_1', '192.168.1.4', 8888)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    print('Активные юзеры\n')
    print(test_db.active_users_list())
    test_db.user_logout('client_1')
    print(test_db.active_users_list())
    test_db.login_history('client_1')
    print(test_db.users_list())