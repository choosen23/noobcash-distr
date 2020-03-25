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

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value, prev_transactions):

        # The wallet's public key of the sender that contains the money
        self.sender_address = sender_address

        # The wallet's public key of the recipient of the money
        self.receiver_address = recipient_address

        # Checks if the transaction can be done
        self.canBeDone = None

        # The amount that is about to be transfered
        self.amount = value

        # The unique ID of the transaction
        self.transaction_id = self.calculate_transaction_id()

        # A list of Transaction Input
        self.transaction_inputs = prev_transactions

        # A list of Transaction Output
        self.transaction_outputs = self.calculate_transaction_outputs()

        # Text that contains the transaction info
        self.text = self.create_transaction_text()

        # The transaction with the sender's signature
        self.signature = self.sign_transaction(sender_private_key)




    def calculate_transaction_id(self):
        """ Finds a unique id to give to the transaction by combining
            the current time in seconds and the sender's public key """

        current_time = str(time.time()).split('.')
        current_time = current_time[0] + current_time[1]
        transaction_id = "TR" + str(current_time) + rsa_to_string(self.sender_address)

        return(transaction_id)

    def create_transaction_text(self):
        sender = rsa_to_string(self.sender_address)
        receiver = rsa_to_string(self.receiver_address)

        text = 'Transaction ID: ' + self.transaction_id + '\n' + '\n'
        text += sender + '\n'
        text += '\n' + 'pays ' + str(self.amount) + ' NBC to' + '\n' + '\n'
        text += receiver + '\n'
       
        return text

    def calculate_transaction_outputs(self):
        """ Finds the UTXOs needed for the transaction
            if there is no enough UTXOs to cover the transaction amount
            the function returns an empty list
            if there is, then it returns 2 output UTXOs,
            one for sender and one for recipient """

        unspent = [] # contains all the unspent transactions of the sender
        available_amount = 0

        for tr in self.transaction_inputs:
            if tr['wallet_id'] == self.sender_address and tr['type'] == 'UTXO':
                available_amount += tr['amount']
                unspent.append(tr)

        if available_amount < self.amount:
            """ Transaction cannot be done """

            self.canBeDone = False

            return []

        sorted_trs = sorted(unspent, key = lambda t : t['amount'])

        output_trs = []

        paid = 0
        while (paid < self.amount):
            tr = sorted_trs.pop(0) # utxo will be used for this transaction so it is removes from the list
            paid += tr['amount']
            if (paid > self.amount):
                change = paid - self.amount

                tr['amount'] = change # change the amount of this transaction to the change of the current payment of sender
                output_trs.append(tr)

        new_tr = {} # we create a new utxo for receiver
        new_tr['transaction_id'] = self.transaction_id
        new_tr['wallet_id'] = self.receiver_address
        new_tr['type'] = 'UTXO'
        new_tr['amount'] = self.amount
        output_trs.append(new_tr)

        self.canBeDone = True

        self.transaction_inputs = sorted_trs

        return output_trs


    def sign_transaction(self, private_key):
        """ Sign transaction with private key """
        """ We crypto our transaction using private key """

        message = self.text.encode('utf8')
        signer = PKCS1_v1_5.new(private_key)
        signature = signer.sign(message)
        return signature


if __name__ == "__main__":

    sender, senderpr = generate_keys()
    receiver, _ = generate_keys()

    trs = []
    new_tr = {}
    new_tr['transaction_id'] = "13323232323232"
    new_tr['wallet_id'] = sender
    new_tr['type'] = 'UTXO'
    new_tr['amount'] = 100000
    trs.append(new_tr)

    t = Transaction(sender, senderpr, receiver, 100, trs)

    print(t.text)
