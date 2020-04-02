import requests
from flask import Flask, jsonify, request, render_template, g
from flask_cors import CORS
import node as nd
import json
import netifaces as ni
import settings
import params
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
task = None
i_am_mining = False
logger = get_task_logger(__name__)

# CELERY_ROUTES = {
#     'core.tasks.too_long_task': {'queue': 'too_long_queue'},
#     'core.tasks.quick_task': {'queue': 'quick_queue'},
# }

@celery.task(name = 'rest.mine')
def mine(block_content):
    logger.info("Starting mining in background")
    nonce = mining.mine_block(block_content)
    print('I mined')
    requests.post(f'http://127.0.0.1:5000/mined_block', json = nonce)
    return nonce
    #do mining

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
    receiver = RSA.importKey(l1['receiver_address'].encode('utf8'))
    value = l1['amount']
    transaction_id = l1['transaction_id']
    text = l1['text']
    transaction_input = l1['transaction_input']
    transaction_output = l1['transaction_output']
    isGenesis = l1['isGenesis']
    if l1['isGenesis'] == False:
        sender = RSA.importKey(l1['sender_address'].encode('utf8'))
        signature = l1['signature'].encode('latin-1')
        to_be_signed = l1['to_be_signed']
        transaction = Transaction.Transaction(sender,receiver,value, genesis_transaction = isGenesis, new_transaction = False) 

        transaction.set_transaction_info(transaction_id,signature,to_be_signed,text,transaction_input,transaction_output)#keys
    else:
        sender = l1['sender_address']
        receiver = RSA.importKey(l1['receiver_address'].encode('utf8'))

        transaction = Transaction.Transaction(sender,receiver,value, genesis_transaction = isGenesis, new_transaction = False)
        transaction.set_genesis_transaction_info(transaction_id,text,transaction_input,transaction_output)
    return transaction

def create_blockchain_to_dict(l1):
    l2 = []
    for x in l1:
        y = x.__dict__
        d = y.copy()
        for i in d:
            if i == 'listOfTransactions':
                d[i] = create_list_of_dict_transactions(d[i])
        l2.append(d)
    return l2

def create_block_to_dict(b):
    y = b.__dict__
    d = y.copy()
    for i in d:
        if i == 'listOfTransactions':
            d[i] = create_list_of_dict_transactions(d[i])
    return d

def start_mining():
    print('node is ready to mine')
    global node
    global i_am_mining
    block_content, previous_hash, to_be_mined = mining.mining_content(node)
    node.new_previous_hash = previous_hash
    node.new_to_be_mined = to_be_mined
    #print(node.new_previous_hash)
    #print(f'{block_content}\n{previous_hash}\n{to_be_mined}')
    global task
    i_am_mining = True
    task = mine.delay(block_content)

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
    return str(node.id),200

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
    
     
    res = node.add_transaction_to_block(transaction) # returns none if not mining, or the mining block
    #print(transaction.transaction_input)
    global i_am_mining
    if res == 'mine' and i_am_mining == False:
        start_mining()
    
    # Broadcast the transaction to all existing nodes in the network
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
        real_capacity = params.getCapacity()
        params.changeCapacity(node.num_nodes-1)
        start_mining()

        params.changeCapacity(real_capacity)
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

@app.route('/give_blockchain', methods = ['GET']) # simple node scope
def give_blockchain():
    global node
    blockchain = create_blockchain_to_dict(node.blockchain)
    # node.show_blockchain()
    return jsonify(blockchain),200


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
    print(transaction.canBeDone)
    if transaction.canBeDone == False:
        return '',500
    
    res = node.add_transaction_to_block(transaction) # returns none if not mining, or the mining block
    #print(transaction.transaction_input)

    global i_am_mining
    if res == 'mine' and i_am_mining == False:
        start_mining()
    
    #Broadcast to the network
    to_send = transaction.__dict__
    for x in range(node.ring):
        if x == node.id:
            continue
        ip = node.ring[x]['ip']
        port = node.ring[x]['port']
        requests.post(f'http://{ip}:{port}/accept_and_verify_transaction', json=to_send)
    
    return '',200

