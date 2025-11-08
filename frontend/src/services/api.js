import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://b3-api-cloud.azurewebsites.net';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const cotacoesService = {
  // Busca todas as cotações (últimas 100)
  getAll: async () => {
    const response = await api.get('/api/data');
    return response.data;
  },

  // Busca cotações por ativo
  getByAtivo: async (ativo) => {
    const response = await api.get(`/api/data/ativo/${ativo}`);
    return response.data;
  },

  // Lista todas as tabelas disponíveis
  getTables: async () => {
    const response = await api.get('/api/tables');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};
