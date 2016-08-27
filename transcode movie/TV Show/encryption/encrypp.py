from Crypto import Random
from Crypto.Cipher import AES

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, iv):
    message = pad(message)
    #iv = Random.new().read(AES.block_size)
    #print iv
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(message)

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

#key = b'\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18'
from random import choice
from string import ascii_uppercase

key = (''.join(choice(ascii_uppercase) for i in range(16)))
print key
iv = (''.join(choice(ascii_uppercase) for i in range(16)))
#iv = hex(iv)
print iv
encrypt_file('Grass.jpg', key, iv)
decrypt_file('Grass.jpg.enc', key, iv)
