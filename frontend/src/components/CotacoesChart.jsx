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
      <h3 className="chart-title">Histórico de Preços (Últimos 30 Dias)</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="data"
            stroke="#666"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#666"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `R$ ${value.toFixed(2)}`}
          />
          <Tooltip
            formatter={(value) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '14px' }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="Abertura"
            stroke="#8884d8"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            name="Abertura"
          />
          <Line
            type="monotone"
            dataKey="Fechamento"
            stroke="#82ca9d"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            name="Fechamento"
          />
          <Line
            type="monotone"
            dataKey="Máximo"
            stroke="#ff7c7c"
            strokeWidth={1.5}
            dot={{ r: 2 }}
            strokeDasharray="5 5"
            name="Máximo"
          />
          <Line
            type="monotone"
            dataKey="Mínimo"
            stroke="#ffa726"
            strokeWidth={1.5}
            dot={{ r: 2 }}
            strokeDasharray="5 5"
            name="Mínimo"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CotacoesChart;
