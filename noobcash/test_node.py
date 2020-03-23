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

