"""Лаунчер"""
import os
import subprocess


process = []

while True:
    action = input('Выберите действие: '
                   'q - выход, '
                   's - запустить сервер, '
                   'c - запустить ктиенты, '
                   'x - закрыть все окна: ')

    if action == 'q':
        break
    elif action == 's':
        process.append(subprocess.Popen('gnome-terminal -- python3 server.py',
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        preexec_fn=os.setsid))
    elif action == 'c':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        for i in range(clients_count):
            process.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n test{i + 1} -p 123456',
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            preexec_fn=os.setsid))
    elif action == 'x':
        while process:
            process.pop().kill()
            #  process.pop().terminate()
            # os.killpg(os.getpgid( process.pop().pid), signal.SIGKILL)
