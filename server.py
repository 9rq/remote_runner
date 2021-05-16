import socket
import subprocess
import threading


bind_ip = '127.0.0.1'
bind_port = 9999

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print('[*] Received : {}'.format(request))
    client_socket.send(b'ACK!')
    client_socket.close()
    exec(request)


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
