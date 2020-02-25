from knight_bus.base import Base


class Receiver(Base):
    def __init__(self, key: str or bytes, port: int = 8900, auto_connect: bool = True):
        super().__init__(key=key, port=port, ip="0.0.0.0", auto_connect=False)
        self.listen_socket, self.socket = self.socket, None
        self.listen_socket.bind(self.server_address)
        self.listen_socket.listen(3)

        if auto_connect:
            self.connect()

    def connect(self):
        if self._is_connected:
            return
        self.socket, _ = self.listen_socket.accept()
        self._is_connected = True

    def disconnect(self):
        if not self._is_connected:
            return
        self.socket.close()
        self._is_connected = False

    def __del__(self):
        self.socket.close()
        self.listen_socket.close()
        del self
