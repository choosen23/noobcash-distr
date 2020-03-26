import requests
from flask import Flask, jsonify, request, render_template, g
from flask_cors import CORS
import test_node as nd
import json
import netifaces as ni
import settings
import redis
import pickle
# import block
# import node
# import blockchain
# import wallet
# import transaction

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

from Crypto.PublicKey import RSA
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
#blockchain = Blockchain()
bootstrap = None
simple_node = None
r = redis.StrictRedis(host='localhost', port=6379, password='')

@app.route('/init_coordinator', methods=['POST'])
def init_coordinator():
    participants = request.json['participants']
    port = request.json['port']
    ni.ifaddresses('eth1')
    ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']
    coordinator_details={
        'port': port,
        'ip': ip
    }
    global bootstrap
    bootstrap = nd.node(participants,coordinator_details)

    return '',200

@app.route('/init_simple_node', methods=['POST'])
def init_node():
    #generate public/private key
    #send public key to coordinator
    #take the unique id from coordinator
    node_port = request.json['port']
    ni.ifaddresses('eth1')
    node_ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']
    global simple_node
    simple_node = nd.node()
    data = {}
    data['public_key'] = simple_node.wallet.public_key.exportKey('PEM').decode('utf-8')
    data['ip'] = node_ip
    data['port'] = node_port
    response = requests.post(f'http://{settings.COORDINATOR_IP}:{settings.COORDINATOR_PORT}/new_node_came', json=data)
    simple_node.id = response.json()['id']
    return '',200

@app.route('/new_node_came',methods= ['POST'])
def node_details():
    global bootstrap
    bootstrap.current_id_count += 1
    data = request.json
    data['public_key'] =data['public_key'].encode('utf8')
    data['id'] = bootstrap.current_id_count
    bootstrap.ring[bootstrap.current_id_count] = data
    if bootstrap.current_id_count == bootstrap.num_nodes-1:     
        requests.post(f'http://127.0.0.1:{port}/send_list_of_nodes')
    to_send = {
        'id': bootstrap.current_id_count,
        'blockchain': bootstrap.blockchain, # TODO: convert obj to readable
        'unspent_transactions': bootstrap.unspent_transactions
    }
    ## do transaction
    return jsonify(to_send),200

@app.route('/send_list_of_nodes', methods=['POST'])
def send_list_of_nodes():
    global bootstrap
    to_send = []
    for x in range(bootstrap.num_nodes):
        data = bootstrap.ring[x]
        data['public_key'] = data['public_key'].decode('utf8')
        to_send.append(data)
    print(to_send)
    for x in range(bootstrap.num_nodes-1):
        ip = bootstrap.ring[x+1]['ip']
        port = bootstrap.ring[x+1]['port']
        requests.post(f'http://{ip}:{port}/get_list_of_nodes', json=to_send)
    return '',200

@app.route('/get_list_of_nodes', methods=['POST'])
def get_list_of_nodes():
    global simple_node
    to_save = request.json
    for x in to_save:
        x['public_key'] = x['public_key'].encode('utf8')
    simple_node.ring = to_save
    return '',200

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    # given a transaction object
    # import test_node as node
    # node.create_transaction(id->public_key receiver,value)
    # broadcast transaction
    return '',200

@app.route('/accept_and_verify_transaction', methods=['POST'])
def accept_and_verify_transaction():
    # given a transaction in body with json
    # import test_mnode as node
    # node.add_transaction_to_block(transaction object) = True or False
    global bootstrap
    data = request.json
    h = SHA.new(data['message'].encode('utf8'))
    x = bootstrap.ring[1]['public_key']
    pk = RSA.importKey(x)
    verifier = PKCS1_v1_5.new(pk)
    if verifier.verify(h,data['signature'].encode('latin-1')):
        print("true")
    else:
        print("false")
    return '',200

@app.route('/view_last_transactions', methods=['GET'])
def view_last_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/show_balance', methods=['GET'])
def show_balance():
    global bootstrap
    bootstrap.show_wallet_balance()
    return '',200

@app.route('/', methods=['POST'])
def index():
    global simple_node
    print(request.json['message'])
    message = request.json['message'].encode('utf8')
    h = SHA.new(message)
    signer = PKCS1_v1_5.new(simple_node.wallet.private_key)
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

@app.route('/test/bootstrap/check_ring', methods=['GET'])
def test_check_ring_bootstrap():
    global bootstrap
    to_send = bootstrap.ring
    for x in to_send:
        x['public_key'] = x['public_key'].decode('utf8')
    return jsonify(to_send),200

@app.route('/test/simple_node/check_ring', methods=['GET'])
def test_check_ring_simple_node():
    global simple_node
    to_send = simple_node.ring
    for x in to_send:
        x['public_key'] = x['public_key'].decode('utf8')
    return jsonify(to_send),200

@app.route('/test/simple_node/check_id', methods=['GET'])
def test_check_id_simple_node():
    global simple_node
    to_send = {'id':simple_node.id}
    return jsonify(to_send),200

@app.route('/test/bootstrap/check_id', methods=['GET'])
def test_check_id_bootstrap():
    global bootstrap
    to_send = {'id':bootstrap.id}
    return jsonify(to_send),200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on (default:5000')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)