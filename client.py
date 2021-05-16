import socket


target_host = '127.0.0.1'
target_port = 9999


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, target_port))
    with open('example.py', 'r') as f:
        data = f.read()
        client.send(data.encode())
    response = client.recv(4096).decode()

    print(response)

if __name__ == '__main__':
    main()
