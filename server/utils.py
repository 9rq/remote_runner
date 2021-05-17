import contextlib
import importlib
import io
import socket
import sys


# implement write function coz print calls IO.write
class SocketIO:
    def __init__(self,sock):
        self.sock = sock

    def write(self,msg):
        self.sock.send(msg.encode())


# substitute stdio inside context-manager
@contextlib.contextmanager
def substitute_stdio(alt_io):
    sys.stdout = alt_io
    try:
        yield
    finally:
        sys.stdout = sys.__stdout__


class RemoteImporter:
    def __init__(self):
        self.current_module_code = ''

    def find_spec(self, fullname, path, target=None):
        print('[*] Attempting to retrive {}'.format(fullname))
        self.fullname = fullname
        new_library ='def hello():print("hello world!)'

        if new_library is not None:
            self.current_module_code = new_library
            return importlib.machinery.ModuleSpec(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module, package=None):
        try:
            exec(self.current_module_code, module.__dict__)
        except Exception as e:
            raise ImportError('cannot import name {}'.format(self.fullname))


def main():
    pass


if __name__ == '__main__':
    main()
