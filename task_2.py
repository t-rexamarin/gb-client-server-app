"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
from ipaddress import ip_address
from task_1 import host_ping


class RangeTooLargeError(Exception):
    """Выстреливает если значение последнего октета больше 254"""
    pass


def host_range_ping():
    while True:
        ip = input('Введите IP адрес: ')

        try:
            ip_format = ip_address(ip)
            last_octet = int(ip.split('.')[3])
        except ValueError:
            print('IP адрес некорректен.')
        except Exception as e:
            print(f'Произошла необработанная ошибка: {e}')
        else:
            break

    while True:
        ip_range = input('Сколько адресов проверить?: ')

        try:
            ip_range = int(ip_range)
            # 254, т.к. 255 зарезервировано и не используется
            if last_octet + ip_range > 254:
                raise RangeTooLargeError
        except ValueError:
            print('Необходимо ввести число')
        except RangeTooLargeError:
            print('Значение последнего октета не может быть больше 244. '
                  f'Максимальное кол-во адресов для проверки {254 - last_octet}.')
        except Exception as e:
            print(f'Произошла необработанная ошибка: {e}')
        else:
            break

    hosts_list = [str(ip_format + i) for i in range(ip_range)]
    return host_ping(hosts_list)


if __name__ == '__main__':
    host_range_ping()
