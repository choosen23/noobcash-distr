#import block
import wallet
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

""" Define some functions that is needed """
def sha(text):
	""" Hash the text with SHA encryption
		The output is the hashed text in binary form """

	byte_string = text.encode()
	hashed = SHA.new(byte_string)
	hex_string = hashed.hexdigest()
	bin_string = bin(int(hex_string, 16))[2:]

	return bin_string


def correct_block(hash, difficulty):
	sha_output_len = 160

	if (sha_output_len - len(hash)) >= difficulty:
		return True
	
	return False



def generate_keys():
    # RSA modulus length must be a multiple of 256 and >= 1024
    modulus_length = 256*4  # use larger value in production
    privatekey = RSA.generate(modulus_length, Random.new().read)
    publickey = privatekey.publickey()
    return privatekey, publickey



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

    # decoded_decrypted_msg = privatekey.decrypt(decoded_encrypted_msg)
    return decrypted



class node:
	def __init__(self, node_id):
		#self.NBC=100;
		##set

		self.node_id = node_id
		print("Node ID:", self.node_id)

		self.boostrap_node = False
		if node_id == 0:
			self.boostrap_node = True
			print("Boostrap node")

		self.chain = []

		#self.current_id_count
		#self.NBCs
		self.wallet = self.create_wallet()

		#self.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance

	def validate_transaction(self):
		
		my_wallet = wallet.wallet()
		#Define pk (Public Key) and sk (Secret Key)
		sk = my_wallet.private_key
		pk = my_wallet.public_key

		#We define the message
		message = "Oh nana Oh nanana"
		encrypted_msg = encrypt_message(message, pk)
		decrypted_msg = decrypt_message(encrypted_msg, sk)

		# print("%s " % (sk.exportKey()))
		# print("%s " % (pk.exportKey()))
		print(" Original content: %s " % (message))
		print("Encrypted message: %s " % (encrypted_msg))
		print("Decrypted message: %s " % (decrypted_msg))

		return 0


	def create_wallet(self):
		""" create a wallet for this node, with a public key and a private key """

		my_wallet = wallet.wallet()

		return my_wallet


	def show_wallet_balance(self):
		self.wallet.showBalance()


	def mine_block(self,block, difficulty):
		nonce = 0

		while(True):
			hashed = sha(block + str(nonce))
			if correct_block(hashed, difficulty):
				print("New block is mined with success!")
				print("Nonce:", nonce)
				print("Block ID:", hashed)
				print("Binary hash lenght", len(hashed))

				return hashed

			try:
				nonce += 1
						
			except Exception as ex:
				print("nonce reached max value")
				raise ex


if __name__ == "__main__":

	try:
		node_id = int(sys.argv[1])
		my_node = node(node_id)
		print(my_node.validate_transaction())

	except Exception as ex:
		print("Node is not created.")
		raise ex

	else:
		print("Node is created with success.\n")

	my_node.show_wallet_balance()

