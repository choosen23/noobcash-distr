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
*`check id`							 See the id of this node
*`check ring`						 See the dictionary with details of other nodes
'''
parser = argparse.ArgumentParser()
parser.add_argument('port', help='port of the backend process', type=int)
parser.add_argument('-n', help='Init as coordinator, for N partipipants', type=int)
args = parser.parse_args()

PARTICIPANTS = args.n
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
		print('mpika')
		response = requests.get(f'http://127.0.0.1:{args.port}/show_balance')
	elif cmd == 'test':
		response = requests.post(f'http://127.0.0.1:{args.port}/',json={'message':'a simple message'})
		print("nice")
	elif cmd == 'view':
		continue  
	elif cmd == "help":
		print(help_message)
	elif cmd.startswith('t'):
		args = cmd.split()
	elif cmd == 'exit':
		exit(-1)
	elif cmd == exit:
		exit(-1)
	#=======================================================
	#		FOR DEVELOPERS
	#=======================================================
	elif cmd == "check ring" and PARTICIPANTS:
		response = requests.get(f'http://127.0.0.1:{args.port}/test/bootstrap/check_ring')
		res = response.json()
		to_show = []
		for x in res:
			x['public_key']=x['public_key'].encode('utf8')
		print(res)
		continue
	elif cmd == "check ring":
		response = requests.get(f'http://127.0.0.1:{args.port}/test/simple_node/check_ring')
		res = response.json()
		to_show = []
		for x in res:
			x['public_key']=x['public_key'].encode('utf8')
		print(res)	
	elif cmd == "check id":
		response = requests.get(f'http://127.0.0.1:{args.port}/test/check_id')

	else:
		print("Uknown Command")
		print(help_message)
