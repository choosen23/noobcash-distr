import requests
from flask import Flask, jsonify, request, render_template, g
from flask_cors import CORS
import test_node as nd
import json
import netifaces as ni
import settings
# import block
# import node
# import blockchain
# import wallet
import transaction as Transaction
import json

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

from Crypto.PublicKey import RSA
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

node = None

def copy_list_with_dicts_and_decode(l1):
    l2 = []
    for d1 in l1:
        d2 = d1.copy()
        if d2:
            d2['public_key'] = d2['public_key'].decode('utf8')
        l2.append(d2)
    return l2

@app.route('/init_coordinator', methods=['POST']) #bootstrap DONE
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
    node = nd.node(participants,coordinator_details)

    return '',200

@app.route('/init_simple_node', methods=['POST']) #simple node DONE
def init_node():

    port = request.json['port']
    ni.ifaddresses('eth1')
    ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']
    if not ip.startswith('192.'):
        ip = ni.ifaddresses('eth2')[ni.AF_INET][0]['addr']

    global node
    node = nd.node()
    data = {}
    data['public_key'] = node.wallet.public_key.exportKey('PEM').decode('utf-8')
    data['ip'] = ip
    data['port'] = port
    response = requests.post(f'http://{settings.COORDINATOR_IP}:{settings.COORDINATOR_PORT}/new_node_came', json=data)
    node.id = response.json()['id']
    return '',200

@app.route('/new_node_came',methods= ['POST']) # bootstrap
def node_details():
    global node
    node.current_id_count += 1
    data = request.json
    data['public_key'] = data['public_key'].encode('utf8')
    data['id'] = node.current_id_count
    node.ring[node.current_id_count] = data

    # send_to_new_node(node.open_transactions)
    
    #do transaction
    receiver_key_PEM = node.ring[node.current_id_count]['public_key']
    receiver_key = RSA.importKey(receiver_key_PEM)
    value = 100
    transaction = node.create_transaction(receiver_key,value)

    # node.add_transaction_to_block(transaction)

    to_send = transaction.__dict__
    
    print(to_send)
    # print(type(to_send))
    # to_send_json = json.dumps(to_send)
    # print(to_send_json)
    # print(type(to_send_json))

    for x in range(node.current_id_count):
         ip = node.ring[x+1]['ip']
         port = node.ring[x+1]['port']
         requests.post(f'http://{ip}:{port}/accept_and_verify_transaction', json=to_send)

    # If all nodes are connected
    if node.current_id_count == node.num_nodes-1:
        port = node.ring[0]['port']
        requests.post(f'http://127.0.0.1:{port}/send_list_of_nodes')
    
    #for each node send the details
    # to_send = {
    #     'id': node.current_id_count,
    #     'blockchain': node.blockchain, # TODO: convert obj to readable
    #     'unspent_transactions': node.unspent_transactions
    # }
    
    to_send = {'id' :  node.current_id_count}
    return jsonify(to_send),200

@app.route('/send_list_of_nodes', methods=['POST']) #bootstrap DONE
def send_list_of_nodes():
    global node
    to_send = copy_list_with_dicts_and_decode(node.ring)
    for x in range(node.num_nodes-1):
        ip = node.ring[x+1]['ip']
        port = node.ring[x+1]['port']
        requests.post(f'http://{ip}:{port}/get_list_of_nodes', json=to_send)
    return '',200

@app.route('/get_list_of_nodes', methods=['POST']) #simple_node  DONE
def get_list_of_nodes():
    global node
    to_save = request.json
    for x in to_save:
        x['public_key'] = x['public_key'].encode('utf8')
    node.ring = to_save
    return '',200

@app.route('/new_transaction', methods=['POST']) #all 
def new_transaction():
    # given a transaction object
    # import test_node as node
    # node.create_transaction(id->public_key receiver,value)
    # broadcast transaction
    global node
    response = request.json
    value = int(response['amount'])
    receiver_id = int(response['id'])
    print(type(value),type(receiver_id))
    receiver_key = RSA.importKey(node.ring[receiver_id]['public_key'])
    transaction = node.create_transaction(receiver_key,value)
    
    to_send = transaction.__dict__
    for x in range(node.ring):
        if x == node.id:
            continue
        ip = node.ring[x]['ip']
        port = node.ring[x]['port']
        requests.post(f'http://{ip}:{port}/accept_and_verify_transaction', json=to_send)
    
    return '',200

@app.route('/accept_and_verify_transaction', methods=['POST']) #all
def accept_and_verify_transaction():
    # given a transaction in body with json
    # import test_mnode as node
    # node.add_transaction_to_block(transaction object) = True or False
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
    # transaction is a transaction object to be modified

    transaction.set_transaction_info(transaction_id,signature,to_be_signed,text,transaction_input,transaction_output)#keys
    is_valid = node.validate_transaction(transaction)
    if is_valid:
        print('Transaction is valid')
    else:
        print('is Not Valid')   
    # node.add_transaction_to_block(transaction)
    
    return '',200

@app.route('/view_last_transactions', methods=['GET'])
def view_last_transactions():
    return '',200


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

@app.route('/test/check_ring', methods=['GET'])
def test_check_ring():
    params = request.args.get('id')
    global node
    if node.ring:    
        to_send = copy_list_with_dicts_and_decode(node.ring)
        return jsonify(to_send),200
    else: 
        return '',500

@app.route('/test/check_id', methods=['GET'])
def test_check_id_node():
    params = request.args.get('id')
    global node
    to_send = {'id':node.id}
    return jsonify(to_send),200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on (default:5000')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)