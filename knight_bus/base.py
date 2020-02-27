import socket
from abc import abstractmethod

from loopyCryptor import Cryptor, Serializer


class Base:
    def __init__(
            self,
            encrypt_method: str = "rsa",
            key: str or bytes = None,
            ip: str = "127.0.0.1",
            port: int = 8900,
            auto_connect: bool = True,
            buffer_size: int = 2048,
    ):
        """
        init
        
        :param encrypt_method: the method of encryption
                                currently support: rsa, none
        :param key: the key of sender/receiver
                    Sender holds the public key (use to encrypt & verify),
                    Receiver holds the private key (use to decrypt & sign).
        :param ip: IP of Receiver
                    Default value set to 127.0.0.1, which is localhost
                    Receiver.ip should set to 0.0.0.0
        :param port: port of Receiver
                    Default value set to 8900
        :param auto_connect: whether to connect automatically when init
        :param buffer_size: size of receiving buffer.
                            Default value set to 2048 (2k)
        """
        self._salt = None
        self._is_connected = None

        self.key = key
        self.buffer_size = int(buffer_size)
        self.server_address = (str(ip), int(port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.encrypt_method = str(encrypt_method)

        if auto_connect:
            self.connect()

    def salt(self, verify=False):
        """
        use a 16-bytes long AES key as salt

        :param verify: whether the salt value is used for verify
        :return: bytes
        """
        if not verify:
            self._salt = Cryptor.generate_AES_key()
        return self._salt

    @property
    def encrypt_method(self):
        return

    @encrypt_method.setter
    def encrypt_method(self, method: str):
        """
        set protocol for transport

        :param method: same as encrypt_method in __init__()
        :return: none
        """
        method = method.lower()
        if method == "none":
            if self.key is not None:
                raise UserWarning("When not using encryption method, you don't need to pass in a key")

            self._serialize = lambda obj: Serializer.to_byte(obj)
            self._deserialize = lambda bytes_: Serializer.to_obj(bytes_)

            self._build_header = lambda size, md5: self._serialize((size, md5, self.salt()))
            self._read_header = lambda header: self._deserialize(header)
            self._build_ack = lambda size, md5, salt: Cryptor.md5((size, md5, salt)).encode()
            self._verify_ack = lambda ack, size, md5: Cryptor.md5((size, md5, self.salt(verify=True))).encode() == ack

        elif method == "rsa":
            if self.key is None:
                raise ValueError("When using encryption method, you need to pass in a key")

            self._serialize = lambda obj: Cryptor.RSA_encrypt(obj, key=self.key)
            self._deserialize = lambda bytes_: Cryptor.RSA_decrypt(bytes_, key=self.key)

            self._build_header = lambda size, md5: self._serialize(("knight-bus", size, md5, self.salt()))
            self._read_header = lambda header: self._deserialize(header)[1:4]
            self._build_ack = lambda size, md5, salt: Cryptor.RSA_sign(("bus-knight", size, md5, salt), key=self.key)
            self._verify_ack = lambda ack, size, md5: Cryptor.RSA_verify(
                ("bus-knight", size, md5, self.salt(verify=True)), ack, key=self.key)
        else:
            raise NotImplementedError(
                "Method \"{}\" is not currently supported.Try rsa or none.".format(method))

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    def _send_bytes(self, bytes_: bytes):
        """
        send bytes

        First make sure the socket is connected, then use the socket to send some bytes
        :param bytes_:
        :return: None
        :raise ConnectionError: when self.socket send bytes failed
        """
        self.connect()
        try:
            self.socket.send(bytes_)
        except Exception as e:
            raise ConnectionError("Send bytes failed:{}".format(e))

    def _recv_bytes(self, size: int = None):
        """
        receive bytes

        :Note: function will block until recv some bytes
        :param size: max buffer size
        :return: received bytes
        """
        self.connect()
        try:
            bytes_ = self.socket.recv(size if size is not None else self.buffer_size)
        except Exception as e:
            raise ConnectionError("Recv bytes failed:{}".format(e))
        return bytes_

    def _send_object_header(self, size, md5):
        """
        send a header to inform the receiver about the incoming object about its md5 and size,
        and verify if server's signature is valid.

        :param size: size of object in bytes
        :param md5: md5 of object in bytes
        :return: None
        :raise: ConnectionAbortedError: something wrong with server's signature
        """

        try:
            self._send_bytes(self._build_header(size, md5))
            ack = self._recv_bytes()
            if not self._verify_ack(ack, size, md5):
                raise ConnectionError("ACK not matched")
        except Exception as e:
            self.disconnect()
            raise ConnectionAbortedError(
                "FAILED: Connection is unsecured and terminated : {}".format(e)
            )

    def _recv_object_header(self):
        """
        receive a header, get the size & md5 of incoming object, then sign new header and send it back

        :return: size & md5 of incoming object
        :raise: ConnectionAbortedError: header is damaged or something wrong with signature
        """

        try:
            header = self._recv_bytes()
            size, md5, salt = self._read_header(header)
            ack = self._build_ack(size, md5, salt)
            self._send_bytes(ack)
        except Exception as e:
            self.disconnect()
            raise ConnectionAbortedError(
                "FAILED: Connection is unsecured and terminated : {}".format(e)
            )
        return size, md5

    def recv(self):
        """
        receive a object

        receive a object header, then receive bytes according to the object size,
        calculate md5 to check if object is damaged, then decrypt and rebuild the object

        :note: always make sure object is not damaged before build the object
        :return: received object
        :raise: ConnectionAbortedError: receive failed or object is damaged
        """

        size, md5 = self._recv_object_header()
        try:
            bytes_ = b""
            while size > 0:
                buffer = self._recv_bytes(
                    self.buffer_size if size > self.buffer_size else size
                )
                size -= len(buffer)
                bytes_ += buffer
                if not buffer:
                    break
            if md5 != Cryptor.md5(bytes_):
                raise ConnectionError("Object md5 unmatched")
            else:
                obj = self._deserialize(bytes_)
        except Exception as e:
            self.disconnect()
            raise ConnectionAbortedError(
                "FAILED: Receiving object failed : {}".format(e)
            )
        return obj

    def send(self, obj):
        """
        send a object

        send a object header, then the encrypted object
        :param obj: object to be sent
        :return: None
        """

        data = self._serialize(obj)
        self._send_object_header(size=len(data), md5=Cryptor.md5(data))
        self._send_bytes(data)

    def __del__(self):
        """
        destructor

        close all the socket and destruct
        """
        self.socket.close()
        del self
