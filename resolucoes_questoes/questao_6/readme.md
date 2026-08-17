# 📈 Questão 6 - Previsão de Demanda Mensal (Modelo Baseline)

## 📌 Visão Geral do Projeto

Dando continuidade às análises da empresa fictícia **LH Nautical**, esta etapa desenvolve um **modelo preditivo baseline de demanda mensal** para o produto **"Bússola de Bordo 702"**, para apoiar a diretoria no planejamento de compras com fornecedores e evitar problemas de estoque.

O script `previsao_demanda_q6.py` conecta-se ao banco de dados **PostgreSQL**, realiza a junção das tabelas de produtos, variantes e vendas, constrói uma série temporal mensal, aplica a **Média Móvel de 3 Meses (MA3) de forma autoregressiva** para o 1º trimestre de 2026 e calcula o erro absoluto médio (**MAE**).

---

## 🎯 Premissas Atendidas

- **Produto Analisado:** Exclusivamente o produto **"Bússola de Bordo 702"**.
- **Datasets Unificados:** Junção relacional das 4 tabelas exigidas: `products`, `product_variants`, `orders` e `order_items`.
- **Período de Treino:** Histórico transacional completo de vendas até **31/12/2025**.
- **Período de Teste:** O primeiro trimestre de 2026 (`Jan/2026`, `Fev/2026` e `Mar/2026`).
- **Granularidade:** Previsão agregada em base mensal (`YYYY-MM`).
- **Modelo Baseline:** Média Móvel dos últimos 3 meses (MA3) calculada de forma autoregressiva sem dados do futuro (*zero data leakage*).
- **Métrica de Avaliação:** **MAE (Mean Absolute Error)** para mensuração da acurácia preditiva.

---

## 📁 Estrutura de Arquivos da Questão 6

Na pasta `resolucoes_questoes/questao_6`, encontram-se os seguintes arquivos:

```text
📁 resolucoes_questoes/questao_6/
├── previsao_demanda_q6.py   # Script Python para a previsão de demanda mensal no PostgreSQL
└── readme.md                 # Este arquivo que você está lendo, uma documentação técnica da solução
```

---

## 🧠 Linha de Raciocínio e Decisões de Arquitetura

O desenvolvimento do script `previsao_demanda_q6.py` foi guiado pelas seguintes etapas e decisões técnicas:

```text
                  ┌─────────────────────────────────────────┐
                  │              script Python              │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       1. Conexão com o PostgreSQL       │
                  │  (via psycopg2 + variáveis de ambiente) │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │      2. Unificação & Série Temporal     │
                  │   (Filtragem "Bússola de Bordo 702")    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │     3. Modelo Autoregressivo MA3        │
                  │        (Média Móvel de 3 Meses)         │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │      4. Cálculo do MAE & Avaliação      │
                  │     (Métrica de Erro Absoluto Médio)    │
                  └─────────────────────────────────────────┘
```

---

### 1. Configuração de Conexão por Variáveis de Ambiente

O script lê as credenciais do PostgreSQL a partir de **variáveis de ambiente**, com valores padrão definidos como *fallback* para execução local no Docker:

| Variável de Ambiente | Constante no Script | Valor Padrão |
| --- | --- | --- |
| `PGHOST` | `PG_HOST` | `localhost` |
| `PGPORT` | `PG_PORT` | `5432` |
| `PGDATABASE` | `PG_DB` | `postgres` |
| `PGUSER` | `PG_USER` | `postgres` |
| `PGPASSWORD` | `PG_PASS` | `postgres` |

---

### 2. Unificação Relacional e Agregação Temporal em SQL

Para construir o dataset de modelagem, executou-se uma consulta SQL que realiza o cruzamento das tabelas de negócio e agrupa o volume vendido por mês

---

### 3. Modelo Autoregressivo MA3

Para prever os 3 meses do primeiro trimestre de 2026 de forma estritamente realista, aplicou-se a abordagem **autoregressiva**. Isso significa que as previsões para os meses $t+1$ e $t+2$ utilizaram as próprias previsões geradas nos passos anteriores ($\hat{Y}$), em vez de consultar as vendas reais do futuro:

- **Janeiro/2026:** Média de (Out/25, Nov/25, Dez/25) $\rightarrow (25 + 54 + 19) / 3 = \mathbf{32,67\text{ un.}}$
- **Fevereiro/2026:** Média de (Nov/25, Dez/25, $\hat{Y}_{\text{Jan}}$) $\rightarrow (54 + 19 + 32,67) / 3 = \mathbf{35,22\text{ un.}}$
- **Março/2026:** Média de (Dez/25, $\hat{Y}_{\text{Jan}}$, $\hat{Y}_{\text{Fev}}$) $\rightarrow (19 + 32,67 + 35,22) / 3 = \mathbf{28,96\text{ un.}}$

---

## ⚙️ Como Executar o Script

### Pré-requisitos

1. **Python 3** instalado no sistema.
2. **PostgreSQL** rodando no Docker ou localmente com o banco `postgres` populado.
3. Instalar as bibliotecas necessárias:

```bash
pip install psycopg2-binary pandas numpy
```

### Configuração das Credenciais (Opcional)

Caso seu banco PostgreSQL não utilize as credenciais padrão (`localhost / 5432 / postgres / postgres`), defina as variáveis de ambiente antes da execução do script

### Execução

Abra um terminal na pasta do script e execute:

```bash
python previsao_demanda_q6.py
```
