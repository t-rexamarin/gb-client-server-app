"""
3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате (использовать модуль tabulate).
Таблица должна состоять из двух колонок и выглядеть примерно так:
Reachable
10.0.0.1
10.0.0.2

Unreachable
10.0.0.3
10.0.0.4
"""
from task_2 import host_range_ping
from tabulate import tabulate


def host_range_ping_tab():
    ping_result = host_range_ping()
    tab = tabulate(ping_result,
                   headers='keys',
                   tablefmt='grid',
                   stralign='center')
    return tab


if __name__ == '__main__':
    host_range_ping_tab()
