# Azure Function - Extração de Dados B3

## 📝 Mudanças Realizadas

### ✅ Correções Aplicadas:

1. **Diretório Temporário**
   - Alterado de `./dados_b3` para usar `tempfile.gettempdir()`
   - Azure Functions tem acesso limitado ao sistema de arquivos local
   - O diretório temporário é limpo automaticamente

2. **Tratamento de Erros**
   - Adicionado try/catch em todas as etapas críticas
   - Logs detalhados em cada passo do processo
   - Stack trace completo registrado no Azure

3. **Logs Aprimorados**
   - Mensagens mais descritivas em cada etapa
   - Facilita debugging via Azure Portal
   - Indica progresso e possíveis falhas

### 🔍 Como Debugar:

No Azure Portal:
1. Vá para sua Function App
2. **Monitor** → **Logs**
3. Procure por mensagens como:
   - `[INFO] Iniciando extracao B3...`
   - `[ERROR] Falha ao...`
   - Stack traces completos

### ⚙️ Configurações:

- **Schedule**: `*/30 * * * * *` (a cada 30 segundos para testes)
- **run_on_startup**: `False`
- **use_monitor**: `False`

### 🚀 Próximos Passos:

Após corrigir os erros, ajuste o schedule para produção:
- Todo dia à meia-noite: `0 0 0 * * *`
- A cada hora: `0 0 * * * *`
- Segunda a sexta às 18h: `0 0 18 * * 1-5`

## 📊 Fluxo de Execução:

1. Busca arquivo B3 dos últimos 7 dias
2. Faz download do ZIP
3. Salva em diretório temporário
4. Extrai ZIP (duas camadas)
5. Upload dos XMLs para Azure Blob Storage
6. Cria ponteiro com último arquivo
7. Limpa arquivos temporários

## ⚠️ Possíveis Erros:

Se continuar falhando, verifique:
- Conexão de rede da Function App
- Permissões de Storage Account
- Connection strings nas variáveis de ambiente
- Site da B3 está acessível
