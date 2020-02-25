from knight_bus.base import Base


class Sender(Base):
    def connect(self):
        if self._is_connected:
            return
        try:
            self.socket.connect(self.server_address)
            self._is_connected = True
        except Exception as e:
            raise ConnectionError("Connect failed:{}".format(e))

    def disconnect(self):
        if not self._is_connected:
            return
        try:
            self.socket.close()
            self._is_connected = False
        except Exception as e:
            raise ConnectionError("Disconnect failed:{}".format(e))
