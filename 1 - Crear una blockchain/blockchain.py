# Librerias
from ctypes import memset
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Parte 1 - Crear la cadena de bloques
class Blockchain:

    def __init__(self) -> None:
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof: int, previous_hash: str) -> None:
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }
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

# Parte 2 - Minado del bloque
def main():
    # Crear una web app
    app = Flask(__name__)

    # Crear una blockchain 
    _blockchain = Blockchain()

    # Pagina de bienvenida
    @app.route('/', methods=['GET'])
    def home():
        wellcome = '<h1>Bienvenido al proyecto de blockchain</h1>'
        mine_link = '<a href="/mine_block"> Minar un bloque </a> <br/>'
        chain_link = '<a href="/get_chain"> Visualizar cadena de bloques </a> <br/>'
        verify_chain_link = '<a href="/is_valid"> Verificar cadena de bloques. </a>'
        return wellcome + mine_link + chain_link + verify_chain_link

    # verificar blockchain
    @app.route("/is_valid", methods=['GET'])
    def is_valid():
        verify = _blockchain.is_chain_valid()
        msj = "Cadena de bloques valida"
        if(not verify):
            msj = "Cadena de bloques invalida"
        response = {
            'msj': msj,
            'data': {
                'value': verify
            }
        }
        return jsonify(response), 200

    # Minar un bloque
    @app.route("/mine_block", methods=['GET'])
    def mine_block():
        previous_block = _blockchain.get_last_block()
        previous_proof = previous_block['proof']
        proof = _blockchain.proof_of_work(previous_proof)
        previous_hash = _blockchain.hash(previous_block)
        block = _blockchain.create_block(proof, previous_hash)
        response = {
            'msj': 'Se ha minado un bloque!',
            'data': {
                'block': block
            },
        }
        return jsonify(response), 200

    @app.route('/get_chain', methods=['GET'])
    def get_chain():
        response = {
            'msj': 'Se ha obtenido la cadena de bloques',
            'data': {
                'chain': _blockchain.chain,
                'length': len(_blockchain.chain)
            }
        }
        return jsonify(response), 200

    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()