from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

import time
import json


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

        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address

        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = recipient_address

        # Checks if the transaction can be done
        self.canBeDone = True

        #self.amount: το ποσό που θα μεταφερθεί
        self.amount = value

        #self.transaction_id: το hash του transaction
        self.transaction_id = self.calculate_transaction_id()

        #self.transaction_inputs: λίστα από Transaction Input
        self.transaction_inputs = prev_transactions

        #self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs = self.calculate_transaction_outputs()

        self.signature = self.sign_transaction(sender_private_key)

        self.canBeDone = None

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



    #def to_dict(self):


    def sign_transaction(self, private_key):
        """ Sign transaction with private key """

        return(private_key + "-signature")


if __name__ == "__main__":

    with open('./TXOexample/someTXOs.json', encoding='utf8') as trs:
	    trs = json.load(trs)

    transaction = Transaction("1", "privatekey2", "recipient3", 100, trs)