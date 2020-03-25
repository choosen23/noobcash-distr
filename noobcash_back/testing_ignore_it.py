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


if __name__ == "__main__":
	public, private = generate_keys()
	signature = sign_transaction(private)

	print('sig done')
	s = signature.decode("utf-8")[:-1]
	print(s)
	print(type(s))