import requests
from flask import Flask, jsonify, request, render_template, g
from flask_cors import CORS
import test_node as nd
import json
import netifaces as ni
import settings
import transaction as Transaction
import json

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

from Crypto.PublicKey import RSA
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

node = None

# Use to extract data from ring and decode the keys to send them via json
def copy_list_with_dicts_and_decode(l1): 
    l2 = []
    for d1 in l1:
        d2 = d1.copy()
        if d2:
            d2['public_key'] = d2['public_key'].decode('utf8')
        l2.append(d2)
    return l2

# Use by taking a list of transaction objects and convert it in a list with transactions.__dict__ to send via json 
def create_list_of_dict_transactions(l1):
    l2 = []
    for x in l1:
        l2.append(x.__dict__)
    return l2

# Use by taking a transaction.__dict__ and convert it to a transaction object for further using
def create_transaction_from_dict(l1):
    sender = RSA.importKey(l1['sender_address'].encode('utf8'))
    receiver = RSA.importKey(l1['receiver_address'].encode('utf8'))
    value = l1['amount']
    signature = l1['signature'].encode('latin-1')

    transaction = Transaction.Transaction(sender,receiver,value,new_transaction = False) 
    
    transaction_id = l1['transaction_id']
    to_be_signed = l1['to_be_signed']
    text = l1['text']
    transaction_input = l1['transaction_input']
    transaction_output = l1['transaction_output']

    transaction.set_transaction_info(transaction_id,signature,to_be_signed,text,transaction_input,transaction_output)#keys
    return transaction

#Initializing the coordinator's variables and node
@app.route('/init_coordinator', methods=['POST']) #bootstrap scope | DONE
def init_coordinator():
    participants = request.json['participants']
    port = request.json['port']
    ni.ifaddresses('eth1')
    ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']
    if not ip.startswith('192.'):
        ip = ni.ifaddresses('eth2')[ni.AF_INET][0]['addr']


    coordinator_details={
        'port': port,
        'ip': ip
    }
    global node
    node = nd.node( num_nodes = participants,coordinator = coordinator_details)

    return '',200
# Initializing a simple node of the network and it's variables
@app.route('/init_simple_node', methods=['POST']) #simple node scope | DONE
def init_node():

    port = request.json['port']
    ni.ifaddresses('eth1')
    ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']
    if not ip.startswith('192.'):
        ip = ni.ifaddresses('eth2')[ni.AF_INET][0]['addr']

    global node
    node = nd.node()
    
    #Send simple node's information to boostrap node
    data = {}
    data['public_key'] = node.wallet.public_key.exportKey('PEM').decode('utf-8')
    data['ip'] = ip
    data['port'] = port
    
    response = requests.post(f'http://{settings.COORDINATOR_IP}:{settings.COORDINATOR_PORT}/new_node_came', json=data)
    node.id = response.json()['id']
    return '',200

# Do the essentials after a node is being connected to the network
@app.route('/new_node_came',methods= ['POST']) # bootstrap scope
def node_details():
    
    # Refresh the ring which contains infos for all nodes in network
    global node
    node.current_id_count += 1
    data = request.json
    data['public_key'] = data['public_key'].encode('utf8')
    data['id'] = node.current_id_count
    node.ring[node.current_id_count] = data
    
    # Inform the upcoming node for previous open transactions of the network that bootstrap has
    list_of_open_transactions = create_list_of_dict_transactions(node.open_transactions)
    
    to_send = {}
    to_send['open_transactions'] = list_of_open_transactions
    to_send['unspent_transactions'] = node.unspent_transactions
    ip = node.ring[node.current_id_count]['ip']
    port = node.ring[node.current_id_count]['port']
    requests.post(f'http://{ip}:{port}/open_transactions', json=to_send)
    
    # Do the initial transaction to the upcoming node bu giving 100 NBC
    receiver_key_PEM = node.ring[node.current_id_count]['public_key']
    receiver_key = RSA.importKey(receiver_key_PEM)
    value = 100
    
    transaction = node.create_transaction(receiver_key,value)
    if transaction.canBeDone: # TODO
        node.add_transaction_to_block(transaction) # returns none if not mining, or the mining block

    # Broadcast the transaction to all existing nodes in the network
    to_send = transaction.__dict__
    
    # print(to_send)
    # print(type(to_send))
    # to_send_json = json.dumps(to_send)
    # print(to_send_json)
    # print(type(to_send_json))

    for x in range(node.current_id_count):
        ip = node.ring[x+1]['ip']
        port = node.ring[x+1]['port']
        requests.post(f'http://{ip}:{port}/accept_and_verify_transaction', json=to_send)

    # If all nodes are connected then send to all the network informations that are stored in bootstrap's ring
    if node.current_id_count == node.num_nodes-1:
        port = node.ring[0]['port']     
        requests.post(f'http://127.0.0.1:{port}/send_list_of_nodes')
    
    #for each node send the details
    # to_send = {
    #     'id': node.current_id_count,
    #     'blockchain': node.blockchain, # TODO: convert obj to readable
    #     'unspent_transactions': node.unspent_transactions
    # }
    
    # Finally return the id of the node connected
    to_send = {'id' :  node.current_id_count}
    return jsonify(to_send),200

