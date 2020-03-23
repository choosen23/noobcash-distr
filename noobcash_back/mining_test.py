from Crypto.Hash import SHA
import sys

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

def mining(block, difficulty):

	nonce = 0

	while(True):
		hashed = sha(block + str(nonce))
		if correct_block(hashed, difficulty):
			print("New block is mined with success!")
			print("Nonce:", nonce)
			print("Block ID:", hashed)
			print("Binary hash lenght", len(hashed))

			return hashed

		try:
			nonce += 1
					
		except Exception as ex:
			print("nonce reached max value")
			raise ex



if __name__ == "__main__":
	block = "121212idd7ddddddd\nBob sends to ros 1M\n" #test block to mine
	print("block\n")
	print(block)
	difficulty = 15
	mining(block, difficulty)