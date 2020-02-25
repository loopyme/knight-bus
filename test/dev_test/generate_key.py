from loopyCryptor import generate_RSA_key

pub_key, pri_key = generate_RSA_key()

print("{}\n{}".format(pub_key, pri_key))
