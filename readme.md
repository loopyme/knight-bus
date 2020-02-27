# knight-bus

Knight bus can **safely** and **losslessly** transport most of your python objects from one process(or computer) to another. 

The following types of objects can use the knight-bus:
 - None, True, and False
 - integers, floating point numbers, complex numbers
 - strings, bytes, bytearrays
 - tuples, lists, sets, and dictionaries containing only picklable objects
 - functions defined at the top level of a module (using def, not lambda)
 - built-in functions defined at the top level of a module
 - classes that are defined at the top level of a module
 - instances of such classes whose __dict__ or the result of calling __getstate__() is picklable (see section [Pickling Class Instances](https://docs.python.org/3/library/pickle.html#pickle-inst) for details).

## How do I use it?

1. To hail the bus, you need to install it first: `pip install knight-bus`
2. Then you need to get a pair of RSA-keys(Skip this step if you already have your keys):
    ```python
   from loopyCryptor import generate_RSA_key
   
   
   pub_key, pri_key = generate_RSA_key()
   
   # Then you can either print it and copy to your code or 
   # save the key as a file
   ...
    ```
3. Launch the Receiver
    ```python
   from knight_bus.Receiver import Receiver

   
   key = b"-----BEGIN RSA PRIVATE KEY-----\n ......"

   receiver = Receiver(key=key)
   obj = receiver.recv()    # This step blocks until an object is received.
    ```
4. Use Sender to send object
    ```python
   from knight_bus.Sender import Sender

   
   key = b"-----BEGIN PUBLIC KEY-----\n ......"
     
   sender = Sender(key=key, ip="....", port=...)
   sender.send([1,2,"3",{"4":"four"}])
    ```
5. The object has been transported to `obj` by knight-bus!!!

Examples: [dev_test](https://github.com/loopyme/knight-bus/tree/master/test/dev_test) or [unit_test](https://github.com/loopyme/knight-bus/blob/master/test/unit_test/test.py) may able to help you understand how to use it.

## Why is it named knight-bus?
> [Harry Potter Wiki](https://harrypotter.fandom.com/wiki/Knight_Bus): *The Knight Bus is a triple-decker, purple AEC Regent III RT that assists stranded individuals of the wizarding community through public transportation.*

This project is similar to Knight Bus in that objects are transported to their destination by *magic*. The transport process is magical and complicated, but the wizard or user need not worry about the transport process, only need to fully trust that the transport process is safe and lossless.

## How does it work?

> Note: As a muggle user, there is no need to worry about how the knight-bus deforms and works.


> The knight-bus is based on lots of magic technology, such as `pickle`,`pycryptodome`,`socket` and `loopyCrypto`

The following is the workflow of the knightBus (when using default parameters). You can also call some setting functions and adjust some parameters to customize your workflow.

1. Once `Reciever` is instantiation, it create a listen socket, bind the address and waiting for connection.
2. Once `Sender` is instantiation, it create a socket to receiver. Later when `Sender.send` is called, it will calculate the md5 & size of the transfer object, encrypt the result along with a salt and a magic code with the given RSA public key, finally send cipher text to `Reciever`.  
3. When `Reciever` get the cipher text, it use the given RSA private key decrypt the text and check the magic code. If matched, it will calculate md5 of a list which contains the salt, size and md5(object). Then sign the result along with the magic code, finally send the signature back. 
4. Then `Sender` verify the signature and then start to transport the encrypt object.
5. `Reciever` get the encrypt object and check its md5 and size(make sure it is what you want), decrypt it to the object if md5 and size matched.
6. Finally, you will get a deep copy of the origin object in another machine.

## Why do I make it?
We already have so many muggle ways to transport data, like `json`. However, I am tired of caring about data types and transmission security issues and care less about efficiency. I always like to make or use magic(black box) to solve problems. Just throw the raw material in, then wait for magic, poof!
