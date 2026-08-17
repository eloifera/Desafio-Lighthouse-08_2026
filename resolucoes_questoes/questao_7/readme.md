# 🤖 Questão 7 - Sistema de Recomendação de Produtos (Similaridade de Cosseno)

## 📌 Visão Geral do Projeto

Dando continuidade às soluções de dados para a **LH Nautical**, esta etapa desenvolve um **Sistema de Recomendação de Produtos baseado em Filtragem Colaborativa Item-Item (Item-Item Collaborative Filtering)**. O objetivo é recomendar os produtos mais afins e frequentemente adquiridos em conjunto por clientes que compraram o produto **"Motor de Popa 1949"**, apoiando estratégias de *cross-selling* e personalização de ofertas na plataforma.

O script `sistema_recomendacao_q7.py` conecta-se ao banco de dados **PostgreSQL**, extrai os históricos de compras dos clientes, constrói uma **Matriz de Interação Usuário x Produto Binária**, calcula a **Similaridade de Cosseno** entre os vetores de produtos e gera o ranking dos 5 itens mais recomendados.

---

## 🎯 Premissas e Restrições Obrigatórias Atendidas

- **Produto de Referência:** Exclusivamente o produto **"Motor de Popa 1949"**.
- **Métrica de Similaridade:** **Similaridade de Cosseno (Cosine Similarity)** calculada sobre os vetores de co-ocorrência dos produtos.
- **Mapeamento de Transações:** Junção relacional das tabelas: `orders`, `order_items`, `product_variants` e `products`.
- **Tratamento de Ruídos:** Remoção automatizada de registros de teste/demonstração para garantir recomendações apenas de produtos válidos da loja.

---

## 📁 Estrutura de Arquivos da Questão 7

Na pasta `resolucoes_questoes/questao_7`, encontram-se os seguintes arquivos:

```text
📁 resolucoes_questoes/questao_7/
├── sistema_recomendacao_q7.py   # Script Python para o sistema de recomendação no PostgreSQL
└── readme.md                    # Este arquivo que você está lendo, uma documentação técnica da solução
```

---

## 🧠 Linha de Raciocínio e Decisões de Arquitetura

O desenvolvimento do script `sistema_recomendacao_q7.py` foi guiado pelas seguintes etapas e decisões técnicas:

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
                  │   2. Matriz Binária Usuário x Produto   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │   3. Matriz de Similaridade de Cosseno  │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │   4. Ranking Top 5 & Limpeza de Ruídos  │
                  │    (Recomendação "Motor de Popa 1949")  │
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

### 2. Matriz Usuário-Item Binária & Fórmula da Similaridade de Cosseno

A matriz de interação foi construída através de um produto cruzado (`pd.crosstab`) entre a lista única de clientes e os produtos comprados, convertido em matriz binária ($1$ se comprou pelo menos uma vez, $0$ caso contrário).

A Similaridade de Cosseno entre dois vetores de produtos $\mathbf{u}$ e $\mathbf{v}$ mede o cosseno do ângulo entre eles no espaço vetorial de clientes, variando entre $0.0$ (nenhuma co-ocorrência) e $1.0$ (co-ocorrência idêntica):

$$\text{Similaridade}(u, v) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|} = \frac{\sum_{i} u_i v_i}{\sqrt{\sum_i u_i^2} \sqrt{\sum_i v_i^2}}$$

---

## ⚙️ Como Executar o Script

### Pré-requisitos

1. **Python 3** instalado no sistema.
2. **PostgreSQL** rodando no Docker ou localmente com o banco `postgres` populado.
3. Instalar as bibliotecas necessárias:

```bash
pip install psycopg2-binary pandas numpy
```

### Execução

Abra um terminal na pasta do script e execute:

```bash
python sistema_recomendacao_q7.py
```
