import wallet
import transaction
from transaction import Transaction
from block import create_block_content
from block import Block
import settings
import binascii
import Crypto
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import random
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import base64
import ast
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

class node:
	def __init__(self, num_nodes = 0, coordinator = {}):

		self.node_id = None

		self.wallet = self.create_wallet()

		self.boostrap_node = False

		self.ring = None

		self.blockchain = None

		self.current_id_count = None

		self.unspent_transactions = None
		self.num_nodes = None
		if num_nodes:
			self.boostrap_node = True
			print("Boostrap node")

			self.id = 0

			self.num_nodes = num_nodes

			self.current_id_count = 0

			self.ring = [dict() for x in range(num_nodes)] # here we store information for every node, as its id, its address (ip:port)

			self.ring[0]['id'] = self.id
			self.ring[0]['ip'] = coordinator['ip']
			self.ring[0]['port'] = coordinator['port']
			self.ring[0]['public_key'] = self.wallet.public_key.exportKey('PEM')

			genesis_block = self.create_genesis_block()

			self.blockchain = [genesis_block]

			self.wallet.transactions = self.unspent_transactions


	def validate_transaction(self, transaction):
		""" When a transaction is received, it needs to be verified first """
		
		sender_public_key = transaction.sender_address

		# Check if it is signed by the sender
		message = transaction.text
		signature = transaction.signature
		h = SHA.new(message)
		verifier = PKCS1_v1_5.new(sender_public_key)

		if not verifier.verify(h, signature):
			print("The transaction have not been signed by the sender")

			return False

		# Chech if there are enough previous unspent transactions of the sender in order to pay the receiver the transaction amount
		sender = transaction.sender_str
		amount = transaction.amount
		transaction_input = transaction.transaction_input
		transaction_output = transaction.transaction_output

		available_amount = 0
		for tr in transaction_input:
			if tr not in self.unspent_transactions:
				print("Input unspent transaction has already been spent")

				return False

			if tr['wallet_id'] == sender:
				available_amount += tr['amount']

			else:
				print("Input unspent transactions contain utxos that are not belong to the sender")

				return False

		if available_amount < amount:
			print("Input unspent transactions are not enough for the transaction")

			return False

		# Check if the unspent transactions output is correct
		change = available_amount - amount
		receiver = transaction.receiver_str
		for tr in transaction_output:
			if tr['wallet_id'] == sender:
				if tr['amount'] != change:
					print("Sender's utxo does not contains the propper amount")

					return False

			if tr['wallet_id'] == receiver:
				if tr['amount'] != amount:
					print("Receiver's utxo does not contains the propper amount")

					return False

			if len(transaction_output) > 2:
				print("Output unspent transactions are more than two")

				return False


			# Transaction is valid

			# We remove the transaction input unspent transactions cause now they are spent
			self.unspent_transactions = list(filter(lambda utxo: utxo not in transaction_input, self.unspent_transactions))

			# We add the new unspent transactions to the list
			self.unspent_transactions = list(np.concatenate((self.unspent_transactions, transaction_output), axis = 0))

			return True


	def create_wallet(self):
		""" Creates a wallet for this node, with a public key and a private key """

		my_wallet = wallet.wallet()

		return my_wallet


	def show_wallet_balance(self):
		self.wallet.showBalance()

	def create_genesis_block(self):
		""" The first block of the blockhain """

		prev_has = "1"
		nonce = 0
		sender = "0"
		sender_private_key = None
		receiver = self.wallet.public_key
		amount = 100 * self.num_nodes
		prev_transactions = []

		genesis_transaction  = Transaction(sender, sender_private_key, receiver, amount, prev_transactions, genesis_transaction = True)

		self.unspent_transactions = genesis_transaction.transaction_output

		genesis_block = Block(prev_has, nonce, [genesis_transaction], genesis = True)

		return genesis_block

	
	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		raise


	def create_transaction(self, receiver, value):
		new_transaction = Transaction(self.wallet.public_key, self.wallet.private_key, receiver, value, self.wallet.transactions)

		return new_transaction


	def add_transaction_to_block(self, new_transaction):
		if self.validate_transaction(new_transaction):
			self.open_transactions.append(new_transaction)

			if len(open_transactions) == settings.capacity:
				previous_hash = self.find_last_block_hash()

				block_content = create_block_content(previous_hash, open_transactions)
				
				nonce = self.mine_block(block_content, settings.difficulty)

				# creates the new block that found
				new_block = Block(previous_hash, nonce, self.open_transactions)

				self.add_block_to_chain(new_block)

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

	def add_block_to_chain(block):
		self.blockchain.append(block)

	def find_last_block_hash():
		prev = self.blockchain[-1]

		return prev.hash

	def show_blockchain(self):
		for i, block in enumerate(self.blockchain):
			print('BLOCK', i, '\n')
			print(block)


	def valid_proof(self, block):
		""" Checks if the broadcasted new block is valid """

		difficulty = settings.difficulty
		transactions = block.listOfTransactions
		previous_hash = block.previousHash
		block_hash = block.hash
		nonce = block.nonce

		# Check if the hash of the block is its true hash
		block_content = create_block_content(previous_hash, transactions)
		hashed = sha(block_content + str(nonce))
		if not (hashed == block_hash):
			print("Block hash is fake")

			return False

		# Check the proof of work
		if not correct_block(hashed, difficulty):
			print("The block does not achieves the needed proof of work")

			return False

		# Check if the number of transactions is equal to block capacity
		if len(transactions) != settings.capacity:
			print("The number of transactions is not equal to block capacity")

			return False

		# Check if the transactions are valid
		for tr in transactions:
			if not validate_transaction(tr):
				print("Transaction with ID", tr.transaction_id, "is not valid")

				return False


		# Block is valid
		return True



	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes
		pass


	def resolve_conflicts(self):
		#resolve correct chain
		pass



if __name__ == "__main__":

	try:
		coord = {}
		coord['ip'] = '192.168.1.1'
		coord['port'] = '5000'
		my_node = node(num_nodes = 5, coordinator = coord)

	except Exception as ex:
		print("Node is not created.")
		raise ex

	else:
		print("Node is created with success.\n")

	my_node.show_wallet_balance()

	my_node.show_blockchain()
