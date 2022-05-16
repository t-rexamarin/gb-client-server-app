"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с
выводом соответствующего сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
from ipaddress import ip_address
from subprocess import Popen, PIPE
from socket import getaddrinfo, gaierror


def host_ping(hosts, timeout=10, count=1):
    """
    Пингуется список хостов hosts
    :param hosts: list of hosts
    :type hosts: list
    :param timeout: stop receiving a ping output after a specific amount of time (sec)
    :type timeout: int
    :param count: automatically stop after it sends a certain number of packets
    :type count: int
    :return:
    :rtype:
    """
    # в вашем примере вы использовали строки, чтобы хранить
    # это займет меньше места, но в случае необходимости пройтись по списку
    # сделать это будет затруднительно
    # да и в целом получается обе эти реализации противоречат принципу YAGNI
    # "You aren't going to need it" - не надо добавлять то, чего не требуется
    # нам хватит простых принтов по результатом вызова команды ping
    result = {
        'hosts_available': [],
        'hosts_unavailable': [],
        'hosts_incorrect': []
    }

    for host in hosts:
        try:
            address = getaddrinfo(host, None)
        except gaierror:
            result['hosts_incorrect'].append(host)
        else:
            address = address[0][4][0]  # ip address
            address = ip_address(address)  # ipv4 or ipv4 obj
            address_protocol = address.version

            command = Popen(['ping', f'-{address_protocol}', '-c', f'{count}', f'{address}', '-w', f'{timeout}'],
                            shell=False,
                            stdout=PIPE)
            # в такой реализации получаю FileNotFoundError: [Errno 2] No such file or directory:
            # command = Popen(f'ping -c {count} {ip} -w {timeout}', shell=False, stdout=PIPE)

            # Wait for child process to terminate. Set and return returncode attribute.
            command.wait()

            if command.returncode == 0:
                print(f'{host} узел доступен')
                result['hosts_available'].append(host)
            else:
                print(f'{host} узел недоступен')
                result['hosts_unavailable'].append(host)
    return result


if __name__ == '__main__':
    hosts = ['https://yandex.ru/',
             'yandex.ru',
             'https://www.google.com/',
             '8.8.8.8',
             '127.0.0.1',
             '2001:db8::',
             '2001:4860:4860::8888']
    host_ping(hosts)
