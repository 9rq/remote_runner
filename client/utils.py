import contextlib
import socket
import sys
import pickle


@contextlib.contextmanager
def substitute_Finder(alt_finders):
    orig_finders = sys.meta_path
    sys.meta_path = alt_finders
    try:
        yield
    finally:
        sys.meta_path = orig_finders


class MySocket:
    def __init__(self, sock=None):
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buff = b''

    def connect(self, target):
        self.sock.connect(target)

    def close(self):
        self.sock.close()

    def send(self, msg:object, sep:str='\r\n'):
        totalsent = 0
        msg = pickle.dumps(msg)
        msg += sep.encode()
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('[!] socket connection broken')
            totalsent += sent

    def recv(self, buff_size, sep:str='\r\n'):
        while 1:
            buff_split = self.buff.split(sep.encode(), 1)
            if len(buff_split) > 1:
                break
            data = self.sock.recv(buff_size)
            if not data:
                raise RuntimeError('[!c] socket connection broken')
            self.buff += data
        msg, self.buff = buff_split
        return pickle.loads(msg)
