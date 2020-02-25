from knight_bus.base import Base


class Receiver(Base):
    def __init__(self, key: str or bytes, port: int = 8900, auto_connect: bool = True):
        """
        init: Most functions are the same as super class
        but self.socket used to receive object self.listen_socket used to accept connection
        """
        super().__init__(key=key, port=port, ip="0.0.0.0", auto_connect=False)
        self.listen_socket, self.socket = self.socket, None
        self.listen_socket.bind(self.server_address)
        self.listen_socket.listen(3)

        if auto_connect:
            self.connect()

    def connect(self):
        """
        accept a connection

        :Note: function will block until a connection established
        :return:None
        """
        if self._is_connected:
            return
        self.socket, _ = self.listen_socket.accept()
        self._is_connected = True

    def disconnect(self):
        """
        close self.socket (used to receive object) but keep self.listen_socket (used to accept connection)
        :return: None
        """
        if not self._is_connected:
            return
        self.socket.close()
        self._is_connected = False

    def __del__(self):
        """
        destructor

        close all the socket and destruct
        """
        self.socket.close()
        self.listen_socket.close()
        del self
