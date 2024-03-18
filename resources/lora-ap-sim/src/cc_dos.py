import socket
import ssl
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE,SIG_DFL)


class ConnectionController:
    def __init__(self, s=None):
        if s is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(5)
        else:
            self.s = s

        self.conn = ssl.wrap_socket(self.s, ssl_version=ssl.PROTOCOL_TLSv1_2)

    def connect(self, host, port):
        try:
            self.conn.connect((host, port))
        except Exception as e:
            print("An error occurred during a connection attempt")
            print(e)

    def send_data(self, data):
        self.conn.sendall(data)

    def close(self):
        self.s.close()
        self.conn.close()