# Taking a transaction, verify it and add it to the block
@app.route('/accept_and_verify_transaction', methods=['POST' , 'GET']) #all scope
def accept_and_verify_transaction():
    # given a transaction in body with json
    # import test_mnode as node
    # node.add_transaction_to_block(transaction object) = True or False
    global node 
    print("a new transaction came")
    response = request.json
    #print(response)
    # global task
    # if task:
    #     print('Stop mining cause a new block came')
    #     task.revoke(terminate = True,signal='SIGKILL')
    
    transaction = create_transaction_from_dict(response)
    # is_valid = node.validate_transaction(transaction)
    # if is_valid:
    #     print('Transaction is valid')
    # else:
    #     print('is Not Valid')  
    res = node.add_transaction_to_block(transaction) # returns none if not mining, or the mining block
    #print(transaction.transaction_input)
    global i_am_mining
    if res == 'mine' and i_am_mining == False and node.ring:
        start_mining()
    return '',200

@app.route('/view_last_transactions', methods=['GET'])
def view_last_transactions():
    global node
    last_block = node.blockchain[-1]
    to_send = str(last_block,node)
    return jsonify(to_send),200


@app.route('/show_balance', methods=['GET'])
def show_balance():
    global node
    to_send = {
        'balance' : node.wallet_balance()
    }
    return jsonify(to_send),200

@app.route('/', methods=['POST'])
def index():
    global task
    task.revoke(terminate = True,signal='SIGKILL')
    return '',200

@app.route('/mined_block', methods=['POST'])
def mined_block():
    from datetime import datetime
    print(str(datetime.now()),"mined_block called")
    global i_am_mining
    global node
    nonce = request.json
    new_block = mining.create_mined_block(node.new_previous_hash, nonce, node.new_to_be_mined)
    node.add_block_to_chain(new_block)
    
    i_am_mining = False
    to_send = create_block_to_dict(new_block)
    for x in node.ring:
        if x and x['id'] != node.id:
            ip = x['ip']
            port = x['port']
            requests.post(f'http://{ip}:{port}/accept_and_verify_block', json=to_send)
    if len(node.open_transactions) >= params.getCapacity():
        start_mining()
    return '',200

@app.route('/accept_and_verify_block', methods=['POST'])
def accept_and_verify_block():
    global node
    global i_am_mining
    if i_am_mining and task:

        print('A new block came and i kill the task')
        print('Stop mining cause a new block came')
        task.revoke(terminate = True,signal='SIGKILL')
        i_am_mining = False

    b = request.json
    previous_hash = b['previousHash']
    timestamp = b['timestamp']
    nonce = b['nonce']
    listOfTransactions = []
    for y in b['listOfTransactions']:
        listOfTransactions.append(create_transaction_from_dict(y))
    block_hash = b['hash']
    genesis = b['genesis']
    new_block = Block(previous_hash,nonce,listOfTransactions,genesis = genesis,new_block= False)
    new_block.set_hash(block_hash)
    from datetime import datetime
    res = node.block_placement(new_block)
    print(str(datetime.now()),"RES from block placement is: ", res)
    if res == "OK":
        print('OKKK RRRRRRRRR')
        if node.valid_proof(new_block):
            if node.add_block_to_chain(new_block):
                print('I accepted the block')
            else:
                print('i didnt add it')
        else:
            print('Sorry easy money')
    elif res == 'consensus':
        print('Consensus')
        all_blockchain = []
        for x in node.ring:
            if x and x['id'] != node.id:
                ip = x['ip']
                port = x['port']
                res = requests.get(f'http://{ip}:{port}/give_blockchain')
                new_blockchain = [] # TODO the function 
                for b in res.json():
                    previous_hash = b['previousHash']
                    timestamp = b['timestamp']
                    nonce = b['nonce']
                    listOfTransactions = []
                    for y in b['listOfTransactions']:
                        listOfTransactions.append(create_transaction_from_dict(y))
                    block_hash = b['hash']
                    genesis = b['genesis']
                    new_block = Block(previous_hash,nonce,listOfTransactions,genesis = genesis,new_block= False)
                    new_block.set_hash(block_hash)
                    new_blockchain.append(new_block)
                all_blockchain.append(new_blockchain)
        node.valid_chain(all_blockchain)
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