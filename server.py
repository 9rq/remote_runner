import contextlib
import socket
import subprocess
import threading


bind_ip = '127.0.0.1'
bind_port = 9999


@contextlib.contextmanager
def send_to_local(client_socket):
    global print
    orig_print = print
    print = client_socket.send(x.encode())
    try:
        yield None
    finally:
        print = orig_print



# メッセージへの処理
def handle_client(client_socket):
    request = client_socket.recv(1024)
    print('[*] Received : {}'.format(request))
    client_socket.send(b'ACK!')

    # printのすり替え
    @contextlib.contextmanager
    def send_to_local():
        global print
        orig_print = print
        print = lambda x: client_socket.send(x.encode())
        try:
            yield None
        finally:
            print = orig_print

    with send_to_local():
        exec(request)
    client_socket.close()
    print('[*] connection closed')


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print('[*] Listening on {}:{}'.format(bind_ip,bind_port))

    while 1:
        client, addr = server.accept()
        print('[*] Accepted connection from : {}:{}'.format(addr[0], addr[1]))
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


if __name__ == '__main__':
    main()
