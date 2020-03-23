import json

""" test file for TXO """


TXOs = []

tr = {}
tr['transaction_id'] = '1'   # transaction id
tr['wallet_id'] = "1"        # wallet's public key
tr['type'] = 'UTXO'          # spent TXO
tr['amount'] = 10            # NBCs

TXOs.append(tr)

tr = {}
tr['transaction_id'] = '2'   # transaction id
tr['wallet_id'] = "1"        # wallet's public key
tr['type'] = 'UTXO'          # spent TXO
tr['amount'] = 111           # NBCs

TXOs.append(tr)

tr = {}
tr['transaction_id'] = "3" # transaction id
tr['wallet_id'] = "3"      # wallet's public key
tr['type'] = 'UTXO'        # spent TXO
tr['amount'] = 102         # NBCs

TXOs.append(tr)

tr = {}
tr['transaction_id'] = '5' # transaction id
tr['wallet_id'] = '1'      # wallet's public key
tr['type'] = 'UTXO'        # spent TXO
tr['amount'] = 900         # NBCs

TXOs.append(tr)

tr = {}
tr['transaction_id'] = '6' # transaction id
tr['wallet_id'] = '1'      # wallet's public key
tr['type'] = 'UTXO'        # spent TXO
tr['amount'] = 200         # NBCs

TXOs.append(tr)

tr = {}
tr['transaction_id'] = '7' # transaction id
tr['wallet_id'] = '1'      # wallet's public key
tr['type'] = 'UTXO'        # spent TXO
tr['amount'] = 500         # NBCs

TXOs.append(tr)

with open('someTXOs.json', 'w', encoding = "utf8") as outfile:
    json.dump(TXOs, outfile)