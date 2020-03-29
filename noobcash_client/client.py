import requests
import argparse

help_message = '''
Available commands:
* `t <recipient_address> <amount>`   Send `amount` NBC to `recepient`
* `view`                             View transactions of the latest block
* `balance`                          View balance of the wallet (as of last validated block)
* `help`                             Print help message
* `exit`                             Exit client (will not stop server)
==============================================================================================
FOR DEVELOPERS
===============================================================================================
*`check id`				See the id of this node
*`check ring`			See the dictionary with details of other nodes
'''
parser = argparse.ArgumentParser()

parser.add_argument('port', help='port of the backend process', type=int)
parser.add_argument('-n', help='Init as coordinator, for N partipipants', type=int)
args = parser.parse_args()


PARTICIPANTS = args.n
PARAMS = { 'id': 'bootstrap'} if PARTICIPANTS else {'id': 'single_node'}
connection_URL = f'http://127.0.0.1:{args.port}/init_coordinator' if PARTICIPANTS else f'http://127.0.0.1:{args.port}/init_simple_node'

try:
	response = requests.post(connection_URL, json={
		'participants': PARTICIPANTS,
		'port' : args.port
	})
	assert response.status_code == 200
except Exception as e:
    print(f'Could not connect to backend service (probably false port): {e.__class__.__name__}: {e}')
    exit(-1)

while True:
	cmd = input("> ")
	#print(cmd)
	if cmd == 'balance':
		response = requests.get(f'http://127.0.0.1:{args.port}/show_balance')
		print(str(response.json()['balance']) + ' NBC')
	elif cmd == 'test':
		response = requests.post(f'http://127.0.0.1:{args.port}/',json={'message':'a simple message'})
		print("nice")
	elif cmd == 'view':
		continue  
	elif cmd == "help":
		print(help_message)
	elif cmd.startswith('t'):
		data = cmd.split()
		to_send = {
			'id': data[1],
			'amount': data[2]
		}
		response = requests.post(f'http://127.0.0.1:{args.port}/new_transaction',json= to_send)
		if response.status_code == 200:
			print("Transaction is done!")
	elif cmd == 'exit':
		exit(-1)
	elif cmd == exit:
		exit(-1)
	#=======================================================
	#		FOR DEVELOPERS
	#=======================================================
	elif cmd == "check ring":
		response = requests.get(f'http://127.0.0.1:{args.port}/test/check_ring', params = PARAMS)
		if response.status_code == 500:
			print('ERROR, not all nodes registered in the network')
			continue
		res = response.json()
		to_show = []
		for x in res:
			print(x) 
		

	elif cmd == "check id":
		response = requests.get(f'http://127.0.0.1:{args.port}/test/check_id', params = PARAMS)
		res = response.json()
		print('Your id is', res['id'])

	else:
		print("Uknown Command")
		print(help_message)
