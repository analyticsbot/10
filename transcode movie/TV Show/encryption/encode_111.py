from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from random import choice
from string import ascii_uppercase

##def derive_key_and_iv(password, salt, key_length, iv_length):
##    d = d_i = ''
##    while len(d) < key_length + iv_length:
##        d_i = md5(d_i + password + salt).digest()
##        d += d_i
##    return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(in_file, out_file, key, iv, key_length=16):
    bs = AES.block_size
    #salt = Random.new().read(bs - len('Salted__'))
    #key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    #out_file.write('Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = 0
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, key, iv, key_length=16):
    bs = AES.block_size
##    salt = in_file.read(bs)[len('Salted__'):]
##    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = 0
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)

key = (''.join(choice(ascii_uppercase) for i in range(16)))
print key
iv = (''.join(choice(ascii_uppercase) for i in range(16)))
#iv = hex(iv)
print iv

in_file = open('Grass.jpg', 'rb')
out_file = open('Grass.jpg.ec', 'wb')
encrypt(in_file, out_file, key, iv, key_length=32)
decrypt(open('Grass.jpg.ec', 'rb'), open('Grass_.jpg', 'wb'), key, iv, key_length=16)
