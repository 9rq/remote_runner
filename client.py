import socket


target_host = socket.gethostname()
target_port = 9999


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, target_port))
    with open('example2.py', 'r') as f:
        data = f.read()
        client.send(data.encode())
    while 1:
        response = client.recv(4096)
        if not response:
            break
        print(response.decode(),end='')
    client.close()
    print('[*] port closed')


if __name__ == '__main__':
    main()
