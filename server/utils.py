import contextlib
import importlib
import io
import os
import pickle
import socket
import sys
import time


class MySocket:
    def __init__(self, sock=None):
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, target):
        self.sock.connect(target)

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


# implement write function coz print calls IO.write
class SocketIO:
    def __init__(self,sock):
        self.sock = sock

    def write(self,msg):
        self.sock.send(msg)


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


# load module from code:str
class StringLoader:
    def __init__(self, code):
        self.code = code

    def create_module(self, spec):
        return None

    def exec_module(self, module, package=None):
        print(module)
        code_object = compile(self.code, '<string>', 'exec', dont_inherit=True)
        exec(code_object, module.__dict__)

    def module_from_spec(self, spec):
        print('module_from_spec called')

class RemoteFinder:
    def __init__(self, sock):
        self.sock = sock

    def find_spec(self, fullname, path, target=None):
        print('[*s] Attempting to retrive {}'.format(fullname))
        args = {'fullname':fullname, 'path':path, 'target':target}
        msg = ('import', args)
        self.sock.send(msg)
        # expand here
        return None

class MyPathFinder:
    @classmethod
    def path_hooks(cls, path):
        for hook in sys.path_hooks:
            try:
                return hook(path)
            except ImportError:
                continue
        else:
            return None

    @classmethod
    def path_importer_cache(cls, path):
        if path == '':
            path = os.getcwd()

        try:
            finder = sys.path_importer_cache[path]
        except KeyError:
            finder = cls.path_hooks(path)

        return finder

    @classmethod
    def get_spec(cls, fullname, path, target=None):
        namespace_path = []

        for entry in path:
            if not isinstance(entry, (str, bytes)):
                continue
            finder = cls.path_importer_cache(entry)
            if finder is not None:
                spec = finder.find_spec(fullname, target)
                if spec is None:
                    continue
                if spec.loader is not None:
                    return spec
                portions = spec.submodule_search_locations
                if portions is None:
                    raise ImportError('spec missing loader')
                # This is possibly part of a namespace package.
                #  Remember these path entries (if any) for when we
                #  create a namespace package, and continue iterating
                #  on path.
                namespace_path.extend(portions)
        else:
            spec = importlib.machinery.ModuleSpec(fullname, None)
            spec.submodule_search_locations = namespace_path
            return spec

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        if path is None:
            path = sys.path
        spec = cls.get_spec(fullname, path, target)
        if spec.loader is None:
            return None
        return spec



def main():
    pass


if __name__ == '__main__':
    main()
