import binascii

import Crypto
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
import random
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import base64
import ast


def generate_keys():
    # RSA modulus length must be a multiple of 256 and >= 1024
    modulus_length = 256*4
    privatekey = RSA.generate(modulus_length, Random.new().read)
    publickey = privatekey.publickey()
    
    return publickey, privatekey

def rsa_to_string(rsa_key):
    key = rsa_key.exportKey("PEM")
    key = key.decode("utf-8")
    key = key.split('\n')
    key = key[:-1]
    key = key[1:]

    str_key = ''
    for k in key:
        str_key += k

    return str_key


class wallet:

    def __init__(self):
        # set

        self.public_key = None
        self.private_key = None

        self.generate_wallet()

        self.unspent_transactions = []

    def generate_wallet(self):
        """ Generates a pair of public/private key using RSA algorithm """

        self.public_key , self.private_key = generate_keys()

        self.public_key_str = rsa_to_string(self.public_key)

        print("New wallet was created with public key")
        print(self.public_key_str)
        print()


    def balance(self):
        """ Wallet balance is calculated by adding all UTXOs having this wallet as a reciever """

        acc_balance = 0

        for tr in self.unspent_transactions:
            if tr['wallet_id'] == self.public_key_str:
                acc_balance += tr['amount']

        return acc_balance

    def showBalance(self):
        print("Balance:", self.balance(), "NBC")
        print()


if __name__ == '__main__':

    ros_wallet = wallet()
    ros_wallet.showBalance()

    print(str(ros_wallet.public_key.exportKey('PEM')))