import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './CotacoesChart.css';

const CotacoesChart = ({ data, loading }) => {
  if (loading) {
    return <div className="loading">Carregando gráfico...</div>;
  }

  if (!data || data.length === 0) {
    return null; // Não mostra nada se não houver dados
  }

  // Formata os dados para o gráfico
  const chartData = data
    .map((cotacao) => {
      const date = new Date(cotacao.DataPregao);
      // Usa UTC para evitar problemas de timezone
      return {
        data: `${String(date.getUTCDate()).padStart(2, '0')}/${String(date.getUTCMonth() + 1).padStart(2, '0')}`,
        Abertura: parseFloat(cotacao.Abertura) || 0,
        Fechamento: parseFloat(cotacao.Fechamento) || 0,
        Máximo: parseFloat(cotacao.PrecoMax) || 0,
        Mínimo: parseFloat(cotacao.PrecoMin) || 0,
        timestamp: date.getTime(),
      };
    })
    .sort((a, b) => a.timestamp - b.timestamp)
    .slice(-30); // Últimos 30 dias

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">
        <span>📈</span>
        Histórico de Preços (Últimos 30 Dias)
      </h3>
      <ResponsiveContainer width="100%" height={450}>
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 20, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--b3-gray-200)" />
          <XAxis
            dataKey="data"
            stroke="var(--b3-gray-600)"
            style={{ fontSize: '12px', fontWeight: '500' }}
            tick={{ fill: 'var(--b3-gray-600)' }}
          />
          <YAxis
            stroke="var(--b3-gray-600)"
            style={{ fontSize: '12px', fontWeight: '500' }}
            tick={{ fill: 'var(--b3-gray-600)' }}
            tickFormatter={(value) => `R$ ${value.toFixed(2)}`}
          />
          <Tooltip
            formatter={(value) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: 'var(--b3-white)',
              border: '2px solid var(--b3-gray-300)',
              borderRadius: '6px',
              boxShadow: '0 4px 12px var(--b3-shadow)',
              padding: '12px',
            }}
            labelStyle={{
              color: 'var(--b3-primary)',
              fontWeight: '700',
              marginBottom: '8px',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '14px', fontWeight: '500', paddingTop: '20px' }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="Abertura"
            stroke="var(--b3-accent)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: 'var(--b3-accent)' }}
            activeDot={{ r: 6, fill: 'var(--b3-primary)' }}
            name="Abertura"
          />
          <Line
            type="monotone"
            dataKey="Fechamento"
            stroke="var(--b3-success)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: 'var(--b3-success)' }}
            activeDot={{ r: 6, fill: 'var(--b3-primary)' }}
            name="Fechamento"
          />
          <Line
            type="monotone"
            dataKey="Máximo"
            stroke="var(--b3-danger)"
            strokeWidth={2}
            dot={{ r: 3, fill: 'var(--b3-danger)' }}
            strokeDasharray="5 5"
            name="Máximo"
          />
          <Line
            type="monotone"
            dataKey="Mínimo"
            stroke="var(--b3-warning)"
            strokeWidth={2}
            dot={{ r: 3, fill: 'var(--b3-warning)' }}
            strokeDasharray="5 5"
            name="Mínimo"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CotacoesChart;
