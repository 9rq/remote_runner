import contextlib
import socket
import sys
import threading
from utils import *


bind_ip = socket.gethostname()
bind_port = 9999

# メッセージへの処理
def handle_client(client_socket):
    client_socket = MySocket(sock=client_socket)
    try:
        request = client_socket.recv(4096)
        print('[*s] Received : {}'.format(request.encode()))

        with substitute_stdio(SocketIO(client_socket)):
            try:
                with substitute_finders(sys.meta_path + [RemoteFinder(client_socket)]):
                    exec(request)
                print('[*s] Done')
                client_socket.send(('exit', None))
            except Exception as e:
                print('[!s] Error occured whlie executing remote code', file=sys.__stdout__)
                print(e, file=sys.__stdout__)
    finally:
        client_socket.close()
        print('[*s] connection closed')


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print('[*s] Listening on {}:{}'.format(bind_ip,bind_port))

    try:
        while 1:
            client, addr = server.accept()
            print('[*s] Accepted connection from : {}:{}'.format(addr[0], addr[1]))
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()
    except KeyboardInterrupt:
        print('\r',end='')
    except Exception as e:
        print('[!s] Error occured')
        print(e)
    finally:
        server.close()
        print('[*s] port closed')


if __name__ == '__main__':
    main()
