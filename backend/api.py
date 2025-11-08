# API simples para conectar ao banco de dados MySQL Azure e expor endpoints

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configuração do banco de dados com SSL habilitado para Azure MySQL
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'ewjgmv'),
    'password': os.getenv('DB_PASSWORD', '123senhaS@'),
    'host': os.getenv('DB_HOST', 'b3-bd-cloud-2025.mysql.database.azure.com'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'b3_data'),
    'ssl_ca': None,  # Azure MySQL requer SSL
    'ssl_verify_cert': False,  # Simplifica a conexão em desenvolvimento
    'connection_timeout': 30,
    'autocommit': True
}

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def fetch_data(query, params=None):
    """Executa uma query e retorna os resultados"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Error as e:
        print(f"Erro ao executar query: {e}")
        if connection:
            connection.close()
        return None

@app.route('/', methods=['GET'])
def index():
    """Rota raiz para verificar se a API está funcionando"""
    return jsonify({
        'status': 'API B3 está online!',
        'endpoints': {
            'health': '/api/health',
            'tables': '/api/tables',
            'data': '/api/data',
            'search': '/api/data/ativo/<ativo>'
        }
    })

@app.route('/api/tables', methods=['GET'])
def list_tables():
    """Lista todas as tabelas disponíveis no banco de dados"""
    query = "SHOW TABLES"
    tables = fetch_data(query)
    if tables is None:
        return jsonify({'error': 'Erro ao buscar tabelas'}), 500
    return jsonify({'tables': tables})

@app.route('/api/data', methods=['GET'])
def get_all_data():
    """Retorna todos os registros da tabela de cotações"""
    query = "SELECT * FROM cotacoes ORDER BY DataPregao DESC"
    data = fetch_data(query)
    if data is None:
        return jsonify({'error': 'Erro ao buscar dados'}), 500
    return jsonify({'data': data, 'count': len(data)})

@app.route('/api/data/ativo/<ativo>', methods=['GET'])
def get_by_ativo(ativo):
    """Retorna registros filtrados por ativo (nome da ação)"""
    query = "SELECT * FROM cotacoes WHERE Ativo LIKE %s ORDER BY DataPregao DESC"
    params = (f'%{ativo}%',)
    data = fetch_data(query, params)
    if data is None:
        return jsonify({'error': 'Erro ao buscar dados'}), 500
    return jsonify({'data': data, 'count': len(data)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica se a API e a conexão com o banco estão funcionando"""
    connection = get_db_connection()
    if connection:
        connection.close()
        return jsonify({'status': 'OK', 'database': 'connected'})
    return jsonify({'status': 'ERROR', 'database': 'disconnected'}), 500

if __name__ == "__main__":
    print("\nIniciando servidor Flask...")
    print("Endpoints disponíveis:")
    print("  GET /api/health - Verifica status da API")
    print("  GET /api/tables - Lista todas as tabelas")
    print("  GET /api/data - Retorna todas as cotações (últimas 100)")
    print("  GET /api/data/ativo/<ativo> - Busca cotações por nome do ativo")
    print("\nExemplo: http://localhost:5000/api/data/ativo/PETR4")
    app.run(debug=True, host='0.0.0.0', port=5000)
