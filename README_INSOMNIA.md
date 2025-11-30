# Coleção Insomnia - Duzz Commercial BFF API

## 📋 Sobre a Coleção

Esta coleção do Insomnia contém todos os endpoints da API BFF do Duzz Commercial, organizados por categorias e com exemplos prontos para uso.

## 🚀 Como Usar

### 1. Importar a Coleção
1. Abra o Insomnia
2. Vá em **Application** → **Preferences** → **Data** → **Import Data**
3. Selecione **From File** e escolha o arquivo `insomnia_collection.json`
4. A coleção será importada com todas as requisições organizadas

### 2. Configurar o Ambiente
1. Na coleção importada, vá para **Environments** (ícone do globo)
2. Edite o ambiente **Base Environment**
3. Configure as variáveis:
   - `base_url`: `http://localhost:8000` (URL da sua API)
   - `sessiontoken`: Seu token de autenticação real
   - `company`: Sua empresa/company real

### 3. Iniciar a API
```bash
cd /home/henrique/Documents/freela/Duzz-Commercial-DRE
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Endpoints Disponíveis

### 🔍 Health Checks
- **GET /health** - Verifica se a API está funcionando (sem autenticação)
- **GET /** - Endpoint raiz da API (sem autenticação)

### 💰 Faturamento
- **GET /api/faturamento** - Busca dados de faturamento por mês
  - Parâmetro: `month` (YYYY-MM-DD)
- **POST /api/faturamento/process** - Processa dados brutos de faturamento
  - Body: JSON com dados de pagamentos, vendas, estoque e contas

### 📦 Produtos
- **GET /api/produtos** - Resumo de vendas de produtos por mês
  - Parâmetro: `month` (YYYY-MM-DD)

### 🛠️ Serviços
- **GET /api/servicos** - Resumo de vendas de serviços por mês
  - Parâmetro: `month` (YYYY-MM-DD)

### 👥 Fidelidade
- **GET /api/fidelidade** - Dados de fidelidade de clientes por mês
  - Parâmetro: `month` (YYYY-MM-DD)

## 🔐 Autenticação

Todos os endpoints (exceto health checks) requerem autenticação via headers:
- `sessiontoken`: Token de sessão válido
- `company`: Identificador da empresa

## 📝 Exemplo de Uso

### Testando o Health Check:
1. Selecione **Health Check** na pasta **Health Checks**
2. Clique em **Send**
3. Deve retornar: `{"status": "healthy", "service": "Duzz Commercial BFF"}`

### Testando um Endpoint Protegido:
1. Configure as variáveis de ambiente com seus dados reais
2. Selecione **GET Faturamento** na pasta **Faturamento**
3. Clique em **Send**
4. Se autenticado corretamente, retornará os dados de faturamento

### Testando o POST de Processamento:
1. Selecione **POST Processar Faturamento**
2. O body já contém um exemplo de JSON
3. Modifique os dados conforme necessário
4. Clique em **Send** para processar

## 🎯 Estrutura das Respostas

Todas as respostas seguem o padrão:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

## ⚠️ Observações Importantes

1. **Headers de Autenticação**: Configure corretamente no ambiente
2. **Parâmetro Month**: Use sempre no formato `YYYY-MM-DD` (ex: `2024-01-01`)
3. **Servidor Local**: Certifique-se de que a API está rodando em `http://localhost:8000`
4. **Dados Reais**: Substitua os valores de exemplo por dados reais da sua empresa

## 🔄 Atualizações

A coleção pode ser atualizada conforme novos endpoints forem adicionados à API. Para exportar uma versão atualizada, use **Export** no Insomnia.
