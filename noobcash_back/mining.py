from block import create_block_content
from block import Block
import settings
import numpy as np
from random import randint
from Crypto.Hash import SHA

MAX_INT =  9223372036854775807

def makeCopy(x):
	cp = []
	
	for tr in x:
		newtr = {}
		newtr = tr.copy()
		cp.append(newtr)
	
	return cp

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

def mining_content(node):
	if len(node.open_transactions) < settings.capacity:
		print("The open transactions are fewer than the required block capacity")

		return None

	unspent_to_use = makeCopy(node.unspent_transactions)

	to_be_mined = []

	for i in range(0, len(node.open_transactions)):
		new_tr = node.open_transactions[i]
		new_tr = mining_recalculate(unspent_to_use, new_tr)

		if new_tr.canBeDone:
			to_be_mined.append(new_tr)

			if len(to_be_mined) == settings.capacity:
				break
		
			transaction_input = new_tr.transaction_input
			transaction_output = new_tr.transaction_output

			# We add the new unspent transactions to the list
			unspent_to_use = list(np.concatenate((unspent_to_use, transaction_output), axis = 0))
		
			# We remove the transaction input unspent transactions cause now they are spent
			unspent_to_use = list(filter(lambda utxo: utxo not in transaction_input, unspent_to_use))
		
	if len(to_be_mined) < settings.capacity:
		print("The open transactions that can be done are fewer than the required block capacity")
		return None

	previous_hash = node.find_last_block_hash()
	block_content = create_block_content(previous_hash, to_be_mined)

	return block_content, previous_hash, to_be_mined


def mining_recalculate(unspent_trs, open_tr):

	open_tr.canBeDone = False

	unspent = [] # contains all the unspent transactions of the sender
	available_amount = 0

	for tr in unspent_trs:
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

def mine_block(block_content):
	difficulty = settings.difficulty
		
	nonce = randint(0, MAX_INT)

	while(True):
		hashed = sha(block_content + str(nonce))
		if correct_block(hashed, difficulty):
			print("New block is mined with success!")
			print("Nonce:", nonce)
			print("Block ID:", hashed)
			print("Binary hash lenght", len(hashed))

			return nonce
				

		try:
			nonce = randint(0, MAX_INT)

		except Exception as ex:
			print("nonce reached max value")
			raise ex

def create_mined_block(previous_hash, nonce, to_be_mined):
	# creates the new block that found
	new_block = Block(previous_hash, nonce, to_be_mined)

	return new_block


if __name__ == '__main__':

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

	node2.unspent_transactions = my_node.unspent_transactions

	tr = my_node.create_transaction(node2.wallet.public_key, 120)

	res = my_node.add_transaction_to_block(tr)

	if res == 'mine':
		print('node is ready to mine')
		block_content, previous_hash, to_be_mined = mining_content(my_node)
		nonce = mine_block(block_content)
		new_block = create_mined_block(previous_hash, nonce, to_be_mined)