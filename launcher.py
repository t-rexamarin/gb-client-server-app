"""Лаунчер"""
import os
import signal
import subprocess
from time import sleep

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('gnome-terminal -- python3 server.py',
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        preexec_fn=os.setsid))
        sleep(1)

        while True:
            CLIENTS = input('Сколько клиентов запустить?: ')
            try:
                CLIENTS = int(CLIENTS)
            except ValueError:
                print('Укажите числом кол-во клиентов.')
            else:
                break

        for i in range(CLIENTS):
            PROCESS.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n Test{i}',
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            preexec_fn=os.setsid))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
            # VICTIM.terminate()
            # os.killpg(os.getpgid(VICTIM.pid), signal.SIGKILL)
