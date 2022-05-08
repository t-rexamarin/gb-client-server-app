"""Лаунчер"""

import subprocess
from time import sleep

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        # PROCESS.append(subprocess.Popen(['python', 'server.py'],
        #                                 creationflags=subprocess.CREATE_NEW_CONSOLE))
        # PROCESS.append(subprocess.Popen('python server.py', shell=True))
        PROCESS.append(subprocess.Popen('gnome-terminal -- python3 server.py', shell=True))
        sleep(1)
        for i in range(1):
            # PROCESS.append(subprocess.Popen(['python', 'client.py', '-m', 'listen'],
            #                                 creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen('gnome-terminal -- python3 client.py -m listen', shell=True))
            sleep(1)
        for i in range(1):
            # PROCESS.append(subprocess.Popen(['python', 'client.py', '-m', 'send'],
            #                                 creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen('gnome-terminal -- python3 client.py -m send', shell=True))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
            VICTIM.terminate()
