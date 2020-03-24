from collections import OrderedDict

import binascii

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



def encrypt_message(a_message, key):
    encryptor = PKCS1_OAEP.new(key)
    encrypted = encryptor.encrypt(bytes(a_message, "utf8"))
    # base64 encoded strings are database friendly
    encoded_encrypted_msg = base64.b64encode(encrypted)
    return encoded_encrypted_msg


class Transaction:
    def __init__(self, sender_address, sender_private_key, recipient_address, value, prev_transactions):

        ##set

        ##############################################
        #ONLY FOR DEBUG
        print()
        print("previous transactions")
        for t in prev_transactions:
            print(t)
        print()
        ##############################################

        # The wallet's public key of the sender that contains the money
        self.sender_address = sender_address

        # The wallet's public key of the recipient of the money
        self.receiver_address = recipient_address

        # Checks if the transaction can be done
        self.canBeDone = None

        # The amount that is about to be transfered
        self.amount = value

        # Text that contains the transaction info
        self.text = self.sender_address + ' pays ' + str(self.amount) + ' NBC to ' + self.receiver_address

        # The unique ID of the transaction
        self.transaction_id = self.calculate_transaction_id()

        # A list of Transaction Input
        self.transaction_inputs = prev_transactions

        # A list of Transaction Output
        self.transaction_outputs = self.calculate_transaction_outputs()

        # The transaction with the sender's signature
        self.signature = self.sign_transaction(sender_private_key)


        ##############################################
        #ONLY FOR DEBUG
        print("sender public key:", self.sender_address, "private key:", sender_private_key)
        print("recipient:", self.receiver_address)
        print("amount:", self.amount)
        print()
        print("Transaction ID:", self.transaction_id)
        print()
        print("signature:", self.signature)
        print("new input transactions")
        for t in self.transaction_inputs:
            print(t)
        print()
        print("output transactions")
        for t in self.transaction_outputs:
            print(t)
        print()
        if self.canBeDone:
            print("Transaction can be done")
        else:
            print("Transaction cannot be done")
        ##############################################


    def calculate_transaction_id(self):
        """ Finds a unique id to give to the transaction by combining
            the current time in seconds and the sender's public key """

        current_time = str(time.time()).split('.')
        current_time = current_time[0] + current_time[1]
        transaction_id = "TR" + str(current_time) + str(self.sender_address)

        return(transaction_id)


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

        message = self.text
        signature = encrypt_message(message, private_key)

        return signature


if __name__ == "__main__":

    with open('./TXOexample/someTXOs.json', encoding='utf8') as trs:
	    trs = json.load(trs)

    transaction = Transaction("1", "privatekey2", "recipient3", 100, trs)
