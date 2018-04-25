# -*- coding:utf-8  -*-

import json
from uuid import uuid4

from flask import Flask, jsonify, request
from src.BlockChain import BlockChain

# https://mp.weixin.qq.com/s/-LOu6TixGGkeLrWGZCQ5zQ

# instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# instantiate the blockchain
blockchain = BlockChain()


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': BlockChain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_data()
    values = json.loads(values)

    # check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f"transaction will be added to block {index}"}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    # we runs the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_block = last_block['proof']
    proof = blockchain.proof_of_work(last_block)

    # we must receive a reward for finding the proof.
    # the sender is '0' to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=0,
    )

    # forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'new block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['prevsious_hash'],
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)