# Taking the history of open and unpsent transactions from bootstrap
@app.route('/open_transactions', methods = ['POST']) # simple node scope
def open_transactions():
    
    global node
    open_transactions_dict = request.json['open_transactions']
    
    open_transactions=[]
    for x in open_transactions_dict:
        open_transactions.append(create_transaction_from_dict(x))
    
    unspent_transactions = request.json['unspent_transactions'] 
    node.unspent_transactions = unspent_transactions
    node.open_transactions = open_transactions
    return '',200

# After all nodes have connected to the network inform all nodes of the network about the network
@app.route('/send_list_of_nodes', methods=['POST']) #bootstrap scope | DONE
def send_list_of_nodes():
    global node
    to_send = copy_list_with_dicts_and_decode(node.ring)
    for x in range(node.num_nodes-1):
        ip = node.ring[x+1]['ip']
        port = node.ring[x+1]['port']
        requests.post(f'http://{ip}:{port}/get_list_of_nodes', json=to_send)
    return '',200

# Create each node's ring that holds the network infos 
@app.route('/get_list_of_nodes', methods=['POST']) #simple node scope |  DONE
def get_list_of_nodes():
    global node
    to_save = request.json
    for x in to_save:
        x['public_key'] = x['public_key'].encode('utf8')
    node.ring = to_save
    return '',200

# Creating a new transaction
@app.route('/new_transaction', methods=['POST']) #all scope
def new_transaction():
    global node
    response = request.json
    value = int(response['amount'])
    receiver_id = int(response['id'])
    
    #Create transaction
    receiver_key = RSA.importKey(node.ring[receiver_id]['public_key'])
    transaction = node.create_transaction(receiver_key,value)
    if transaction.canBeDone == False:
        return '',500
    node.add_transaction_to_block(transaction)

    #Broadcast to the network
    to_send = transaction.__dict__
    for x in range(len(node.ring)):
        if x == node.id:
            continue
        ip = node.ring[x]['ip']
        port = node.ring[x]['port']
        requests.post(f'http://{ip}:{port}/accept_and_verify_transaction', json=to_send)
    
    return '',200

# Taking a transaction, verify it and add it to the block
@app.route('/accept_and_verify_transaction', methods=['POST']) #all scope
def accept_and_verify_transaction():
    global node 

    response = request.json
    print(response)

    sender = RSA.importKey(response['sender_address'].encode('utf8'))
    receiver = RSA.importKey(response['receiver_address'].encode('utf8'))
    value = response['amount']
    signature = response['signature'].encode('latin-1')

    transaction = Transaction.Transaction(sender,receiver,value,new_transaction = False) #check keys
    
    transaction_id = response['transaction_id']
    to_be_signed = response['to_be_signed']
    text = response['text']
    transaction_input = response['transaction_input']
    transaction_output = response['transaction_output']

    transaction.set_transaction_info(transaction_id,signature,to_be_signed,text,transaction_input,transaction_output)#keys
    # is_valid = node.validate_transaction(transaction)
    # if is_valid:
    #     print('Transaction is valid')
    # else:
    #     print('is Not Valid')  
    node.add_transaction_to_block(transaction)
    return '',200

# View the transactions of last blockchain's block
@app.route('/view_last_transactions', methods=['GET'])
def view_last_transactions():
    global node
    last_block = node.blockchain[-1]
    print(type(last_block))
    return '',200

# Show the balance of node's wallet
@app.route('/show_balance', methods=['GET'])
def show_balance():
    global node
    to_send = {
        'balance' : node.wallet_balance()
    }
    return jsonify(to_send),200

@app.route('/', methods=['POST'])
def index():
    global node
    print(request.json['message'])
    message = request.json['message'].encode('utf8')
    h = SHA.new(message)
    signer = PKCS1_v1_5.new(node.wallet.private_key)
    signature = signer.sign(h)
    decoded_signature = signature.decode('latin-1')
    data = {
        'message': request.json['message'],
        'signature': decoded_signature
    }
    print('hi')
    response = requests.post(f'http://{settings.COORDINATOR_IP}:{settings.COORDINATOR_PORT}/accept_and_verify_transaction', json=data)
    return '',200


#=======================================================
#		FOR DEVELOPERS
#=======================================================

# Check the ring of the node
@app.route('/test/check_ring', methods=['GET'])
def test_check_ring():
    params = request.args.get('id')
    global node
    if node.ring:    
        to_send = copy_list_with_dicts_and_decode(node.ring)
        return jsonify(to_send),200
    else: 
        return '',500

# Check the id of the node
@app.route('/test/check_id', methods=['GET'])
def test_check_id_node():
    params = request.args.get('id')
    global node
    to_send = {'id':node.id}
    return jsonify(to_send),200

# Check the open transactions of the node
@app.route('/test/open_transactions', methods=['GET'])
def test_open_transactions():
    global node
    to_send = []
    for x in node.open_transactions:
        to_send.append(x.__dict__)
    return jsonify(to_send),200
    return '',200

# Check the unspent transaction of the node
@app.route('/test/unspent_transactions', methods=['GET'])
def test_unspent_transactions():
    global node
    return jsonify(node.unspent_transactions),200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on (default:5000')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)