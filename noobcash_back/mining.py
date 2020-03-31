from block import create_block_content
from block import Block
import settings

from Crypto.Hash import SHA

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

	to_be_mined = node.open_transactions[:settings.capacity]
	previous_hash = node.find_last_block_hash()
	block_content = create_block_content(previous_hash, to_be_mined)

	return block_content, previous_hash, to_be_mined
	
def mine_block(block_content):
	difficulty = settings.difficulty
		
	nonce = 0

	while(True):
		hashed = sha(block_content + str(nonce))
		if correct_block(hashed, difficulty):
			print("New block is mined with success!")
			print("Nonce:", nonce)
			print("Block ID:", hashed)
			print("Binary hash lenght", len(hashed))

			return nonce
				
			# creates the new block that found
			new_block = Block(previous_hash, nonce, to_be_mined)

			return new_block

		try:
			nonce += 1

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