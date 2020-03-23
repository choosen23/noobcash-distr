#import block
import wallet
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import random
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import sys

#function to hash data
def hash_data(data):
    return hashlib.sha256(data.encode('utf8')).hexdigest()

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
		#use of signature and NBCs balance
		my_wallet = wallet.wallet()
		private_key = my_wallet.private_key
		public_key = my_wallet.public_key

		message = hash_data("eimai to mnm")
		
  		#public = hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000).hex()
		
		signature = hashlib.pbkdf2_hmac('sha256', bytes(str(private_key),'utf8'), bytes(message,'utf8'), 100000).hex()
		verification = hashlib.pbkdf2_hmac('sha256', bytes(str(public_key),'utf8'), bytes(signature,'utf8'), 100000).hex()
		print("verification")
		print(verification)
		print("message")
		print(message)
  
		#normally should happend this:
		if (verification == message ):
			print("message signed by private_key associated with public_key")
		else :
			print("not")
		return 0
		
  
	def create_wallet(self):
		""" create a wallet for this node, with a public key and a private key """

		my_wallet = wallet.wallet()

		return my_wallet


	def show_wallet_balance(self):
		self.wallet.showBalance()


	def mine_block(block, difficulty):
		nonce = 0

		while(True):
			hashed = sha(block + str(nonce))
			if correct(hashed, difficulty):
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
		print( my_node.validate_transaction() )

	except Exception as ex:
		print("Node is not created.")
		raise ex

	else:
		print("Node is created with success.\n")

	my_node.show_wallet_balance()

