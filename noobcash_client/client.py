import requests
import argparse
import time
help_message = '''
Available commands:
* `t <recipient_address> <amount>`   Send `amount` NBC to `recepient`
* `view`                             View transactions of the latest block
* `balance`                          View balance of the wallet (as of last validated block)
* `help`                             Print help message
* `exit`                             Exit client (will not stop server)
==============================================================================================
FOR DEVELOPERS
==============================================================================================
*`check id`                          View the id of this node
*`check ring`                        View the dictionary with details of other nodes
*`check open_transactions`           View the open transactions
*`check unspent_transactions`        View the unspent transactions
'''
parser = argparse.ArgumentParser()

parser.add_argument('port', help='port of the backend process', type=int)
parser.add_argument('-n', help='Init as coordinator, for N partipipants', type=int)
args = parser.parse_args()
# initialize the node depends on his nature
PARTICIPANTS = args.n
PARAMS = { 'id': 'bootstrap'} if PARTICIPANTS else {'id': 'single_node'}
connection_URL = f'http://127.0.0.1:{args.port}/init_coordinator' if PARTICIPANTS else f'http://127.0.0.1:{args.port}/init_simple_node'

try:
	response = requests.post(connection_URL, json={
		'participants': PARTICIPANTS,
		'port' : args.port
	})
	assert response.status_code == 200

	my_id = response.json()
	print(my_id)
except Exception as e:
    print(f'Could not connect to backend service (probably false port): {e.__class__.__name__}: {e}')
    exit(-1)

while True:
	cmd = input("> ")
	# Check wallet's balance
	if cmd == 'balance':
		response = requests.get(f'http://127.0.0.1:{args.port}/show_balance')
		print(str(response.json()['balance']) + ' NBC')
	elif cmd == 'test':
		count = 0 
		f = open(f"../transactions/5nodes/transactions{my_id}.txt", "r")
		for x in f:
			line = x.split()
			receiver = line[0].split('d')[1]
			amount = line[1]
			to_send = {
			'id': receiver,
			'amount': amount
			}
			print("******Transactions*****")
			print("send to id:",receiver,"the amount:",amount)
			response = requests.post(f'http://127.0.0.1:{args.port}/new_transaction',json= to_send)
			if response.status_code == 200:
				print("Transaction is done!")
			elif response.status_code == 500:
				print("ERROR!")
				print("Transaction cannot be Done because you don't have enough money")
			time.sleep(4)
			count += 1
			if count == 20:
				break
		continue
	# View the transactions of last blockchain's block
	elif cmd == 'view': 
		response = requests.get(f'http://127.0.0.1:{args.port}/view_last_transactions')
		print(response.json())
	# Print the help message of available commands
	elif cmd == "help":
		print(help_message)
	# Create a new transaction: t <recipient's id> <amount>
	elif cmd.startswith('t'):
		data = cmd.split()
		to_send = {
			'id': data[1],
			'amount': data[2]
		}
		response = requests.post(f'http://127.0.0.1:{args.port}/new_transaction',json= to_send)
		if response.status_code == 200:
			print("Transaction is done!")
		elif response.status_code == 500:
			print("ERROR!")
			print("Transaction cannot be Done because you don't have enough money")
	elif cmd == 'exit':
		exit(-1)
	elif cmd == exit:
		exit(-1)
	#=======================================================
	#		FOR DEVELOPERS
	#=======================================================

	# Check the ring of the node
	elif cmd == "check ring":
		response = requests.get(f'http://127.0.0.1:{args.port}/test/check_ring', params = PARAMS)
		if response.status_code == 500:
			print('ERROR, not all nodes registered in the network')
			continue
		res = response.json()
		to_show = []
		for x in res:
			print(x) 
	# Check the open transactions of the node
	elif cmd == 'check open_transactions': 
		response = requests.get(f'http://127.0.0.1:{args.port}/test/open_transactions')
		for x in response.json():
			print(x)
	# Check the unspent transaction of the node
	elif cmd == 'check unspent_transactions': 
		response = requests.get(f'http://127.0.0.1:{args.port}/test/unspent_transactions')
		print(response.json())
	# Check the id of the node
	elif cmd == "check id":
		response = requests.get(f'http://127.0.0.1:{args.port}/test/check_id', params = PARAMS)
		res = response.json()
		#print('Your id is', res['id'])
		print(id)
	elif cmd == 'check blockchain':
		response = requests.get(f'http://127.0.0.1:{args.port}/test/blockchain')
	# If command is uknown print the help message
	else:
		print("Uknown Command")
		print(help_message)
