#import blockchain
import test_node as node #import node sto telos

from datetime import datetime


class Block:
	def __init__(self, previousHash, nonce, listOfTransactions):

		self.previousHash = previousHash
		self.timestamp = datetime.now()
		self.nonce = nonce
		self.listOfTransactions = listOfTransactions
		self.hash = myHash(listOfTransactions)


	def myHash(self, listOfTransactions):
		""" Calculates the hash of the block """

		transactions = node.transactions_text(listOfTransactions)

		text = str(self.previousHash) + '\n'
		text += transactions
		text += str(self.nonce)

		return text

	def add_transaction(transaction, blockchain):
		#add a transaction to the block
		pass
