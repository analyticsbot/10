from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
import os

def encrypt(in_file, out_file, key, iv):
    bs = AES.block_size
    cipher = AES.new(key, AES.MODE_CBC, iv)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = bs - (len(chunk) % bs)
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, key, iv):
    bs = AES.block_size
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            if padding_length < 1 or padding_length > bs:
               raise ValueError("bad decrypt pad (%d)" % padding_length)           
            if chunk[-padding_length:] != (padding_length * chr(padding_length)):               
               raise ValueError("bad decrypt")
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)

in_file = open('Harvard_Business_Review_Logo.jpg', 'rb')
out_file = open('Harvard_Business_Review_Logo_enc.jpg', 'wb')
key = os.urandom(32)
iv = os.urandom(16)
encrypt(in_file, out_file, key, iv)
in_file.close()
out_file.close()

in_file = open('Harvard_Business_Review_Logo_enc.jpg', 'rb')
out_file = open('Harvard_Business_Review_Logo_dec.jpg', 'wb')
decrypt(in_file, out_file, key, iv)
in_file.close()
out_file.close()


in_file = open('Chrysanthemum.jpg', 'rb')
out_file = open('Chrysanthemum_enc.jpg', 'wb')
key = os.urandom(32)
iv = os.urandom(16)
encrypt(in_file, out_file, key, iv)
in_file.close()
out_file.close()

in_file = open('Chrysanthemum_enc.jpg', 'rb')
out_file = open('Chrysanthemum_dec.jpg', 'wb')
decrypt(in_file, out_file, key, iv)
in_file.close()
out_file.close()
