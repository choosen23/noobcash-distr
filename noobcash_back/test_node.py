import block
import wallet
import transaction
from transaction import Transaction

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

def transactions_text(transactions):
	""" Creates a text with the transactions
		This text will be placed in the corresponding block """
		
	text = []

	for tr in transactions:
		text += tr.text + '\n'

	return text




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

		self.blockchain = []

		#self.current_id_count
		#self.NBCs

		self.wallet = self.create_wallet()

		#self.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance

	def validate_transaction(self, transaction, encrypted_transaction_message):

		#Define pk (Public Key) and sk (Secret Key)
		sk = self.wallet.private_key
		pk = self.wallet.public_key

		#We define the message
		message = transaction.text
		encrypted_msg = encrypt_message(message, pk)
		decrypted_msg = decrypt_message(encrypted_msg, sk)

		# print("%s " % (sk.exportKey()))
		# print("%s " % (pk.exportKey()))
		print("Original content: %s " % (message))
		print("Encrypted message: %s " % (encrypted_msg))
		print("Decrypted message: %s " % (decrypted_msg))

		return 0


	def create_wallet(self):
		""" Creates a wallet for this node, with a public key and a private key """

		my_wallet = wallet.wallet()

		return my_wallet


	def show_wallet_balance(self):
		self.wallet.showBalance()

	
	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		raise


	def create_transaction(self, receiver, value):
		#remember to broadcast it
		new_transaction = Transaction(self.wallet.public_key, self.wallet.private_key, receiver, value, self.wallet.transactions)

		broadcast_transaction(new_transaction)


	def broadcast_transaction():
		# MHTSOOOOOOO
		pass


	def add_transaction_to_block(self, new_transaction):
		if self.validdate_transaction(new_transaction):
			self.open_transactions.append(new_transaction)

			#capacity must be defined somewhere
			if len(open_transactions) == capacity:
				previous_hash = self.blockchain.getHashOfTheLastBlock

				block_content = str(previous_hash) + '\n'
				block_content += transactions_text(self.open_transactions)
				
				#capacity must be defined somewhere
				nonce = self.mine_block(block_content, difficulty)

				new_block = Block(previous_hash, nonce, self.open_transactions)

				broadcast_block(new_block)


	def mine_block(self, block, difficulty):
		nonce = 0

		while(True):
			hashed = sha(block + str(nonce))
			if correct_block(hashed, difficulty):
				print("New block is mined with success!")
				print("Nonce:", nonce)
				print("Block ID:", hashed)
				print("Binary hash lenght", len(hashed))

				return nonce

			try:
				nonce += 1
						
			except Exception as ex:
				print("nonce reached max value")
				raise ex


	def broadcast_block(self):
		# MHTSOOOOO
		pass


	def valid_proof(self, block, difficulty):
		pass


	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes
		pass


	def resolve_conflicts(self):
		#resolve correct chain
		pass



if __name__ == "__main__":

	try:
		node_id = int(sys.argv[1])
		my_node = node(node_id)

	except Exception as ex:
		print("Node is not created.")
		raise ex

	else:
		print("Node is created with success.\n")

	my_node.show_wallet_balance()
