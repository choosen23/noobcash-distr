import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
# import block
# import node
# import blockchain
# import wallet
# import transaction


app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
#blockchain = Blockchain()
*

@app.route('/init_coordinator', methods=['POST'])
def init_coordinator():
    participants = request.json['participants']
    import test_node as node
    node(participants)

    return '',200

@app.route('/init_node', methods=['POST'])
def init_node():
    #generate public/private key
    #send public key to coordinator
    #take the unique id from coordinator
    return '',200

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
    #
    return '',200


# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on (default:5000')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)