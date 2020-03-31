from block import create_block_content
from block import Block
import settings

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
	
def mine_block(node):
	if len(node.open_transactions) < settings.capacity:
		print("The open transactions are fewer than the required block capacity")

		return None

	to_be_mined = node.open_transactions[:settings.capacity]
	difficulty = settings.difficulty
	previous_hash = node.find_last_block_hash()
	block_content = create_block_content(previous_hash, to_be_mined)
		
	nonce = 0
	print("mpika")
	while(True):
		hashed = sha(block_content + str(nonce))
		if correct_block(hashed, difficulty):
			print("New block is mined with success!")
			print("Nonce:", nonce)
			print("Block ID:", hashed)
			print("Binary hash lenght", len(hashed))
				
			# creates the new block that found
			new_block = Block(previous_hash, nonce, to_be_mined)

			return new_block

		try:
			nonce += 1

		except Exception as ex:
			print("nonce reached max value")
			raise ex