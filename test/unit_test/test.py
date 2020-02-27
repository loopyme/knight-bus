import multiprocessing
import string
import time
import unittest
from random import choice, randint

from Crypto.Random import get_random_bytes


class foo:
    cls_value = 0

    def __init__(self, value1, value2, cls_value):
        self.value1 = value1
        self.value2 = value2
        self.cls_value = cls_value

    def __eq__(self, other):
        return self.value1 == other.value1 and self.value2 == other.value2 and self.cls_value == other.cls_value


def bar(n):
    return n * bar(n - 1) if n != 1 else 1


def random_str():
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(randint(10, 1000)))


def random_list():
    return list(random_str()) + list(range(randint(4, 20))) + [None]


def random_byte():
    return get_random_bytes(randint(10, 1000))


def random_obj():
    return foo(randint(1, 100), random_byte(), random_str())


def ret_cls():
    return foo


def ret_func():
    return bar


get_obj_list = [random_byte, random_obj, random_str, random_list, ret_cls, ret_func]


class MyTestCase(unittest.TestCase):

    @staticmethod
    def run_send(key, method, q):
        from knight_bus.Sender import Sender
        time.sleep(0.2)  # make sure receiver is open first
        sender = Sender(key=key, encrypt_method=method)
        test_obj = []
        for random_obj in get_obj_list:
            test_obj.append(random_obj())
            sender.send(test_obj[-1])
        q.put(test_obj)
        sender.disconnect()

    @staticmethod
    def run_recv(key, method, q):
        from knight_bus.Receiver import Receiver
        receiver = Receiver(key=key, encrypt_method=method)
        test_obj = []
        for i in range(6):
            test_obj.append(receiver.recv())
        q.put(test_obj)
        receiver.disconnect()

    def test_rsa_transport(self):
        from loopyCryptor import generate_RSA_key
        pub_key, pri_key = generate_RSA_key()
        q = multiprocessing.Queue()
        jobs = [multiprocessing.Process(target=MyTestCase.run_recv, args=(pri_key, 'rsa', q)),
                multiprocessing.Process(target=MyTestCase.run_send, args=(pub_key, 'rsa', q))]
        for p in jobs:
            p.start()
        for p in jobs:
            p.join()

        results = [q.get() for p in jobs]
        self.assertEqual(results[0], results[1])

    def test_none_transport(self):

        q = multiprocessing.Queue()
        jobs = [multiprocessing.Process(target=MyTestCase.run_recv, args=(None, 'none', q)),
                multiprocessing.Process(target=MyTestCase.run_send, args=(None, 'none', q))]
        for p in jobs:
            p.start()
        for p in jobs:
            p.join()

        results = [q.get() for p in jobs]
        self.assertEqual(results[0], results[1])


if __name__ == '__main__':
    unittest.main()
