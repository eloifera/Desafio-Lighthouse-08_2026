# 📊 Questão 1 - Análise Exploratória de Dados (EDA)

## 📌 Visão Geral do Projeto

Esta etapa tem como objetivo realizar a **Análise Exploratória de Dados (EDA)** sobre a tabela `orders` da empresa fictícia **LH Nautical**, respondendo às dúvidas do Sr. Almir a respeito da **confiabilidade, volume, distribuição e qualidade dos dados brutos** para tomada de decisão.

---

## 📁 Estrutura de Arquivos da Questão 1

Na pasta `resolucoes_questoes/questao_1`, você encontrará os seguintes arquivos:

```text
📁resolucoes_questoes/questao_1/
├── eda_inicial.ipynb
├── consulta_q1_1.sql
└── orders.sqlite
└── readme.md
```

### 📄 Descrição dos Arquivos

1. **`eda_inicial.ipynb`**: Notebook Jupyter interativo com:
   * Conexão e ingestão do CSV no banco SQLite.
   * Consultas SQL executadas usando biblioteca nativa do Python `sqlite3`.
   * Diagnóstico explicativo estruturado para apresentação executiva.
2. **`consulta_q1_1.sql`**: Script em ANSI SQL padrão contendo a consulta agregada das métricas da Questão 1.1 (`COUNT`, `MIN`, `MAX`, `AVG`).
3. **`orders.sqlite`**: Arquivo .sqlite leve contendo a tabela `orders` para consulta rápida no DBeaver/DataGrip.
4. **`readme.md`**: Este arquivo que você está lendo, fornecendo uma visão geral do projeto e instruções de uso.
