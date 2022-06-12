class Port:
    """
    Класс - дескриптор для номера порта.
    Позволяет использовать только порты с 1023 по 65536.
    При попытке установить неподходящий номер порта генерирует исключение.
    """
    def __set_name__(self, owner, name):
        # owner - <class '__main__.Server'>
        # name - port
        self.name = name

    def __set__(self, instance, value):
        min_port, max_port = 1024, 65535
        value = int(value)
        if not min_port < value < max_port:
            raise TypeError(f'Порт должен быть в диапазоне от {min_port} до {max_port}.')
        # setattr(instance, self.name, value)  # RecursionError
        instance.__dict__[self.name] = value
