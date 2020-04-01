from wallet import rsa_to_string
from wallet import generate_keys

from collections import OrderedDict

import binascii
from Crypto.Signature import PKCS1_v1_5
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import requests
from flask import Flask, jsonify, request, render_template
import wallet
import time
import json
import base64
import hashlib

def sha_hex(text):
	""" Hash the text with SHA encryption
		The output is the hashed text in binary form """

	byte_string = text.encode()
	hashed = SHA.new(byte_string)
	hex_string = hashed.hexdigest()

	return hex_string


class Transaction:

    def __init__(self, sender_address, recipient_address, value, sender_private_key = None, previous_transactions = [], genesis_transaction = False, new_transaction = True):

        
        # The wallet's public key of the sender that contains the money
        if genesis_transaction:
            self.sender_address = sender_address
            self.sender_str = sender_address
        else:
            self.sender_str = rsa_to_string(sender_address)
            self.sender_address = sender_address.exportKey('PEM').decode('utf8')

        # Shows if the transaction is the genesis transaction that is inside the genesis block
        self.isGenesis = genesis_transaction

        # The wallet's public key of the recipient of the money
        self.receiver_address = recipient_address.exportKey('PEM').decode('utf8')

        # The wallet's public key of the recipient of the money
        self.receiver_str = rsa_to_string(recipient_address)
        
        # Checks if the transaction can be done
        self.canBeDone = None

        # The amount that is about to be transfered
        self.amount = value

        # The unique ID of the transaction
        self.transaction_id = None

        # A list of Transaction Input
        self.transaction_input = None

        # A list of Transaction Output
        self.transaction_output = None

        # Text that contains the transaction info, the sender will sign it
        self.to_be_signed = None

        # The transaction with the sender's signature
        self.signature = None

        # Text that contains the transaction info that will be put in the block
        self.text = None

        if new_transaction:

            self.transaction_id = self.calculate_transaction_id()

            if genesis_transaction:
                """ If this is the first transaction of the system that is inside the genesis block """

                first_unspent = {}
                first_unspent['transaction_id'] = self.transaction_id
                first_unspent['wallet_id'] = self.receiver_str
                first_unspent['amount'] = self.amount

                self.transaction_input = []
                self.transaction_output = [first_unspent]

                self.canBeDone = True

                self.text = self.create_transaction_for_signing()

            else:
                self.transaction_input, self.transaction_output = self.calculate_transaction_IO(previous_transactions)

                self.to_be_signed = self.create_transaction_for_signing()

                self.signature = self.sign_transaction(self.to_be_signed, sender_private_key).decode('latin-1')

                self.text = self.to_be_signed + '\nSignature\n' + str(self.signature) + '\n'


    def set_transaction_info(self, transaction_id, signature, to_be_signed, text, transaction_input, transaction_output):
        self.transaction_id = transaction_id
        self.signature = signature.decode('latin-1')
        self.to_be_signed = to_be_signed
        self.text = text
        self.transaction_input = transaction_input
        self.transaction_output = transaction_output

    def set_genesis_transaction_info(self, transaction_id, text, transaction_input, transaction_output):
        self.transaction_id = transaction_id
        self.text = text
        self.transaction_input = transaction_input
        self.transaction_output = transaction_output

    def calculate_transaction_id(self):
        """ Finds a unique id to give to the transaction by combining
            the current time in seconds and the sender's public key """

        current_time = str(time.time()).split('.')
        current_time = current_time[0] + current_time[1]
        unique_num = str(current_time) + self.sender_str
        transaction_id = "TR" + sha_hex(unique_num)

        return(transaction_id)

    def create_transaction_for_signing(self):
        """ Create the string that is about to be signed by the sender """

        text = 'Transaction ID \n'
        text += self.transaction_id + '\n' + '\n'
        text += 'Sender \n'
        text += self.sender_str + '\n'
        text += '\n' + 'pays ' + str(self.amount) + ' NBC to' + '\n' + '\n'
        text += 'Receiver \n'
        text += self.receiver_str + '\n'
       
        return text

    def calculate_transaction_IO(self, prev_transactions):
        """ Finds the UTXOs needed for the transaction
            if there is no enough UTXOs to cover the transaction amount
            the function returns an empty list
            If there is then they are the input transactions
            Also we have 2 output transactions,
            one for sender and one for recipient """

        unspent = [] # contains all the unspent transactions of the sender
        available_amount = 0

        for tr in prev_transactions:
            if tr['wallet_id'] == self.sender_str:
                available_amount += tr['amount']
                unspent.append(tr)

        if available_amount < self.amount:
            """ Sender does not have enough UTXOs
                Transaction cannot be done """

            self.canBeDone = False

            print("Transaction cannot be done due to sender's lack of money")

            return [], []

        sorted_trs = sorted(unspent, key = lambda t : t['amount'])

        input_trs = []
        output_trs = []

        paid = 0
        while (paid < self.amount):
            tr = sorted_trs.pop(0) # utxo will be used for this transaction so it is removes from the list
            input_trs.append(tr) # also this transactions is added to input transactions
            paid += tr['amount']
            if (paid > self.amount):
                change = paid - self.amount

                new_tr = {} # we create a new utxo for sender
                new_tr['transaction_id'] = tr['transaction_id']
                new_tr['wallet_id'] = tr['wallet_id']
                new_tr['amount'] = change

                output_trs.append(new_tr)

        new_tr = {} # we create a new utxo for receiver
        new_tr['transaction_id'] = self.transaction_id
        new_tr['wallet_id'] = self.receiver_str
        new_tr['amount'] = self.amount
        output_trs.append(new_tr)

        self.canBeDone = True

        return input_trs, output_trs


    def sign_transaction(self, message, private_key):
        """ Sign transaction with private key """
        """ We crypto our transaction using private key """

        message = message.encode('utf8')
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(message)
        signature = signer.sign(h)
        
        return signature


if __name__ == "__main__":

    sender, senderpr = generate_keys()
    receiver, _ = generate_keys()

    trs = []
    new_tr = {}
    new_tr['transaction_id'] = "13323232323232"
    new_tr['wallet_id'] = rsa_to_string(sender)
    new_tr['amount'] = 100000
    trs.append(new_tr)

    t = Transaction(sender, receiver, 100, sender_private_key = senderpr, previous_transactions = trs)

    print(t.text)