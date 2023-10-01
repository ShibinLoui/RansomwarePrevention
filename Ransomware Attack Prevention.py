# Import necessary libraries
from hashlib import sha256
import json
import time
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()

        # Create genesis block
        self.add_block(previous_hash='1', proof=100)

    def add_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, recipient, file_hash):
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'file_hash': file_hash,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        return sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

# Flask web application
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# API endpoint to mine a new block
@app.route('/mine', methods=['GET'])
def mine():
    # Proof of Work algorithm - Simplified for illustration purposes
    last_block = blockchain.last_block
    proof = 0
    while blockchain.hash_proof(last_block, proof)[:4] != '0000':
        proof += 1

    # Add a transaction (for file info) to the blockchain
    blockchain.add_transaction(sender="0", recipient=node_identifier, file_hash="example_file_hash")

    # Add the new block to the blockchain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

# API endpoint to create a new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'file_hash']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.add_transaction(values['sender'], values['recipient'], values['file_hash'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

# API endpoint to get the full blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
