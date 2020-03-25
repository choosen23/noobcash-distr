import requests
import argparse

help_message = '''
Available commands:
* `t <recipient_address> <amount>`   Send `amount` NBC to `recepient`
* `view`                             View transactions of the latest block
* `balance`                          View balance of the wallet (as of last validated block)
* `help`                             Print help message
* `exit`                             Exit client (will not stop server)
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
		continue
	elif cmd == 'test':
		response = requests.post('http://127.0.0.1:5000/', json={
			'participants': 10,
	})
		print(response.json())
		print(type(response.json()))
	elif cmd == 'view':
		print(URL)
	elif cmd == "balance":
		continue
	elif cmd == "help":
		print(help_message)
	elif cmd.startswith('t'):
		args = cmd.split()
	elif cmd == exit:
		exit(-1)
	else:
		print("Uknown Command")
		print(help_message)
