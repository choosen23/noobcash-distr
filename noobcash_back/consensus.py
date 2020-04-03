from block import create_block_content
from mining import sha, correct_block
import transaction
import settings

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import numpy as np

def makeCopy(x):
	cp = []
	
	for tr in x:
		newtr = {}
		newtr = tr.copy()
		cp.append(newtr)
	
	return cp

class state:

	def __init__(self, genesis_block, open_transactions):

		if not genesis_block.genesis:
			raise ValueError('genesis_block is not a real genesis block')
		
		self.blockchain = [genesis_block]

		genesis_transaction = genesis_block.listOfTransactions[0]
		self.unspent_transactions = genesis_transaction.transaction_output

		self.open_transactions = open_transactions

		self.valid_blockchain = True


	def find_last_block_hash(self):
		prev = self.blockchain[-1]

		return prev.hash	


	def validate_blockchain(self, blockhain):
		for block in blockhain:
			if block.genesis:
				continue
			
			if self.validate_block(block):
				if not self.add_block_to_chain(block):
					print('Blockchain is not valid cause blocks are not connected with their hashes')
					self.valid_blockchain = False
			else:
				print('Blockchain is not valid cause block with id', hex(int(block.hash, 2))[2:], 'is not valid')
				self.valid_blockchain = False

	def recalculate(self, open_tr):

		open_tr.canBeDone = False

		unspent = [] # contains all the unspent transactions of the sender
		available_amount = 0

		for tr in self.unspent_transactions:
			if tr['wallet_id'] == open_tr.sender_str:
				available_amount += tr['amount']
				unspent.append(tr)

		if available_amount < open_tr.amount:
			""" Sender does not have enough UTXOs
				Transaction cannot be done """

			open_tr.canBeDone = False

			print("Transaction cannot be done due to sender's lack of money")

			return open_tr

		sorted_trs = sorted(unspent, key = lambda t : t['amount'])

		input_trs = []
		output_trs = []

		paid = 0
		while (paid < open_tr.amount):
			tr = sorted_trs.pop(0) # utxo will be used for this transaction so it is removes from the list
			input_trs.append(tr) # also this transactions is added to input transactions
			paid += tr['amount']
			if (paid > open_tr.amount):
				change = paid - open_tr.amount

				new_tr = {} # we create a new utxo for sender
				new_tr['transaction_id'] = tr['transaction_id']
				new_tr['wallet_id'] = tr['wallet_id']
				new_tr['amount'] = change

				output_trs.append(new_tr)

		new_tr = {} # we create a new utxo for receiver
		new_tr['transaction_id'] = open_tr.transaction_id
		new_tr['wallet_id'] = open_tr.receiver_str
		new_tr['amount'] = open_tr.amount
		output_trs.append(new_tr)

		open_tr.canBeDone = True

		open_tr.transaction_input = input_trs
		open_tr.transaction_output = output_trs

		return open_tr

	def add_block_to_chain(self, block):
		"""
			Returns:

				True  : Block has been put in the node's blockchain, open and unspent transactions has been updated
				False : Block has not been put in the node's blockchain
		"""

		last_hash = self.find_last_block_hash()
		prev_hash = block.previousHash

		if prev_hash != last_hash:
			print('New block is rejected')
			print('New block cannot be put in the blockchain cause its previous hash is not equal to the hash of the current last block')

			return False
		
		transactions = block.listOfTransactions

		for tr in transactions:
			transaction_input = tr.transaction_input
			transaction_output = tr.transaction_output

			# We remove the transaction from the open transactions
			self.open_transactions = list(filter(lambda open_tr: open_tr.transaction_id != tr.transaction_id, self.open_transactions))

			# We add the new unspent transactions to the list
			self.unspent_transactions = list(np.concatenate((self.unspent_transactions, transaction_output), axis = 0))

			# We remove the transaction input unspent transactions cause now they are spent
			self.unspent_transactions = list(filter(lambda utxo: utxo not in transaction_input, self.unspent_transactions))
		
		for i, open_tr in enumerate(self.open_transactions):
			self.open_transactions[i] = self.recalculate(open_tr)

		self.blockchain.append(block)

		return True


	def validate_block(self, block):
		""" Checks if the block is valid """

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
			print(hashed)
			print(block_hash)
			print(previous_hash)
			return False

		# Check the proof of work
		if not correct_block(hashed, difficulty):
			print("The block does not achieves the needed proof of work")

			return False

		# Check if the number of transactions is equal to block capacity
		if len(transactions) != settings.capacity:
			print("The number of transactions is not equal to block capacity")

			return False

		prev_unspent = makeCopy(self.unspent_transactions)
		# Check if the transactions are valid
		for tr in transactions:
			is_valid = self.validate_transaction(tr)
			if is_valid:
				transaction_input = tr.transaction_input
				transaction_output = tr.transaction_output

				# We add the new unspent transactions to the list
				self.unspent_transactions = list(np.concatenate((self.unspent_transactions, transaction_output), axis = 0))

				# We remove the transaction input unspent transactions cause now they are spent
				self.unspent_transactions = list(filter(lambda utxo: utxo not in transaction_input, self.unspent_transactions))

			else:
				print("Block contains transactions that are not valid")
				print("Transaction with ID", tr.transaction_id, "is not valid")

				self.unspent_transactions = makeCopy(prev_unspent)

				return False
			
		# Block is valid
		self.unspent_transactions = makeCopy(prev_unspent)
		return True


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

		# Chech if sender and receiver is the same
		sender = transaction.sender_str
		receiver = transaction.receiver_str
		if sender == receiver:
			print("Sender and receiver has the same wallet public key")

			return False

		# Chech if there are enough previous unspent transactions of the sender in order to pay the receiver the transaction amount
		sender = transaction.sender_str
		amount = transaction.amount
		transaction_input = transaction.transaction_input
		transaction_output = transaction.transaction_output

		available_amount = 0
		for tr in transaction_input:
			if tr not in self.unspent_transactions:
				print("Input unspent transaction has already been spent or never existed")

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