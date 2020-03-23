from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):

        ##set


        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address

        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = receiver_address

        #self.amount: το ποσό που θα μεταφερθεί
        self.amount = value

        #self.transaction_id: το hash του transaction
        self.transaction_id = calculate_transaction_id()

        #self.transaction_inputs: λίστα από Transaction Input
        self.transaction_inputs = calculate_transaction_inputs(TXOs)

        #self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs = calculate_transaction_outputs()

        self.signature = sign_transaction()


    def find_transaction_id():

        return("1")

    def calculate_transaction_inputs(selfe, TXOs):
        """ Finds the UTXOs needed for the transaction
            if there is no enough UTXOs to cover the transaction amount
            the function returns adn empty list """

        sender_UTXOs = [] # contains all the UTXOs of the sender
        available_amount = 0
        for tr in TXOs:
            if tr['wallet_id'] == self.sender_address and tr['type'] == 'UTXO':
                available_amount += tr['amount']

        if available_amount < self.amount:
            """ Transaction cannot be done """

            return []



    def calculate_transaction_outputs(selfe):


    #def to_dict(self):


    def sign_transaction(self):
        """
        Sign transaction with private key
        """

        return("signatureeeeeee")