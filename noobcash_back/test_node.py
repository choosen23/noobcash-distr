import wallet
import transaction
from transaction import Transaction
from block import create_block_content
from block import Block
import settings
from mining import mine_block
import consensus

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
import numpy as np

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

		self.id = None

		self.wallet = self.create_wallet()

		self.boostrap_node = False

		self.ring = None

		self.blockchain = None

		self.current_id_count = None

		self.unspent_transactions = []

		self.open_transactions = []

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

			self.wallet.unspent_transactions = self.unspent_transactions


	def validate_transaction(self, transaction):
		""" When a transaction is received, it needs to be verified first """
		
		sender_public_key = RSA.importKey(transaction.sender_address.encode('utf8'))

		# Check if it is signed by the sender
		message = transaction.to_be_signed
		signature = transaction.signature.encode('latin-1')
		h = SHA.new(message.encode('utf8'))
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

			return True


	def create_wallet(self):
		""" Creates a wallet for this node, with a public key and a private key """

		my_wallet = wallet.wallet()

		return my_wallet

	def wallet_balance(self):
		self.wallet.unspent_transactions = self.unspent_transactions
		return self.wallet.balance()

	def show_wallet_balance(self):
		self.wallet.unspent_transactions = self.unspent_transactions
		self.wallet.showBalance()

	def create_genesis_block(self):
		""" The first block of the blockhain """

		prev_has = "1"
		nonce = 0
		sender = "0"
		sender_private_key = None
		receiver = self.wallet.public_key
		amount = 100 * self.num_nodes

		genesis_transaction = Transaction(sender, receiver, amount, sender_private_key = sender_private_key, genesis_transaction = True)

		self.unspent_transactions = genesis_transaction.transaction_output

		genesis_block = Block(prev_has, nonce, [genesis_transaction], genesis = True)

		return genesis_block


	def init_simple_node(self, blockchain, open_transactions):
		""" Takes the blockchain from the boostrap and initializes its parameters
			If everything is done with success returns True else returns False """

		genesis_block = blockchain[0]
		state = consensus.state(genesis_block, open_transactions)

		if state.valid_blockchain:
			self.blochchain = state.blochchain
			self.unspent_transactions = state.unspent_transactions
			self.open_transactions = state.open_transactions

			return True

		else:
			return False


	def create_transaction(self, receiver, value):
		new_transaction = Transaction(self.wallet.public_key, receiver, value, sender_private_key = self.wallet.private_key, previous_transactions = self.wallet.unspent_transactions)

		return new_transaction


	def add_transaction_to_block(self, new_transaction):
		"""
			Checks what to do with the new transaction that has received by the node

			Returns:

				'OK'         : The transaction is valid and has been put to open transactions
				'mine'       : The transaction is valid and has been put to open transactions, also the miner has to start mining
				'consensus'  : The transaction is not valid and has been rejected
		"""

		if self.validate_transaction(new_transaction):
			self.open_transactions.append(new_transaction)

			if len(self.open_transactions) >= settings.capacity:
				return 'mine'

			else:
				return 'OK'

		return 'rejected'


	def broadcast_block(self):
		# MHTSOOOOO
		pass

	def add_block_to_chain(self, block):
		"""
			Returns:

				True  : Block has been put in the node's blockchain, open and unspent transactions has been updated
				False : Block has not been put in the node's blockchain
		"""

		last_hash = self.find_last_block_hash()
		prev_hash = block.previousHash

		if prev_hash != last_hash:
			print('New block cannot be put in the blockchain cause its previous hash is not equal to the hash of the current last block')

			return False
		
		transactions = block.listOfTransactions

		for tr in transactions:
			transaction_input = tr.transaction_input
			transaction_output = tr.transaction_output

			# We remove the transaction from the open transactions
			self.open_transactions = list(filter(lambda open_tr: open_tr.transaction_id != tr.transaction_id, self.open_transactions))

			# We remove the transaction input unspent transactions cause now they are spent
			self.unspent_transactions = list(filter(lambda utxo: utxo not in transaction_input, self.unspent_transactions))

			# We add the new unspent transactions to the list
			self.unspent_transactions = list(np.concatenate((self.unspent_transactions, transaction_output), axis = 0))

		self.blockchain.append(block)

		return True


	def find_last_block_hash(self):
		prev = self.blockchain[-1]

		return prev.hash

	def show_blockchain(self):
		print('\n------------------------------------------------------------- BLOCKCHAIN STARTS -------------------------------------------------------------\n')

		for i, block in enumerate(self.blockchain):
			print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n')
			print('BLOCK', i, '\n')
			print(block)
		
		print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')

		print('------------------------------------------------------------- BLOCKCHAIN ENDS ------------------------------------------------------------\n')


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
			if not self.validate_transaction(tr):
				print("block contains transactions that are not valid")
				print("Transaction with ID", tr.transaction_id, "is not valid")

				return False


		# Block is valid

		return True


	def block_placement(self, block):
		"""
			Checks what to do with the new block that has already been checked that is valid

			Returns:

				'OK'         : New block is ok to be put in the blockchain, next to the current last block
				'rejected'   : Block belongs to a blockchain with smaller or equal lenght, so it will be rejected
				'consensus'  : Block belongs to an unknown blockchain so consensus has to be checked
		"""

		prev_hash = block.previousHash
		last_block = self.blockchain[-1]

		if last_block.hash == prev_hash:
			return 'OK'

		for b in self.blockchain:
			if b.hash == prev_hash:
				return 'rejected'

		return 'consensus'


	#concencus functions

	def valid_chain(self, blockchains):
		genesis_block = self.blockhain[0]
		open_transactions = self.open_transactions
		best_chain = None
		best_state = None

		for blockchain in blockchains:
			if best_chain is None:
				state = consensus.state(genesis_block, open_transactions)
				if state.valid_blockchain:
					best_chain = blockchain
					best_state = state
			else:
				if len(blockchain) > len(best_chain):
					state = consensus.state(genesis_block, open_transactions)
					if state.valid_blockchain:
						best_chain = blockchain
						best_state = state

		self.blochchain = best_state.blochchain
		self.unspent_transactions = best_state.unspent_transactions
		self.open_transactions = best_state.open_transactions

		print('Best blockchain has been selected')
		

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

	node2 = node()

	node2.unspent_transactions = my_node.unspent_transactions
	node2.blockchain = my_node.blockchain

	tr = my_node.create_transaction(node2.wallet.public_key, 120)

	if node2.validate_transaction(tr):
		print('true')
	else:
		print('TR is fake')

	my_node.show_blockchain()

	exit(-1)

	print(tr.transaction_input)
	print('---------------------')
	print(tr.transaction_output)

	print()
	my_node.show_wallet_balance()
	node2.show_wallet_balance()

	block = my_node.add_transaction_to_block(tr)
	if node2.valid_proof(block):
		print('block is valid by node 2')
		node2.add_block_to_chain(block)
	else:
		print('gamata')


	my_node.show_wallet_balance()
	node2.show_wallet_balance()

	print(my_node.unspent_transactions)
	print(node2.unspent_transactions)