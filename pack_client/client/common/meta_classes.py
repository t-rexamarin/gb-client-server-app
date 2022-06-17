import dis


class ServerVerifier(type):
    """
    Метакласс для проверки соответствия сервера
    """
    def __init__(self, clsname, bases, clsdict):
        """
        :param clsname: экземпляр метакласса - Server
        :type clsname:
        :param bases: кортеж базовых классов - ()
        :type bases:
        :param clsdict: словарь атрибутов и методов экземпляра метакласса
        :type clsdict:
        """
        # необходимые данные по сокету
        socket_data = ('SOCK_STREAM', 'AF_INET')
        # Список методов, которые используются в функциях класса:
        methods = []
        # Атрибуты, используемые в функциях класса
        attrs = []

        # перебираем ключи
        for func in clsdict:
            try:
                # Возвращает итератор по инструкциям в предоставленной функции,
                # методе, строке исходного кода или объекте кода
                ret = dis.get_instructions(clsdict[func])
            except TypeError:  # если не ф-ция
                pass
            else:
                # у ф-ции разбираем код, получая методы и атрибуты
                for i in ret:
                    # opname - имя для операции
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='AF_INET',
                            # argrepr='AF_INET', offset=2, starts_line=None, is_jump_target=False)
                            # Instruction(opname='LOAD_GLOBAL', opcode=116, arg=2, argval='SOCK_STREAM',
                            # argrepr='SOCK_STREAM', offset=4, starts_line=None, is_jump_target=False)
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)

        # Если обнаружено использование недопустимого метода connect, бросаем исключение:
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        # Если сокет не инициализировался константами SOCK_STREAM(TCP) AF_INET(IPv4), тоже исключение.
        if not all([True if socket_item in methods else False for socket_item in socket_data]):
            raise TypeError('Некорректная инициализация сокета.')
        # if 'SOCK_STREAM' not in attrs and \
        #         'AF_INET' not in attrs:
        #     raise TypeError('Некорректная инициализация сокета.')
        # # Обязательно вызываем конструктор предка:
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    """
    Метакласс для проверки соответствия клиента
    """
    def __init__(self, clsname, bases, clsdict):
        # необходимые методы
        """'get_msg' - почему то не находится в клиента, хотя вызов на 106 строке"""
        required_methods = ('get_msg', 'send_msg')
        # Запрещенные методы для клиента
        restricted_methods = ('accept', 'listen', 'socket')
        # Список методов, которые используются в функциях класса:
        methods = []

        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            # Если не функция то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for i in ret:
                    # # opname - human readable name for operation
                    # if i.opname == 'LOAD_GLOBAL':
                    # argval - resolved arg value (if known), otherwise same as arg
                    if i.argval not in methods:
                        methods.append(i.argval)

        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in restricted_methods:
            if command in methods:
                raise TypeError(f'В классе обнаружено использование запрещённого метода: {command}')

        # Вызов get_message или send_message из utils считаем корректным использованием сокетов
        # если любого метода из required_methods нет в классе, то ошибка
        if any([True for required_command in required_methods if required_command in methods]):
            pass
        else:
            raise TypeError(f'Отсутствуют вызов функции, работающей с сокетами.')
        super().__init__(clsname, bases, clsdict)
