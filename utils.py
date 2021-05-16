import contextlib
import sys
import socket


# change output stream of print func
def alternative_print(output_stream):
    def alt_print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        print(objects,sep=sep, end=end,file=output_stream, flush=True)
    return alt_print


# substitute print func inside context manager
@contextlib.contextmanager
def substitute_print(alt_print):
    global print
    orig_print = print
    print = alt_print
    try:
        yield None
    finally:
        print = orig_print

# add write method to socket obj
class MySocket(socket.socket):
    def write(self, msg):
        self.send(msg)



def main():
    pass


if __name__ == '__main__':
    main()
