from Crypto import Random
from Crypto.Cipher import AES
import os

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, iv):
    message = pad(message)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key, iv):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def encrypt_file(file_name, key, iv):
    with open(file_name, 'rb') as fo:
        plaintext = fo.read()
    enc = encrypt(plaintext, key, iv)
    with open(file_name + ".enc", 'wb') as fo:
        fo.write(enc)

def decrypt_file(file_name, key, iv):
    with open(file_name, 'rb') as fo:
        ciphertext = fo.read()
    dec = decrypt(ciphertext, key, iv)
    with open(file_name[:-1], 'wb') as fo:
        fo.write(dec)

#key = '7842f0a1ebc38f44e3e0c81943f685827842f0a1ebc38f44e3e0c81943f68582'.decode('hex')
key = os.urandom(32)
#iv = '7842f0a1ebc38f44e3e0c81943f68582'.decode('hex')
iv = os.urandom(16)
encrypt_file('Grass.jpg', key, iv)
decrypt_file('Grass.jpg.enc', key, iv)
