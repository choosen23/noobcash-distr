from block import create_block_content
from mining import sha, correct_block
import transaction
import settings

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

class state:

	def __init__(self, genesis_block, open_transactions):

		if not genesis_block.genesis:
			raise ValueError('genesis_block is not a real genesis block')
		
		self.blockchain = [genesis_block]

		genesis_transaction = genesis_block.listOfTransactions[0]
		self.unspent_transactions = genesis_transaction.transaction_output

		self.open_transactions = open_transactions

		self.valid_blockchain = True

	
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