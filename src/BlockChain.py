# -*- coding: utf-8 -*-

import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse

'''
    Blockchain 类负责管理链式数据，
    它会存储交易
    并且还有添加新的区块到链式数据的Method
'''


class BlockChain:
    def __init__(self):
        self.chain = []                     # 区块链
        self.current_transactions = []      # 存储交易
        self.nodes = set()                  # 集群

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        创建一个新的区块到区块链中, 在这个新的区块中保存了当前的交易(清空交易记录)
        :param proof: <int> 由工作证明算法生产的证明
        :param previout_hash: (Optional) <str> 前一个区块的hash值
        :return: <dict> 新区块
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # 重置当前交易记录
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        创建一个新的交易到下一个被挖掘的区块
        :param sender:  <str> 发送人的地址.
        :param recipient: <str> 接受人的地址.
        :param amount: <int> 金额.
        :return: <int> 持有本次交易的区块索引.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        各一个区块生成 SHA-256值
        :param block: <dict> Block
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # returns the last block in the chain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        simple proof of work algorithm
        - find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof.
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        validates the proof: Does hash(last_proof, proof) contains 4 leading zeroes ?
        :param last_proof: <int> previous proof
        :param proof: <int> current proof
        :return: <bool> True if corrent, False if not.
        """
        guess = f'{last_proof}{proof}'.endcode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        '''
        add a new node to the list of nodes.
        :param address: <str> address of nodes. Eq 'http://192.168.0.5:5000'
        :return: None
        '''
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url)

    def valid_chain(self, chain):
        '''
        determine if a given blockchain is valid
        :param chain: <list> a blockChain
        :return: <block> true if valid, return false if not
        '''

        last_block = chain[0] ;
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{blick}')
            print('\n-----------\n')
            # check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        this is cour consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # we're only looking for chains longer than ours
        max_length = len(self.chain)

        # grab and verify the chain from all the nodes in our network
        for node in neighbours:
            response = requests.get(f"http://{nodes}/chains")

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False


