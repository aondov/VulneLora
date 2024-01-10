import socket
import ssl


class ConnectionController:
    def __init__(self, s=None):
        """
        Constructor
        :param s: ssl socket, instance of socket
        """
        if s is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(5)
        else:
            self.s = s

        self.conn = ssl.wrap_socket(self.s, ssl_version=ssl.PROTOCOL_TLSv1_2)

    def connect(self, host, port):
        """
        Connect to a remote server
        :param host: string ip address or domain name
        :param port:
        :return
        """
        try:
            self.conn.connect((host, port))
        except Exception as e:
            print("An error occurred during a connection attempt")
            print(e)

    def get_connection(self):
        """
        Returns a connection
        :return ssl socket wrapper
        """
        return self.conn

    def send_data(self, data):
        """
        Send all buffered data using ssl socket
        :param data: bytes, STIoT message in bytes
        :return reply if received, otherwise None
        """
        self.conn.sendall(data)

        try:
            reply = self.recv(1024)
            if reply is not None:
                # print("Reply:")
                # print(str(reply, 'ascii'))
                return reply
            else:
                return None
        except ssl.SSLError as s:
            print("No reply from network server")
            return None

    def close(self):
        """
        Properly close connection
        :return
        """
        self.s.close()
        self.conn.close()

    def recv(self, buffer_size=1024):
        """
        Custom socket receive method
        :param buffer_size: int, default is 1024
        :return received data
        """
        # print("Waiting for reply...")
        try:
            text = bytes()
            chunk = bytes()
            while True:
                chunk += self.conn.recv(buffer_size)
                if not chunk:
                    break
                else:
                    text += chunk
        except Exception as e:
            if text:
                return text
            else:
                return None
