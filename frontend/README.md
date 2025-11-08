# B3 Cotações Dashboard - Frontend

Dashboard React para visualizar cotações da B3 (Bolsa de Valores).

## 🚀 Tecnologias

- **React** 18.3
- **Vite** - Build tool
- **Recharts** - Gráficos
- **Axios** - HTTP client

## 📦 Instalação

```bash
npm install
```

## 🔧 Desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:3000

## 🏗️ Build

```bash
npm run build
```

## 🌐 Configuração da API

Por padrão, a API aponta para:
- Produção: `https://b3-api-cloud.azurewebsites.net`
- Desenvolvimento: proxy para `http://localhost:5000`

Para alterar, crie um arquivo `.env`:

```env
VITE_API_URL=https://sua-api.com
```

## 📊 Funcionalidades

- ✅ Visualização de cotações em tabela
- ✅ Gráfico de linha com histórico de preços
- ✅ Busca por código do ativo (ex: PETR4)
- ✅ Filtros rápidos para ativos populares
- ✅ Responsivo para mobile

## 🎨 Componentes

- `CotacoesTable` - Tabela de cotações
- `CotacoesChart` - Gráfico de histórico
- `App` - Componente principal com busca
