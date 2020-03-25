import binascii
import Crypto
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
import random
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import base64
import ast
from Crypto.Hash import SHA
import sys


from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def sign_transaction(private_key):
	""" Sign transaction with private key """
	""" We crypto our transaction using private key """

	message = 'giorgis on'
	signature = encrypt_message(message, private_key)

	return signature


def generate_keys():
	# RSA modulus length must be a multiple of 256 and >= 1024
	modulus_length = 256*4  # use larger value in production
	privatekey = RSA.generate(modulus_length, Random.new().read)
	publickey = privatekey.publickey()
	return publickey, privatekey


def encrypt_message(a_message, publickey):
	encryptor = PKCS1_OAEP.new(publickey)
	encrypted = encryptor.encrypt(bytes(a_message, "utf8"))
	# base64 encoded strings are database friendly
	encoded_encrypted_msg = base64.b64encode(encrypted)
	return encoded_encrypted_msg


def decrypt_message(encoded_encrypted_msg, privatekey):
	decryptor = PKCS1_OAEP.new(privatekey)
	decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
	decrypted = decryptor.decrypt(ast.literal_eval(str(decoded_encrypted_msg)))

	return decrypted.decode("utf-8")


from Crypto.PublicKey import RSA
from Crypto.Hash import SHA384s
# Generate keypair and store in global state
def generate_keypair():

	rsa_keypair = RSA.generate(2048)

	privkey = rsa_keypair.exportKey('PEM').decode()
	pubkey = rsa_keypair.publickey().exportKey('PEM').decode()

	return pubkey, privkey

def sign(privatekey):
	'''sign a transaction using our private key'''

	malakies = {}
	malakies['gamimenes'] = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
	rsa_key = RSA.importKey(privatekey)
	signer = PKCS1_v1_5.new(rsa_key)

	id = malakies.hexdigest()
	signature = base64.b64encode(signer.sign(malakies)).decode()

	return signature


if __name__ == "__main__":

	from Crypto.Signature import PKCS1_v1_5
	from Crypto.Hash import SHA
	from Crypto.PublicKey import RSA

	public, private = generate_keypair()

	s = sign(private)

















if __name__ == "__main__1":
	public, private = generate_keys()
	signature = sign_transaction(private)

	print('sig done')
	s = signature.decode("utf-8")[:-1]
	print(s)
	print(type(s))
	print()

	print(public.exportKey("PEM"))
	print(private.exportKey("PEM"))

	en = encrypt_message('giorgiii', public)

	dec = decrypt_message(en, private)

	print(dec)