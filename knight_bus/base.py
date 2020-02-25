import socket
from abc import abstractmethod

from loopyCryptor import Cryptor


class Base:
    _buffer_size = 2048

    def __init__(
            self,
            key: str or bytes,
            ip: str = "127.0.0.1",
            port: int = 8900,
            auto_connect: bool = True,
    ):
        self.server_address = (str(ip), int(port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        Cryptor.set_default_RSA_key(public_key=key, private_key=key)
        self._is_connected = None
        self._salt = Cryptor.generate_AES_key()

        if auto_connect:
            self.connect()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    def _send_bytes(self, bytes_: bytes):
        self.connect()
        try:
            self.socket.send(bytes_)
        except Exception as e:
            raise ConnectionError("Send bytes failed:{}".format(e))

    def _recv_bytes(self, size=2048):
        self.connect()
        try:
            bytes_ = self.socket.recv(size)
        except Exception as e:
            raise ConnectionError("Recv bytes failed:{}".format(e))
        return bytes_

    def _send_object_header(self, size, md5):
        try:

            self._send_bytes(
                Cryptor.RSA_encrypt(["LOOPY 1029384756", self._salt, size, md5])
            )
            if not Cryptor.RSA_verify(
                    ["LOOPY 1029384756", Cryptor.md5(self._salt), size, md5],
                    self._recv_bytes(),
            ):
                raise ConnectionError("ACK not matched")
        except Exception as e:
            raise ConnectionAbortedError(
                "FAILED: Connection is unsecured and terminated : {}".format(e)
            )

    def _recv_object_header(self):
        try:
            code, salt, size, md5 = Cryptor.RSA_decrypt(self._recv_bytes())
            if code != "LOOPY 1029384756":
                raise ConnectionError("Code not matched")
            self._send_bytes(Cryptor.RSA_sign([code, Cryptor.md5(salt), size, md5]))
        except Exception as e:
            raise ConnectionAbortedError(
                "FAILED: Connection is unsecured and terminated : {}".format(e)
            )
        return size, md5

    def recv(self):
        size, md5 = self._recv_object_header()
        try:
            bytes_ = b""
            while size > 0:
                buffer = self._recv_bytes(
                    self._buffer_size if size > self._buffer_size else size
                )
                size -= len(buffer)
                bytes_ += buffer
                if not buffer:
                    break
            if md5 != Cryptor.md5(bytes_):
                raise ConnectionError("Object md5 unmatched")
            obj = Cryptor.RSA_decrypt(bytes_)
        except Exception as e:
            raise ConnectionAbortedError(
                "FAILED: Receiving object failed : {}".format(e)
            )
        return obj

    def send(self, obj):
        data = Cryptor.RSA_encrypt(obj)
        self._send_object_header(size=len(data), md5=Cryptor.md5(data))
        self._send_bytes(data)

    def __del__(self):
        self.socket.close()
        del self
