"""Программа-лаунчер"""
import random
import subprocess
import time


PROCESSES = []


def get_name(i):
    return  f'{random.getrandbits(128)}/{i}'


while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, '
                   'x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        # clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        PROCESSES.append(subprocess.Popen('gnome-terminal -- python3 server.py', shell=True))

        time.sleep(0.5)
        for i in range(2):
            # Добавил так имя так как имена 1-2-3 бывают заняты
            # name = get_name(i)
            PROCESSES.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n Test{i}', shell=True))
    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
