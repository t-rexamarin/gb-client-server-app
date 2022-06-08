import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QTableView, QDialog, QPushButton, QLineEdit, \
    QFileDialog, QApplication


def gui_create_model(database):
    """
    Создание таблицы QModel для отображения в окне программы
    :param database:
    :type database:
    :return:
    :rtype:
    """
    list_users = database.active_users_list()  # список активных пользователей
    list_ = QStandardItemModel()  # ???
    list_.setHorizontalHeaderLabels(['Имя клиента',
                                     'IP Адрес',
                                     'Порт',
                                     'Время подключения'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)  # создаем элемент
        user.setEditable(False)

        ip = QStandardItem(ip)
        ip.setEditable(False)

        port = QStandardItem(str(port))
        port.setEditable(False)

        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)

        list_.appendRow([user, ip, port, time])
    return list_


def create_stat_model(database):
    """
    Реализует заполнение таблицы историей сообщений
    :param database:
    :type database:
    :return:
    :rtype:
    """
    hist_list = database.message_history()  # список сообщений из базы
    list_ = QStandardItemModel()
    list_.setHorizontalHeaderLabels(['Имя Клиента',
                                    'Последний раз входил',
                                    'Сообщений отправлено',
                                    'Сообщений получено'])
    for row in hist_list:
        user, last_seen, sent, recvd = row
        user = QStandardItem(user)
        user.setEditable(False)

        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)

        sent = QStandardItem(str(sent))
        sent.setEditable(False)

        recvd = QStandardItem(str(recvd))
        recvd.setEditable(False)

        list_.appendRow([user, last_seen, sent, recvd])
    return list_


class MainWindow(QMainWindow):
    """
    Класс основного окна
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # кнопка выхода
        self.exit_action = QAction('Выход', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(qApp.quit)

        # кнопка обновления списка клиентов
        self.refresh_btn = QAction('Обновить список', self)

        # кнопка вывода истории сообщений
        self.show_history_btn = QAction('История клиентов', self)

        # кнопка настроек сервера
        self.config_btn = QAction('Настройки клиентов', self)

        # статус бар
        self.statusBar()

        # тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exit_action)
        self.toolbar.addAction(self.refresh_btn)
        self.toolbar.addAction(self.show_history_btn)
        self.toolbar.addAction(self.config_btn)

        # настройка геометрии окна
        self.setFixedSize(800, 600)
        self.setWindowTitle('Roma\'s Messaging Server')

        self.label = QLabel('Список подключенных клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 30)

        # окно со списком подключенных клиентов
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        # отображаем окно
        self.show()


class HistoryWindow(QDialog):
    """
    Окно с историей пользователей
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # настройка окна
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # кнопка закрытия
        self.close_btn = QPushButton('Закрыть', self)
        self.close_btn.move(250, 650)
        self.close_btn.clicked.connect(self.close)

        # лист и сторией
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()


class ConfigWindow(QDialog):
    """
    Класс окна настроек
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # настройка окна
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        # надпись о файле бд
        self.db_path_label = QLabel('Пусть до файла базы данных:', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # строка с путем базы
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        # кнопка выбора пути
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        def open_file_dialog():
            """
            бработчик открытия окна выбора папки
            :return:
            :rtype:
            """
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        # метка с именем поля файла базы данных
        self.db_file_label = QLabel('Имя файла базы данных:', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        # поле для ввода имени файла
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)

        # лейбл номера порта
        self.port_label = QLabel('Номера порта для соединения:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        # поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # лейбл для ip
        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        # лейбл напоминания о пустом поле
        self.ip_label_note = QLabel('Оставьте это поле пустым, чтобы принимать сообщения с любых адресов', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        # поле для ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        # кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 220)

        # кнопка закрытия окна
        self.close_btn = QPushButton('Закрыть', self)
        self.close_btn.move(275, 220)
        self.close_btn.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.statusBar().showMessage('Test Status Bar message')
    test_list = QStandardItemModel(ex)
    test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    test_list.appendRow([QStandardItem('1'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow([QStandardItem('4'), QStandardItem('5'), QStandardItem('6')])
    ex.active_clients_table.setModel(test_list)
    ex.active_clients_table.resizeColumnToContents(3)
    print('QQQQQQ')
    app.exec_()
    print('END')