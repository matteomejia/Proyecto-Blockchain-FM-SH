#instalar:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Librerias necesarias
from Blockchain import *
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, Response
from uuid import uuid4

# Parte 2 - Minar transacciones (bloques)

# Crear Web app
app = Flask(__name__)

# Crear un address para el nodo en Port 5000
node_address = str(uuid4()).replace('-', '')

# Usar clase blockchain para crear una instancia de blockchain
blockchain = Blockchain()
# usuario (cambiarlo). Puede ser un login en el futuro.
user = 'casa'
# Establecer Saldo. Quizás tengamos que empezar con este nodo lleno de monedas, y que reparta segun los clientes pidan.
balance = 0
# nodo que reparte las UTECoins. Puede ser parte del Crear grupo.
house = 'casa'


# añadir el nodo testigo. Se espera que cada nodo en el futuro tenga la capacidad de leer resultados y ejecutar sus contratos.
# blockchain.add_node("http://127.0.0.1:5000")
# añade a los dos testers
blockchain.add_node("http://127.0.0.1:5001")
blockchain.add_node("http://127.0.0.1:5002")

#contar saldo NO NECESARIO. Buscar UTXO


#Deberia ejecutarse al finalizar un partido
def bet_outcome():
    #Web Scraping Web Scraping Web Scraping Web Scraping Web Scraping Web Scraping
    #Falta limitar que solo se pueda apostar por uno, una vez. Minima cantidad, etc.
    winner="PERU"
    array_winners=[]
    for block in blockchain.chain:
        prize=0
        transactions= block["transactions"]
        for transaction in transactions:
            if (transaction["receiver"]==user):
                prize= prize+ transaction["amount"]
                if(transaction["country"]==winner):
                    array_winners.append(transaction["sender"])
    n=len(array_winners)
    res= prize%n
    prize= prize-res
    prize= prize/n
    #Se envia el monto dividido (ENTERO) entre ganadores,
    for lucky in array_winners:
        blockchain.add_transaction(user, lucky, winner, prize)


# Minar un nuevo bloque
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = user, country= 'NULL', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Bloque minado.',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200


# Ver Blockchain completo
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Ver si Blockchain es valido.
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Validado.'}
    else:
        response = {'message': 'No es valido.'}
    return jsonify(response), 200


# Añadir una transaccion a la blockchain. Pensar en cambiarle de nombre ya que no es una transaccion en si
@app.route('/add_transaction', methods = ['GET'])
def add_transaction():
    #actualiza la cadena antes de añadir algo.
    blockchain.replace_chain()
    bet_outcome()
    response = {'message': 'se devolvio el dinero a los ganadores'}
    #Se procede a minar tu propia transaccion
    mine_block()
    return jsonify(response), 201


# Parte 3 - Descentralizar la blockchain

# Conectar los nodos
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No hay nodos", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Nodos conectados. Blockchain UTECoin contiene ahora los siguientes nodos:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# Reemplazar la cadena de un nodo por la mas larga cuando sea necesario.
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'La cadena ha sido actualizada.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Esta es la cadena actualizada.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


# Correr el app.
app.run(port = 5000)
