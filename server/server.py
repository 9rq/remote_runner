import contextlib
import socket
import subprocess
import sys
import threading
from utils import *


bind_ip = socket.gethostname()
bind_port = 9999

# メッセージへの処理
def handle_client(client_socket):
    request = client_socket.recv(1024)
    print('[*] Received : {}'.format(request))
    client_socket.send(b'ACK!\n')

    with substitute_stdio(SocketIO(client_socket)):
        try:
            exec(request)
        except Exception as e:
            print('[!] Error occured', file=sys.__stdout__)
            print(e, file=sys.__stdout__)
    client_socket.close()
    print('[*] connection closed')
    print()


def main():
    sys.meta_path.append(RemoteFinder())

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print('[*] Listening on {}:{}'.format(bind_ip,bind_port))

    try:
        while 1:
            client, addr = server.accept()
            print('[*] Accepted connection from : {}:{}'.format(addr[0], addr[1]))
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()
    except KeyboardInterrupt:
        print('\r',end='')
    except Exception as e:
        print('[!] Error occured')
        print(e)
    finally:
        server.close()
        print('[*] port closed')


if __name__ == '__main__':
    main()
