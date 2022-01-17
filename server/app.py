from blockchain.blockchain import Blockchain
from flask import Flask, jsonify, request
from uuid import uuid4

# Parte 2 - Minado del bloque
def exec(port:int, name:str):
    # Crear una web app
    app = Flask(__name__)

    # Si se tiene un error 500, actualizar flask, para que no se quede pillado
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    # Crear la node address
    node_address = str(uuid4()).replace("-","")

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
        _blockchain.add_transaction(sender=node_address, receiver=name, amount=10)
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


    # Añadir una nueva transacción a la cadena de bloques
    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        json = request.get_json()
        transaction_keys = ['sender', 'receiver', 'amount']
        response = {
            'msj': 'Faltan elementos de la transaccion'
        }
        if not all(key in json for key in transaction_keys):
            return jsonify(response), 400
        index = _blockchain.add_transaction(sender=json['sender'], receiver=json['receiver'], amount=json['amount'])
        response={
            'msj': 'Transaccion incluida en la pool',
            'data':{
                'block_index': index
            }
        }
        return jsonify(response), 201

    # Descentralizar la cadena de bloques
    # Conectar nuevos nodos
    @app.route('/connect_node', methods=['POST'])
    def connect_node():
        json = request.get_json()
        nodes = json['nodes'] #json.get('nodes')
        if nodes is None:
            response = {
                'msj': 'No hay nodes que añadir'
            }
            return jsonify(response), 400
        for node in nodes:
            _blockchain.add_node(node)
        response = {
            'msj': 'Nodos actualizados correctamente',
            'data': {
                'total_nodes': list(_blockchain.nodes)
            }
        }
        return jsonify(response), 201

    # Reemplazar la cadena por la mas larga (si es necesario)
    @app.route("/replace_chain", methods=['GET'])
    def replace_chain():
        is_chain_replaced = _blockchain.replace_chain()
        msj = "La cadena de bloques fue reemplazada"
        if(not is_chain_replaced):
            msj = "La cadena de bloques es dominante, por tanto no ha sido remplazada"
        response = {
            'msj': msj,
            'data': {
                'is_chain_replaced': is_chain_replaced,
                'chain': _blockchain.chain
            }
        }
        return jsonify(response), 200

    app.run(host='0.0.0.0', port=port)