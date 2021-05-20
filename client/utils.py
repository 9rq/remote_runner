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

    def connect(self, target):
        self.sock.connect(target)

    def send(self, msg:object, sep:str='\r\n'):
        totalsent = 0
        msg = pickle.dumps(msg)
        msg += sep.encode()
        print(msg)
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('[!] socket connection broken')
            totalsent += sent

    def recv(self, buff_size, sep:str='\r\n'):
        buff = b''
        recv_len = 1
        while recv_len:
            data = self.sock.recv(buff_size)
            recv_len = len(data)
            buff += data
            if recv_len < buff_size:
                break
        if len(buff) == 0:
            return None
        msgs = buff.rstrip(sep.encode()).split(sep.encode())
        msgs = [pickle.loads(msg) for msg in msgs]
        return msgs

    def close(self):
        self.sock.close()
