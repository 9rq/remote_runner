import contextlib
import importlib
import io
import os
import pickle
import socket
import sys


class MySocket:
    def __init__(self, sock=None):
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buff = b''

    def connect(self, target):
        self.sock.connect(target)

    def send(self, msg:object, sep:str='\r\n'):
        totalsent = 0
        msg = pickle.dumps(msg)
        msg += sep.encode()
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('[!s] socket connection broken')
            totalsent += sent

    def recv(self, buff_size, sep:str='\r\n'):
        while 1:
            buff_split = self.buff.split(sep=sep.encode(), maxsplit=1)
            if len(buff_split) == 2:
                break
            data = self.sock.recv(buff_size)
            if not data:
                raise RuntimeError('[!s] socket connection broken')
            self.buff += data
        msg, self.buff = buff_split
        return pickle.loads(msg)

    def close(self):
        self.sock.close()


# implement write function coz print calls IO.write
class SocketIO:
    def __init__(self,sock):
        self.sock = sock

    def write(self,msg):
        self.sock.send(('print', msg))


# substitute stdio inside context-manager
@contextlib.contextmanager
def substitute_stdio(alt_io):
    sys.stdout = alt_io
    try:
        yield
    finally:
        sys.stdout = sys.__stdout__

@contextlib.contextmanager
def substitute_finders(alt_finders):
    orig_finders = sys.meta_path
    sys.meta_path = alt_finders

    try:
        yield
    finally:
        sys.meta_path = orig_finders


class StringLoader:
    '''
    Load module from code:str
    '''
    def __init__(self, code):
        self.code = code

    def create_module(self, spec):
        return None

    def exec_module(self, module, package=None):
        code_object = compile(self.code, '<string>', 'exec', dont_inherit=True)
        exec(code_object, module.__dict__)

    def module_from_spec(self, spec):
        print('module_from_spec called')


class RemoteFinder:
    '''
    Original finder.
    Try to find modules from remote client.
    To apply, you need to add this finder to sys.meta_path(not replace all)
    '''
    def __init__(self, sock):
        self.sock = sock

    def find_spec(self, fullname, path, target=None):
        print('[*s] Attempting to retrive {}'.format(fullname),file=sys.__stdout__)
        args = {'fullname':fullname, 'path':path, 'target':target}
        msg = ('import', args)
        self.sock.send(msg)
        msg = self.sock.recv(4096)
        if msg is None:
            return None
        request, args = msg
        if request == 'spec_and_source':
            print('[*s] Recieved spec and source')
            spec = args['spec']
            source = args['source']
            spec.loader = StringLoader(source)
        return spec


class MyFinder:
    @classmethod
    def find_spec(cls, fullname, path, target=None):
        print('[*] Finding {}'.format(fullname))
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec is None:
            return None
        print('[*] Found spec',spec)
        try:
            with open(spec.origin,'r')as f:
                source = f.read()
        except Exception as e:
            print(e)
        spec.loader = StringLoader(source)
        return spec


def main():
    pass


if __name__ == '__main__':
    main()
