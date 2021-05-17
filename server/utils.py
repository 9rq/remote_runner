import contextlib
import importlib
import io
import os
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


# load module from code:str
class StringLoader:
    def __init__(self, code):
        self.code = code

    def create_module(self, spec):
        return None

    def exec_module(self, module, package=None):
        code_object = compile(self.code, '<string>', 'exec', dont_inherit=True)
        exec(code_object, module.__dict__)

class RemoteFinder:
    def __init__(self):
        self.current_module_code = ''

    def find_spec(self, fullname, path, target=None):
        print('[*] Attempting to retrive {}'.format(fullname))
        new_library ='def hello():print("hello world!")'

        if new_library is not None:
            self.current_module_code = new_library
            return importlib.machinery.ModuleSpec(fullname, StringLoader(self.current_module_code))
        return None


def main():
    pass


if __name__ == '__main__':
    main()
