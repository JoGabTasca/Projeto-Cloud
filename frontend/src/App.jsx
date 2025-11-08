import React, { useState, useEffect } from 'react';
import CotacoesTable from './components/CotacoesTable';
import CotacoesChart from './components/CotacoesChart';
import { cotacoesService } from './services/api';
import './App.css';

function App() {
  const [cotacoes, setCotacoes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [ativo, setAtivo] = useState('');
  const [searchAtivo, setSearchAtivo] = useState('');

  // Lista de ativos populares da B3
  const ativosSugeridos = [
    'PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3',
    'BBAS3', 'WEGE3', 'RENT3', 'MGLU3', 'B3SA3'
  ];

  // Não carrega dados automaticamente - usuário deve selecionar um ativo
  useEffect(() => {
    // Mostra mensagem inicial em vez de carregar tudo
    console.log('Selecione um ativo para visualizar os dados');
  }, []);

  const loadCotacoes = async () => {
    // Removido - não vamos mais carregar todos os dados
    setError('Por favor, selecione um ativo específico para visualizar os dados.');
  };

  const handleSearch = async (ativoParam = searchAtivo) => {
    const ativoTrimmed = ativoParam.trim();
    
    if (!ativoTrimmed) {
      setError('Por favor, digite um código de ativo para buscar (ex: PETR4)');
      setCotacoes([]);
      setAtivo('');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await cotacoesService.getByAtivo(ativoTrimmed);
      
      if (!response.data || response.data.length === 0) {
        setError(`Nenhum dado encontrado para o ativo "${ativoTrimmed.toUpperCase()}". Tente outro código.`);
        setCotacoes([]);
      } else {
        setCotacoes(response.data);
        setAtivo(ativoTrimmed.toUpperCase());
      }
    } catch (err) {
      setError('Erro ao buscar ativo: ' + err.message);
      console.error(err);
      setCotacoes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAtivoClick = (ativoNome) => {
    setSearchAtivo(ativoNome);
    handleSearch(ativoNome);
  };

  const handleClearFilter = () => {
    setSearchAtivo('');
    setAtivo('');
    setCotacoes([]);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📈 B3 Cotações Dashboard</h1>
        <p>Acompanhe o histórico de cotações da Bolsa de Valores</p>
      </header>

      <div className="container">
        <div className="search-section">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Digite o código do ativo (ex: PETR4)"
              value={searchAtivo}
              onChange={(e) => setSearchAtivo(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="search-input"
            />
            <button onClick={() => handleSearch()} className="btn btn-primary">
              Buscar
            </button>
            {ativo && (
              <button onClick={handleClearFilter} className="btn btn-secondary">
                Limpar Filtro
              </button>
            )}
          </div>

          <div className="ativos-sugeridos">
            <span className="sugestoes-label">Ativos populares:</span>
            {ativosSugeridos.map((nome) => (
              <button
                key={nome}
                onClick={() => handleAtivoClick(nome)}
                className={`ativo-chip ${ativo === nome ? 'active' : ''}`}
              >
                {nome}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {!ativo && !loading && cotacoes.length === 0 && !error && (
          <div className="welcome-message">
            <h2>👋 Bem-vindo ao Dashboard de Cotações B3</h2>
            <p>Selecione um ativo acima ou use a busca para visualizar os dados.</p>
            <p className="hint">💡 Dica: Comece com ativos populares como PETR4, VALE3 ou ITUB4</p>
          </div>
        )}

        {ativo && cotacoes.length > 0 && (
          <div className="filter-info">
            Exibindo {cotacoes.length} registro(s) para <strong>{ativo}</strong>
          </div>
        )}

        <CotacoesChart data={cotacoes} loading={loading} />
        <CotacoesTable data={cotacoes} loading={loading} />
      </div>
    </div>
  );
}

export default App;
