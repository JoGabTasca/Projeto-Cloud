import React from 'react';
import './CotacoesTable.css';

const CotacoesTable = ({ data, loading }) => {
  if (loading) {
    return <div className="loading">Carregando dados...</div>;
  }

  if (!data || data.length === 0) {
    return null; // Não mostra nada se não houver dados
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    // Parse a data GMT corretamente sem ajuste de timezone
    const date = new Date(dateString);
    // Usa UTC para evitar conversão de timezone
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const day = String(date.getUTCDate()).padStart(2, '0');
    return `${day}/${month}/${year}`;
  };

  const formatCurrency = (value) => {
    if (!value) return '-';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatVolume = (value) => {
    if (!value) return '-';
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  return (
    <div className="table-container">
      <h3 className="table-title">
        <span>📋</span>
        Dados Detalhados de Cotações
      </h3>
      <table className="cotacoes-table">
        <thead>
          <tr>
            <th>Ativo</th>
            <th>Data Pregão</th>
            <th>Abertura</th>
            <th>Fechamento</th>
            <th>Mínimo</th>
            <th>Máximo</th>
            <th>Volume</th>
          </tr>
        </thead>
        <tbody>
          {data.map((cotacao, index) => (
            <tr key={index}>
              <td className="ativo">{cotacao.Ativo}</td>
              <td>{formatDate(cotacao.DataPregao)}</td>
              <td className="price">{formatCurrency(cotacao.Abertura)}</td>
              <td className="price">{formatCurrency(cotacao.Fechamento)}</td>
              <td className="price">{formatCurrency(cotacao.PrecoMin)}</td>
              <td className="price">{formatCurrency(cotacao.PrecoMax)}</td>
              <td className="volume">{formatVolume(cotacao.Volume)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CotacoesTable;
