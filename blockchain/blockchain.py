# Librerias
from ctypes import memset
import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests

# Crear la cadena de bloques
class Blockchain:

    def __init__(self) -> None:
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()

    def create_block(self, proof: int, previous_hash: str) -> None:
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions,
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof: int) -> int:
        new_proof = 1
        check_proof = False
        while(check_proof == False):
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else :
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain = None) -> bool:
        if(chain == None):
            chain = self.chain
        previous_block = chain[0]
        block_index = 1
        while(block_index < len(chain)):
            block = chain[block_index]
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if block['previous_hash'] != self.hash(previous_block) : return False
            if hash_operation[:4] != "0000": return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender:str, receiver:str, amount:float):
        self.transactions.append({
            'sender': sender,
            'reciver': receiver,
            'ammount': amount
        })
        last_block = self.get_last_block()
        return last_block['index'] + 1

    def add_node(self, address:str):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if(response.status_code == 200):
                node_chain = response.json()['data']['chain']
                lenght_node_chain = response.json()['data']['length']
                if(lenght_node_chain > max_length and self.is_chain_valid(node_chain)):
                    longest_chain = node_chain
                    max_length = lenght_node_chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False