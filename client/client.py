import json
import pickle
import socket
from utils import *


target_host = socket.gethostname()
target_port = 9999


def handle_message(msg):
    if type(msg) == str:
        print(msg, end='')
    elif type(msg) == tuple:
        request, args = msg
        print(request)
        print(args)
    else:
        print('others', msg, end='')


def main():
    client = MySocket()
    try:
        client.connect((target_host, target_port))
        with open('example2.py', 'r') as f:
            data = f.read()
            client.send(data)
        while 1:
            try:
                msgs = client.recv(4096)
                if not msgs:
                    break
                for msg in msgs:
                    handle_message(msg)
            except Exception as e:
                print(e)
                break
    except:
        print('[!c] Exception! Exiting...')
    finally:
        client.close()
        print('[*c] port closed')


if __name__ == '__main__':
    main()
