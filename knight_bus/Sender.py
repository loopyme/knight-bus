from knight_bus.base import Base


class Sender(Base):
    def connect(self):
        """
        try to establish a connection with server

        :return: None
        """
        if self._is_connected:
            return
        try:
            self.socket.connect(self.server_address)
            self._is_connected = True
        except Exception as e:
            raise ConnectionError("Connect failed:{}".format(e))

    def disconnect(self):
        """
        disconnect with server

        :return: None
        """
        if not self._is_connected:
            return
        try:
            self.socket.close()
            self._is_connected = False
        except Exception as e:
            raise ConnectionError("Disconnect failed:{}".format(e))
