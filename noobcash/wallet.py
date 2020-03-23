import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):
		##set

		self.public_key = None
		self.private_key = None

		self.generate_wallet()

		#self_address

		with open('./TXOexample/someTXOs.json', encoding='utf8') as trs:
			trs = json.load(trs)

		self.transactions = trs

		#self.transactions

	def generate_wallet(self):
		""" Generates a pair of public/private key using RSA algorithm """

		public = 1
		private = 2


		self.public_key = public
		self.private_key = private

		print("New wallet is created.")
		print("Wallet public key:", self.public_key)
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