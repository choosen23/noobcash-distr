import blockchain



class Block:
	def __init__(self, previousHash, timestamp, hash, nonce, listOfTransactions):
		##set

		self.previousHash = previousHash
		self.timestamp = timestamp
		self.hash = hash
		self.nonce = nonce
		self.listOfTransactions = listOfTransactions
		pass

	def myHash(self):
		#calculate self.hash
		pass

	def add_transaction(transaction transaction, blockchain blockchain):
		#add a transaction to the block

