from Crypto.Cipher import AES
from Crypto import Random
from PIL import Image


# the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
IV_SIZE = 16
BLOCK_SIZE = 16
cipher_mode = 'CBC'

def encrypt(input_filename, output_filename, cipher_mode, key, iv, chunksize=64*1024):
    """Encrypt an image file and write out the results as a JPEG."""
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(input_filename)

    with open(input_filename, 'rb') as infile:
        with open(output_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))
    os.remove(input_filename)
    
    print("Encrypted using AES in " + cipher_mode + " mode and saved to \"" +
           output_filename + "\"!")

encrypt(input_filename, output_filename, cipher_mode, key, iv)
