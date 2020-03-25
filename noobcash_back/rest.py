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
    print(type(simple_node.wallet.public_key.exportKey('PEM')))
    data['public_key'] = simple_node.wallet.public_key.exportKey('PEM').decode('utf-8')
    data['ip'] = node_ip
    data['port'] = node_port
    response = requests.post(f'http://{settings.COORDINATOR_IP}:{settings.COORDINATOR_PORT}/single_node_details', json=data)
    simple_node.id = response.json()['id']
    print(simple_node.id)
    return '',200

@app.route('/single_node_details',methods= ['POST'])
def node_details():
    global bootstrap
    bootstrap.current_id_count += 1
    data = request.json
    data['public_key'] =data['public_key'].encode('utf8')
    bootstrap.ring[bootstrap.current_id_count] = data
    return {'id': bootstrap.current_id_count},200

@app.route('/send_list_of_nodes', methods=['POST'])
def send_list_of_nodes():
    #send list of nodes
    return '',200

@app.route('/get_list_of_nodes', methods=['GET'])
def get_list_of_nodes():
    #get list of nodes
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
    #
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
    response = requests.post(f'http://{settings.COORDINATOR_IP}:{settings.COORDINATOR_PORT}/accept_and_verify_transaction', json=data)
    return '',200


# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on (default:5000')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)