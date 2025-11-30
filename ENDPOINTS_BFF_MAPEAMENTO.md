# 📊 Mapeamento de Endpoints BFF para Gráficos

## ✅ Endpoints Criados no BFF

### 1. **Faturamento** - `/api/faturamento`
- **Método**: `GET`
- **Parâmetro**: `month` (date)
- **Gráficos correspondentes**:
  - Resumo Geral (receitas, despesas, descontos, CMV)
  - Vendas por dia da semana
  - Vendas por período do dia
  - Entradas por método de pagamento

### 2. **Métricas Calculadas** - `/api/metricas`
- **Método**: `GET`
- **Parâmetro**: `month` (date)
- **Gráficos correspondentes**:
  - Lucro Líquido
  - Receitas - Despesas
  - Ticket Médio
  - Descontos sobre Receita
  - CMV Sobre Receita
  - Custo Ticket

### 3. **Serviços** - `/api/servicos`
- **Método**: `GET`
- **Parâmetro**: `month` (date)
- **Gráficos correspondentes**:
  - TOP Serviços Mais Vendidos
  - Gráfico de área de serviços
  - Tabela de serviços

### 4. **Produtos** - `/api/produtos`
- **Método**: `GET`
- **Parâmetro**: `month` (date)
- **Gráficos correspondentes**:
  - TOP Produtos Mais Vendidos
  - Gráfico de área de produtos
  - Tabela de produtos

### 5. **Fidelidade** - `/api/fidelidade`
- **Método**: `GET`
- **Parâmetro**: `month` (date)
- **Gráficos correspondentes**:
  - TOP Clientes
  - Gráfico de barras de clientes
  - Tabela de fidelidade

## 📈 Gráficos da Interface e seus Endpoints

### **Resumo Geral**
- **Endpoint**: `/api/faturamento`
- **Dados**: receitas, despesas, descontos, CMV
- **Visualizações**: 
  - Dataframe de faturamento
  - Gráfico de área acumulado
  - Métricas (Lucro Líquido, Receitas-Despesas, etc.)

### **Vendas por Dia da Semana**
- **Endpoint**: `/api/faturamento`
- **Dados**: daily (distribuição por dia)
- **Visualizações**:
  - Gráfico de área
  - Dataframe
  - Gráfico de pizza

### **Vendas por Período do Dia**
- **Endpoint**: `/api/faturamento`
- **Dados**: by_period (manhã, tarde, noite, madrugada)
- **Visualizações**:
  - Gráfico de área
  - Dataframe
  - Gráfico de pizza

### **Entradas por Método de Pagamento**
- **Endpoint**: `/api/faturamento`
- **Dados**: by_payment_methods
- **Visualizações**:
  - Gráfico de área
  - Gráfico de pizza

### **Fidelidade (Clientes)**
- **Endpoint**: `/api/fidelidade`
- **Dados**: clientes por valor gasto
- **Visualizações**:
  - TOP N clientes (slider)
  - Dataframe
  - Gráfico de barras

### **Produtos**
- **Endpoint**: `/api/produtos`
- **Dados**: produtos mais vendidos
- **Visualizações**:
  - TOP N produtos (slider)
  - Dataframe
  - Gráfico de área

### **Serviços**
- **Endpoint**: `/api/servicos`
- **Dados**: serviços mais vendidos
- **Visualizações**:
  - TOP N serviços (slider)
  - Dataframe
  - Gráfico de área

## 🔄 Correspondência Completa

| Gráfico/Visualização | Endpoint BFF | Dados Retornados |
|---------------------|--------------|------------------|
| Resumo Geral | `/api/faturamento` | receitas, despesas, descontos, CMV |
| Vendas por Dia | `/api/faturamento` | daily (distribuição por dia da semana) |
| Vendas por Período | `/api/faturamento` | by_period (manhã, tarde, noite, madrugada) |
| Métodos de Pagamento | `/api/faturamento` | by_payment_methods |
| TOP Clientes | `/api/fidelidade` | clientes ordenados por valor gasto |
| TOP Produtos | `/api/produtos` | produtos ordenados por quantidade vendida |
| TOP Serviços | `/api/servicos` | serviços ordenados por quantidade vendida |

## ✅ Status de Implementação

Todos os endpoints necessários para a interface foram implementados no BFF:

- ✅ **4 endpoints principais** (faturamento, serviços, produtos, fidelidade)
- ✅ **1 endpoint de processamento** (faturamento/process)
- ✅ **Autenticação global** via middleware
- ✅ **Modelos de resposta padronizados**
- ✅ **Tratamento de erros consistente**

## 🔍 Observações

1. **Endpoint de faturamento** é o mais complexo, retornando múltiplos tipos de dados para diferentes visualizações
2. **Endpoints de produtos e serviços** são mais específicos, focados em rankings
3. **Endpoint de fidelidade** foca em dados de clientes
4. **Todos os endpoints** seguem o mesmo padrão de autenticação e resposta
5. **Parâmetro `month`** é obrigatório em todos os endpoints para filtragem temporal
