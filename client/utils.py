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
