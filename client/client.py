import json
import pickle
import socket
import importlib
from utils import *
import pdb


target_host = socket.gethostname()
target_port = 9999


def handle_message(msg):
    if type(msg) == tuple:
        request, args = msg
        if request == 'print':
            print(args,end='')
        elif request == 'import':
            args = find_spec_and_source(**args)
            return ('spec_and_source', args)
        elif request == 'exit':
            exit(0)
        else:
            print(request, args)

    else:
        print('others', msg, end='')


def find_spec_and_source(fullname=None, path=None, target=None):
    source = None
    spec = importlib.machinery.PathFinder().find_spec(fullname, path, target)
    try:
        with open(spec.origin,'r') as f:
            source = f.read()
    finally:
        return {'spec':spec, 'source':source}

def main():
    client = MySocket()

    try:
        client.connect((target_host, target_port))
        with open('example2.py', 'r') as f:
            data = f.read()
            client.send(data)
        while 1:
            try:
                msg = client.recv(4096)
                if not msg:
                    break
                reply = handle_message(msg)
                if reply is not None:
                    client.send(reply)
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
