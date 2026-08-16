# 🗄️ Questão 2 - Engenharia de Dados & Modelagem de Schema (PostgreSQL)

## 📌 Visão Geral do Projeto

Essa etapa a empresa fictícia **LH Nautical** recebe dados brutos extraídos do seu ERP através de **24 arquivos CSV**. Como o sistema de origem não permite conexão direta com a base de dados, a missão é estruturar a fundação do banco de dados relacional (Data Warehouse / Raw Stage) através da criação de um script automatizado de inferência de tipos e geração de DDL (`schema.sql`) para o **PostgreSQL**.

---

## 🎯 Premissas e Restrições Obrigatórias Atendidas

- **Arquivos de Fonte:** Considera todos os arquivos `.csv` da pasta como fonte primária.
- **Python 3 Puro (Sem bibliotecas externas):** Desenvolvido utilizando **exclusivamente bibliotecas padrão do Python 3** (`csv`, `os`, `re`). Nenhuma biblioteca de terceiros como `pandas`, `polars` ou `dask` foi utilizada.
- **Banco Alvo PostgreSQL:** Todos os tipos de dados gerados seguem as melhores práticas e tipos nativos do PostgreSQL (`INTEGER`, `BIGINT`, `NUMERIC`, `VARCHAR`, `TIMESTAMP`, `DATE`, `BOOLEAN`).
- **Geração de Arquivo Único:** Produz como saída o arquivo centralizado `schema.sql` pronto para execução.

---

## 📁 Estrutura de Arquivos da Questão 2

Na pasta `resolucoes_questoes/questao_2`, encontram-se os seguintes arquivos:

```text
📁 resolucoes_questoes/questao_2/
├── gerar_schema.py      # Script em Python puro para inferência de tipos e geração DDL
├── schema.sql           # Arquivo DDL com CREATE TABLE das 24 tabelas e constraints
└── readme.md            # Este arquivo que você está lendo, uma documentação técnica e linha de raciocínio da solução
```

---

## 🧠 Linha de Raciocínio e Decisões de Arquitetura

O desenvolvimento do script `gerar_schema.py` foi guiado pelas seguintes etapas e decisões técnicas:

```text
                  ┌────────────────────────────────────────┐
                  │     Entrada de  Arquivos CSV Brutos    │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    1. Leitura e Amostragem Dinâmica    │
                  │   (Varredura de colunas e valores)     │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │  2. Motor de Inferência de Tipos PG    │
                  │  • Identificadores Textuais (VARCHAR)  │
                  │  • Datas e Timestamps (Regex)          │
                  │  • Booleans & Numéricos (INT/NUMERIC)  │
                  │  • Dimensionamento Inteligente Strings │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │  3. Mapeamento de PKs e Foreign Keys   │
                  │  • PK simples (`id`) e compostas (N:N) │
                  │  • Integridade referencial semântica   │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │     schema.sql (Para PostgreSQL)       │
                  └────────────────────────────────────────┘
```

---

### 1. Detecção Dinâmica e Resolução de Caminhos

O código não possui listas fixas de tabelas (*hardcoding*). Ele varre dinamicamente o diretório onde se encontram os arquivos `.csv`, permitindo que novos arquivos sejam incorporados automaticamente sem necessidade de refatoração do código.

---

### 2. Motor de Inferência de Tipos de Dados (Type Inference Engine)

A inferência analisa os registros válidos de cada coluna para garantir que o tipo atribuído suporte 100% dos dados sem perda de precisão. A avaliação segue a seguinte ordem de precedência:

1. **Chave Primária Simples (`id`):**
   - A coluna `id` é automaticamente declarada como `INTEGER PRIMARY KEY`.
2. **Identificadores Textuais Cadastrais (Proteção contra Perda de Dados):**
   - Colunas como `tax_id` (CPF/CNPJ), `postal_code` (CEP), `phone`, `barcode_ean`, `ncm_code`, `nfe_access_key` e `sku` contêm apenas números em muitos registros, mas **não podem ser convertidas em inteiros** para evitar a remoção de zeros à esquerda (ex: CEP `01310-100` virar `1310100`). Essas colunas são forçadas para `VARCHAR`. Eles são definidos pela constante `TEXT_IDENTIFIER_KEYWORDS` no script, que pode ser ajustada conforme a convenção de nomenclatura da empresa.
3. **Data e Hora (`TIMESTAMP` e `DATE`):**
   - Utilização de Expressões Regulares (`re`) para detectar padrões ISO:
     - Formato `YYYY-MM-DD HH:MM:SS` ➔ `TIMESTAMP`
     - Formato `YYYY-MM-DD` ➔ `DATE`
4. **Booleanos (`BOOLEAN`):**
   - Reconhecimento de valores lógicos (`true`/`false`, `t`/`f`).
5. **Numéricos Inteiros (`INTEGER` vs `BIGINT`):**
   - Testa a conversão inteira e avalia o valor absoluto máximo. Valores que excedem o limite de 32 bits (`2.147.483.647`) recebem `BIGINT`; caso contrário, `INTEGER`.
6. **Numéricos Decimais e Monetários (`NUMERIC(12, 2)` / `NUMERIC(12, 3)`):**
   - Valores com ponto flutuante recebem tipo `NUMERIC` com precisão controlada, ideal para finanças, estoques e cálculos de impostos (ICMS, IPI), evitando problemas de arredondamento de dízimas inerentes ao tipo `FLOAT`.
7. **Texto e Strings (`VARCHAR` / `TEXT`):**
   - Calculado com base no maior comprimento observado na coluna: `VARCHAR(50)`, `VARCHAR(255)` ou `TEXT`.

---

### 3. Modelagem Relacional & Chaves Estrangeiras (Foreign Keys)

O script mapeia as convenções de nomenclatura corporativa (`entidade_id`) para construir os relacionamentos relacionais:

- O script identifica colunas que representam **Foreign Keys** e gera as constraints correspondentes no DDL. Seguindo valores definidos na variável `mapeamentos_especificos` no script, que pode ser ajustada conforme a convenção de nomenclatura da empresa. Detectando relacionamentos de **Fluxo Comercial, Catálogo de Produtos e Hierarquias de Categorias**.
- Além disso, o script também identifica e cria **Hierarquia Auto-Referenciada e Tabelas Associativas N:N** por meio da constante `TABELAS_JUNCAO_PK`(Chaves primárias compostas para garantir unicidade).

---

## 💻 Como Executar o Script

Certifique-se de estar com o Python 3 instalado no sistema. Não é necessário instalar nenhum pacote via `pip`. Abra um terminal a partir da pasta do script e execute o seguinte comando:

```bash
# Execução direta no terminal
python gerar_schema.py
```

O script realizará a leitura dos arquivos CSV presentes no seu diretório e gerará o arquivo `schema.sql` no mesmo diretório. Caso não haja arquivos CSV no diretório,o script exibirá uma mensagem de erro e encerrará a execução.
