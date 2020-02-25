from knight_bus.Sender import Sender

key = b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDZopcygBiwWt0LE7FeWohNHtq/\nbQG8gWHdYnvjrJDYDGyl4vAyrc7Ce96k1V+JAsLYCaSMabw5Y0c18Dt7lw8cXiAE\nylZbycECpRvssKM+wEkf6Hml3Lyc7xOLTTad9zpYePxjgjPRAyLzbG7ADKMPBBmL\nW9kNxNv1llZa6wMrpQIDAQAB\n-----END PUBLIC KEY-----"

sender = Sender(key)
sender.send(list(range(10000)))
