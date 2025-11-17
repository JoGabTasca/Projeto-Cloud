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
            'search': '/api/data/ativo/<ativo>',
            'stats': '/api/data/stats',
            'ativo_stats': '/api/data/ativo/<ativo>/stats'
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
    """Retorna registros filtrados por ativo (nome da ação) - busca exata"""
    # Remove espaços e converte para maiúsculo para comparação
    ativo_clean = ativo.strip().upper()
    query = "SELECT * FROM cotacoes WHERE UPPER(TRIM(Ativo)) = %s ORDER BY DataPregao DESC"
    params = (ativo_clean,)
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

@app.route('/api/data/stats', methods=['GET'])
def get_data_stats():
    """Retorna estatísticas dos dados: total de registros, datas disponíveis, etc."""
    try:
        # Total de registros
        total_query = "SELECT COUNT(*) as total FROM cotacoes"
        total_result = fetch_data(total_query)
        total = total_result[0]['total'] if total_result else 0
        
        # Datas disponíveis (distintas)
        dates_query = """
            SELECT 
                DataPregao, 
                COUNT(*) as quantidade,
                COUNT(DISTINCT Ativo) as ativos_distintos
            FROM cotacoes 
            GROUP BY DataPregao 
            ORDER BY DataPregao DESC
        """
        dates_result = fetch_data(dates_query)
        
        # Ativos distintos
        ativos_query = "SELECT COUNT(DISTINCT Ativo) as total FROM cotacoes"
        ativos_result = fetch_data(ativos_query)
        ativos_distintos = ativos_result[0]['total'] if ativos_result else 0
        
        # Data mais antiga e mais recente
        range_query = """
            SELECT 
                MIN(DataPregao) as data_minima,
                MAX(DataPregao) as data_maxima
            FROM cotacoes
        """
        range_result = fetch_data(range_query)
        
        return jsonify({
            'total_registros': total,
            'ativos_distintos': ativos_distintos,
            'data_minima': str(range_result[0]['data_minima']) if range_result and range_result[0]['data_minima'] else None,
            'data_maxima': str(range_result[0]['data_maxima']) if range_result and range_result[0]['data_maxima'] else None,
            'dados_por_data': dates_result or []
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar estatísticas: {str(e)}'}), 500

@app.route('/api/data/ativo/<ativo>/stats', methods=['GET'])
def get_ativo_stats(ativo):
    """Retorna estatísticas de um ativo específico"""
    ativo_clean = ativo.strip().upper()
    try:
        # Total de registros do ativo
        total_query = "SELECT COUNT(*) as total FROM cotacoes WHERE UPPER(TRIM(Ativo)) = %s"
        total_result = fetch_data(total_query, (ativo_clean,))
        total = total_result[0]['total'] if total_result else 0
        
        # Datas disponíveis para este ativo
        dates_query = """
            SELECT 
                DataPregao, 
                COUNT(*) as quantidade
            FROM cotacoes 
            WHERE UPPER(TRIM(Ativo)) = %s
            GROUP BY DataPregao 
            ORDER BY DataPregao DESC
        """
        dates_result = fetch_data(dates_query, (ativo_clean,))
        
        # Data mais antiga e mais recente
        range_query = """
            SELECT 
                MIN(DataPregao) as data_minima,
                MAX(DataPregao) as data_maxima
            FROM cotacoes
            WHERE UPPER(TRIM(Ativo)) = %s
        """
        range_result = fetch_data(range_query, (ativo_clean,))
        
        return jsonify({
            'ativo': ativo_clean,
            'total_registros': total,
            'data_minima': str(range_result[0]['data_minima']) if range_result and range_result[0]['data_minima'] else None,
            'data_maxima': str(range_result[0]['data_maxima']) if range_result and range_result[0]['data_maxima'] else None,
            'dados_por_data': dates_result or []
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar estatísticas: {str(e)}'}), 500

if __name__ == "__main__":
    print("\nIniciando servidor Flask...")
    print("Endpoints disponíveis:")
    print("  GET /api/health - Verifica status da API")
    print("  GET /api/tables - Lista todas as tabelas")
    print("  GET /api/data - Retorna todas as cotações")
    print("  GET /api/data/ativo/<ativo> - Busca cotações por nome do ativo")
    print("  GET /api/data/stats - Estatísticas gerais dos dados")
    print("  GET /api/data/ativo/<ativo>/stats - Estatísticas de um ativo específico")
    print("\nExemplo: http://localhost:5000/api/data/ativo/PETR4")
    print("Exemplo: http://localhost:5000/api/data/stats")
    app.run(debug=True, host='0.0.0.0', port=5000)
