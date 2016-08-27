from Crypto.Cipher import AES
from Crypto.Util import Counter

key = '7842f0a1ebc38f44e3e0c81943f68582'.decode('hex')
iv = '7842f0a1ebc38f44'.decode('hex')

ctr_e = Counter.new(64, prefix=iv, initial_value=0)
encryptor = AES.new(key, AES.MODE_CBC, counter=ctr_e)

with open('Grass.out.jpg', 'wb') as fout:
    with open('Grass.jpg', 'rb') as fin:
        fout.write(encryptor.encrypt(fin.read()))
