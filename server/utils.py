import copy
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

    #orig_modules = sys.modules
    #sys.modules = copy.deepcopy(sys.modules)
    try:
        yield
    finally:
        sys.meta_path = orig_finders
        #sys.modules = orig_modules


# load module from code:str
class StringLoader:
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
    def __init__(self, sock):
        self.sock = sock

    def find_spec(self, fullname, path, target=None):
        print('[*s] Attempting to retrive {}'.format(fullname))
        args = {'fullname':fullname, 'path':path, 'target':target}
        msg = ('import', args)
        self.sock.send(msg)
        # expand here
        print('[*s] Waiting for info...')
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
