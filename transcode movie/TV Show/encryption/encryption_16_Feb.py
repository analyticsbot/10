from __future__ import print_function, unicode_literals
from random import choice
from string import ascii_uppercase
__all__ = ('encrypt', 'decrypt')

import argparse
import os
import struct
import sys

from getpass import getpass
from os.path import exists, splitext

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2


SALT_MARKER = b'$'
ITERATIONS = 1000


def encrypt(infile, outfile, password, key_size=32, salt_marker=SALT_MARKER,
        kdf_iterations=ITERATIONS, hashmod=SHA256):
    if not 1 <= len(salt_marker) <= 6:
        raise ValueError('The salt_marker must be one to six bytes long.')
    elif not isinstance(salt_marker, bytes):
        raise TypeError('salt_marker must be a bytes instance.')

    if kdf_iterations >= 65536:
        raise ValueError('kdf_iterations must be <= 65535.')

    bs = AES.block_size
    header = salt_marker + struct.pack('>H', kdf_iterations) + salt_marker
    salt = os.urandom(bs - len(header))
    kdf = PBKDF2(password, salt, min(kdf_iterations, 65535), hashmod)
    key = kdf.read(key_size)
    iv = os.urandom(bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    outfile.write(header + salt)
    outfile.write(iv)
    finished = False

    while not finished:
        chunk = infile.read(1024 * bs)

        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += (padding_length * chr(padding_length)).encode()
            finished = True

        outfile.write(cipher.encrypt(chunk))


def decrypt(infile, outfile, password, key_size=32, salt_marker=SALT_MARKER,
        hashmod=SHA256):
    mlen = len(salt_marker)
    hlen = mlen * 2 + 2

    if not 1 <= mlen <= 6:
        raise ValueError('The salt_marker must be one to six bytes long.')
    elif not isinstance(salt_marker, bytes):
        raise TypeError('salt_marker must be a bytes instance.')

    bs = AES.block_size
    salt = infile.read(bs)

    if salt[:mlen] == salt_marker and salt[mlen + 2:hlen] == salt_marker:
        kdf_iterations = struct.unpack('>H', salt[mlen:mlen + 2])[0]
        salt = salt[hlen:]
    else:
        kdf_iterations = ITERATIONS

    if kdf_iterations >= 65536:
        raise ValueError('kdf_iterations must be <= 65535.')

    iv = infile.read(bs)
    kdf = PBKDF2(password, salt, kdf_iterations, hashmod)
    key = kdf.read(key_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = b''
    finished = False

    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(infile.read(1024 * bs))

        if not next_chunk:
            padlen = chunk[-1]
            if isinstance(padlen, str):
                padlen = ord(padlen)
                padding = padlen * chr(padlen)
            else:
                padding = (padlen * chr(chunk[-1])).encode()

            if padlen < 1 or padlen > bs:
                raise ValueError("bad decrypt pad (%d)" % padlen)

            # all the pad-bytes must be the same
            if chunk[-padlen:] != padding:
                # this is similar to the bad decrypt:evp_enc.c
                # from openssl program
                raise ValueError("bad decrypt")

            chunk = chunk[:-padlen]
            finished = True

        outfile.write(chunk)

infile = open('Grass.jpg', 'rb')
outfile = open('Grass_enc.jpg', 'wb')
key = (''.join(choice(ascii_uppercase) for i in range(32)))
encrypt(infile, outfile, key, key_size=32, salt_marker=SALT_MARKER,
        kdf_iterations=ITERATIONS, hashmod=SHA256)
infile = open('Grass_enc.jpg', 'rb')
outfile = open('Grass_dec.jpg', 'wb')
decrypt(infile, outfile, key, key_size=32, salt_marker=SALT_MARKER,
        hashmod=SHA256)
