# from Crypto.Cipher import AES, PKCS1_OAEP
# from Crypto.PublicKey import RSA
# from Crypto import Random
# from Crypto.Random import get_random_bytes
# import hashlib

# key = RSA.generate(2048)
# exported_key = key.exportKey().splitlines()[1:-1]
# new = []
# for i in exported_key:
#     new.append(str(i).replace("b","").replace("'",""))

# print('\n'.join(new))
# private_key = '\n'.join(new)
# # public_key = key.publickey().export_key()
# # print(public_key)

# print("public")

# exported_key2 = key.publickey().export_key().splitlines()[1:-1]
# new2 = []
# for i in exported_key2:
#     new2.append(str(i).replace("b","").replace("'",""))

# print('\n'.join(new2))
# public_key = '\n'.join(new2)

# messg = bytes("message",'utf8')
		

# signature = hashlib.pbkdf2_hmac('sha256',bytes(private_key,"utf8") , messg, 100000).hex()

# sign = bytes(signature,'utf8')
# verification = hashlib.pbkdf2_hmac('sha256',bytes(public_key,"utf8"),messg,  100000).hex()
# print("verification")
# print(verification)
# print("sign")
# print(signature)
































# Inspired from http://coding4streetcred.com/blog/post/Asymmetric-Encryption-Revisited-(in-PyCrypto)
# PyCrypto docs available at https://www.dlitz.net/software/pycrypto/api/2.6/

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import base64
import ast

def generate_keys():
	# RSA modulus length must be a multiple of 256 and >= 1024
	modulus_length = 256*4 # use larger value in production
	privatekey = RSA.generate(modulus_length, Random.new().read)
	publickey = privatekey.publickey()
	return privatekey, publickey

def encrypt_message(a_message , publickey):
    encryptor = PKCS1_OAEP.new(publickey)
    encrypted = encryptor.encrypt(bytes(a_message,"utf8"))
    encoded_encrypted_msg = base64.b64encode(encrypted) # base64 encoded strings are database friendly
    return encoded_encrypted_msg


def decrypt_message(encoded_encrypted_msg, privatekey):
    
    decryptor = PKCS1_OAEP.new(privatekey)
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decrypted = decryptor.decrypt(ast.literal_eval(str(decoded_encrypted_msg)))
    
	# decoded_decrypted_msg = privatekey.decrypt(decoded_encrypted_msg)
    return decrypted

########## BEGIN ##########

a_message = "The quick brow11n fox jumped over the lazy dog"
privatekey , publickey = generate_keys()
encrypted_msg = encrypt_message(a_message , publickey)
decrypted_msg = decrypt_message(encrypted_msg, privatekey)

print ("%s " % (privatekey.exportKey() ))
print ("%s " % (publickey.exportKey() ))
print (" Original content: %s " % (a_message))
print ("Encrypted message: %s " % (encrypted_msg))
print ("Decrypted message: %s " % (decrypted_msg))
