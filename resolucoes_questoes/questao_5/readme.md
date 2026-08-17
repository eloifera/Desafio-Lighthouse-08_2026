# 🗓️ Questão 5 - Análise de Vendas com Dimensão de Calendário

## 📌 Visão Geral do Projeto

Dando continuidade ao pipeline de dados da empresa fictícia **LH Nautical**, esta etapa realiza a **Análise de Vendas com Dimensão de Calendário** — Cria uma **Dimensão de Calendário Contínua** para gerar todos os dias corridos entre a **menor** e a **maior** data registradas no canal físico `pos`. Agrupa as vendas diárias por data na loja física. Preenche os dias sem venda com R$ 0,00. Traduz os dias da semana para o português (Segunda-feira, Terça-feira, etc.) e calcula a média real diária.

---

## 📁 Estrutura de Arquivos da Questão 5

Na pasta `resolucoes_questoes/questao_5`, encontram-se os seguintes arquivos:

```text
📁 resolucoes_questoes/questao_5/
├── consulta_q5_1.sql # Consulta SQL da Questão 5.1, dimensão de calendário contínua
└── readme.md         # Este arquivo que você está lendo, uma documentação técnica simples da solução
```
