from datetime import datetime
from Crypto.Hash import SHA

def create_block_content(previous_hash, transactions):
	""" Creates a text with the hash of the previous block and the transactions
		This text will be placed in the corresponding block """

	block_content = str(previous_hash) + '\n'

	for tr in transactions:
		block_content += tr.text

	return block_content

def sha(text):
	""" Hash the text with SHA encryption
		The output is the hashed text in binary form """

	byte_string = text.encode()
	hashed = SHA.new(byte_string)
	hex_string = hashed.hexdigest()
	bin_string = bin(int(hex_string, 16))[2:]

	return bin_string


class Block:
	def __init__(self, previousHash, nonce, listOfTransactions, genesis = False):

		self.previousHash = previousHash
		self.timestamp = datetime.now()
		self.nonce = nonce
		self.listOfTransactions = listOfTransactions
		self.hash = self.myHash(self.previousHash, self.listOfTransactions)
		self.genesis = genesis


	def myHash(self, previousHash, listOfTransactions):
		""" Calculates the hash of the block """

		transactions = create_block_content(previousHash, listOfTransactions)

		text = str(self.previousHash) + '\n'
		text += transactions
		text += str(self.nonce)

		return sha(text)

	def __str__(self):
		text = 'Block ID\n'
		text += hex(int(self.hash, 2))[2:] + '\n' + '\n'

		text += 'Previous block ID\n'
		if self.genesis:
			text += self.previousHash + '\n' + '\n'
		else:
			text += hex(int(self.previousHash, 2))[2:] + '\n' + '\n'

		text += 'Timestamp\n' + str(self.timestamp) + '\n' + '\n'

		text += 'Capacity: ' + str(len(self.listOfTransactions)) + '\n' + '\n'

		text += 'Transactions\n\n'
		for tr in self.listOfTransactions:
			text += tr.text + '\n'

		text += 'Nonce: ' + str(self.nonce) + '\n' + '\n'

		return text