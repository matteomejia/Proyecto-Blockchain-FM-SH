#instalar:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Librerias necesarias
from Blockchain import *
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, Response
from uuid import uuid4
import json

# Parte 2 - Minar transacciones (bloques)

# Crear Web app
app = Flask(__name__)

# Crear un address para el nodo en Port 5000
node_address = str(uuid4()).replace('-', '')

# Usar clase blockchain para crear una instancia de blockchain
blockchain = Blockchain()
#usuario (cambiarlo). Puede ser un login en el futuro.
user= 'shurtado98'
#nodo que reparte las UTECoins. Puede ser parte del Crear grupo.
house= 'casa'


# añadir el nodo testigo. Se espera que cada nodo en el futuro tenga la capacidad de leer resultados y ejecutar sus contratos.
blockchain.add_node("http://127.0.0.1:5000")


# contar saldo. Buscar UTXO. Mostrar el balance en la web (es una herramienta de las wallets). ¡NO FUNCIONA!
def get_balance():
    # ESTABLECER SALDO INICIAL:
    balance = 100
    for block in blockchain.chain:
        prize = 0
        transactions = block["transactions"]
        for transaction in transactions:
            if (transaction["sender"] == user):
                prize = -transaction["amount"]
            balance = balance + prize
            if (transaction["receiver"] == user):
                prize = transaction["amount"]
            balance = balance + prize
    return balance


# Minar un nuevo bloque
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = user, country= 'NULL', amount = 1)
    blockchain.create_block(proof, previous_hash)


# Interface web
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['action'] == 'Historial':
            return redirect('/replace_chain')
        elif request.form['action'] == 'Grupo':
            return redirect('/group')
        elif request.form['action'] == 'Apostar':
            return redirect('/bet')
    return render_template('index.html')


@app.route('/group', methods=['GET', 'POST'])
def group():
    if request.method == 'POST':
        return redirect('/connect_node')
    return render_template('grupo.html')


@app.route('/bet', methods=['GET', 'POST'])
def bet():
    if request.method == 'POST':
        return redirect('/add_transaction')
    return render_template('apostar.html')


# Ver Blockchain completo
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Ver si Blockchain es valido.
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Validado.'}
    else:
        response = {'message': 'No es valido.'}
    return jsonify(response), 200


# Añadir una transaccion a la blockchain. Pensar en cambiarle de nombre ya que no es una transaccion en si
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    country = request.form['country']
    amount = int(request.form['amount'])
    data = {"country": country, "amount": amount}
    blockchain.replace_chain()
    #Omitir el sender, porque es el usuario
    print(get_balance())
    if data["amount"] > get_balance():
        return 'No hay suficientes UTECoins', 400
    #actualiza la cadena antes de añadir algo.
    index = blockchain.add_transaction(user, house, data["country"], data["amount"])
    response = {'message': f'La transaccion se añade al bloque {index}'}
    #Se procede a minar tu propia transaccion
    mine_block()
    return jsonify(response), 201


# Parte 3 - Descentralizar la blockchain
# Conectar los nodos
@app.route('/connect_node', methods=['POST'])
def connect_node():
    node = request.form['friend']
    if node is None:
        return "No hay nodos", 400
    else:
        blockchain.add_node(node)
    response = {'message': 'Nodos conectados. Blockchain UTECoin contiene ahora los siguientes nodos:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
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
app.run(port=5001)
