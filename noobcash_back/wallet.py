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
    modulus_length = 256*4  # use larger value in production
    privatekey = RSA.generate(modulus_length, Random.new().read)
    publickey = privatekey.publickey()
    return privatekey, publickey


def encrypt_message(a_message, publickey):
    encryptor = PKCS1_OAEP.new(publickey)
    encrypted = encryptor.encrypt(bytes(a_message, "utf8"))
    # base64 encoded strings are database friendly
    encoded_encrypted_msg = base64.b64encode(encrypted)
    return encoded_encrypted_msg


def decrypt_message(encoded_encrypted_msg, privatekey):

    decryptor = PKCS1_OAEP.new(privatekey)
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decrypted = decryptor.decrypt(ast.literal_eval(str(decoded_encrypted_msg)))

    # decoded_decrypted_msg = privatekey.decrypt(decoded_encrypted_msg)
    return decrypted


class wallet:

    def __init__(self):
        # set

        self.public_key = None
        self.private_key = None

        self.generate_wallet()

        # self_address

        with open('./TXOexample/someTXOs.json', encoding='utf8') as trs:
            trs = json.load(trs)

        self.transactions = trs

        # self.transactions

    def generate_wallet(self):
        """ Generates a pair of public/private key using RSA algorithm """

        privatekey, publickey = generate_keys()
        """ Example of use """
        # message = "Oh nana Oh nanana"
        # encrypted_msg = encrypt_message(message, publickey)
        # decrypted_msg = decrypt_message(encrypted_msg, privatekey)

        # print("%s " % (privatekey.exportKey()))
        # print("%s " % (publickey.exportKey()))
        # print(" Original content: %s " % (message))
        # print("Encrypted message: %s " % (encrypted_msg))
        # print("Decrypted message: %s " % (decrypted_msg))

        # randomly creates a public key
        public = "%032x" % random.getrandbits(256)
        #using public key and sha256 we create private key
        private = hashlib.sha256(public.encode('utf8')).hexdigest()
  		
        self.public_key = public
        self.private_key = private

        print("New wallet is created.")
        print("Wallet public key:", self.public_key)
        print("Wallet private key:", self.private_key)
        print()

    def balance(self):
        """ Wallet balance is calculated by adding all UTXOs having this wallet as a reciever """

        acc_balance = 0

        for tr in self.transactions:
            if tr['wallet_id'] == self.public_key and tr['type'] == 'UTXO':
                acc_balance += tr['amount']

        return acc_balance

    def showBalance(self):
        print("Wallet public key:", self.public_key)
        print("Balance:", self.balance(), "NBC")
        print()


if __name__ == '__main__':

    ros_wallet = wallet()
    ros_wallet.showBalance()
    