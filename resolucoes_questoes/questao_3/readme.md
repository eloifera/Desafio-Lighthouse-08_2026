# 🐘 Questão 3 - Ingestão de Dados no PostgreSQL (Carregamento CSV)

## 📌 Visão Geral do Projeto

Dando continuidade ao pipeline de dados da empresa fictícia **LH Nautical**, esta etapa realiza a **ingestão dos dados brutos** — contidos nos **24 arquivos CSV** — diretamente no banco de dados **PostgreSQL**, respeitando o schema DDL gerado na Questão 2 (`schema.sql`).

O script `carregar_dados.py` conecta-se ao PostgreSQL, cria as tabelas seguindo o schema definido, carrega todos os arquivos CSV em lote e, por fim, aplica as restrições de integridade referencial (Foreign Keys) via `ALTER TABLE`.

---

## 🎯 Premissas e Restrições Obrigatórias Atendidas

- **Fonte de Dados:** Todos os arquivos `.csv` presentes na mesma pasta do script são considerados como fonte primária.
- **Schema Pré-definido:** O script depende do arquivo `schema.sql` (gerado na Questão 2) para criação das tabelas.
- **Python 3 utilizado:** Desenvolvido utilizando **bibliotecas do Python 3** (`csv`, `os`, `psycopg2`).
- **Banco Alvo PostgreSQL:** A ingestão é feita diretamente via conexão `psycopg2`, sem uso de ORMs ou ferramentas de terceiros além dessa biblioteca.
- **Preservação de Dados Brutos:** Valores vazios nos CSVs são convertidos para `NULL` no banco; nenhum dado Nulo é alterado ou truncado durante a ingestão.

---

## 📁 Estrutura de Arquivos da Questão 3

Na pasta `resolucoes_questoes/questao_3`, encontram-se os seguintes arquivos:

```text
📁 resolucoes_questoes/questao_3/
├── carregar_dados.py   # Script Python para ingestão dos CSVs no PostgreSQL
└── readme.md           # Este arquivo que você está lendo, uma documentação técnica e linha de raciocínio da solução
```

---

## 🧠 Linha de Raciocínio e Decisões de Arquitetura

O desenvolvimento do script `carregar_dados.py` foi guiado pelas seguintes etapas e decisões técnicas:

```text
                  ┌─────────────────────────────────────────┐
                  │    schema.sql + Arquivos CSV Brutos     │
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
                  │       2. Etapa 1/3 — CREATE TABLE       │
                  │   (Criação das tabelas base sem FKs)    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │      3. Etapa 2/3 — INSERT em Lote      │
                  │ (Insere os dados dos CSV no PostgreSQL) │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │     4. Etapa 3/3 — ALTER TABLE (FKs)    │
                  │        (Aplicação das foreign keys)     │
                  └─────────────────────────────────────────┘
```

---

### 1. Configuração de Conexão por Variáveis de Ambiente

O script lê as credenciais do PostgreSQL a partir de **variáveis de ambiente**, com valores padrão definidos como *fallback* para execução local. Isso permite que o mesmo script seja executado tanto em ambiente de desenvolvimento quanto em pipelines automatizados sem alteração de código.

| Variável de Ambiente | Constante no Script | Valor Padrão |
| --- | --- | --- |
| `PGHOST` | `PG_HOST` | `localhost` |
| `PGPORT` | `PG_PORT` | `5432` |
| `PGDATABASE` | `PG_DB` | `postgres` |
| `PGUSER` | `PG_USER` | `postgres` |
| `PGPASSWORD` | `PG_PASS` | `postgres` |

---

### 2. Resolução Dinâmica de Caminhos

Assim como na Questão 2, o script não possui caminhos fixos (*hardcoding*). Ele resolve automaticamente o diretório em que está localizado via `os.path.abspath(__file__)`, garantindo que `schema.sql` e os arquivos `.csv` sejam sempre lidos a partir da **mesma pasta do script**.

---

### 3. Divisão Inteligente do Schema em Duas Etapas

O `schema.sql` contém dois blocos distintos de instruções SQL: os `CREATE TABLE` e os `ALTER TABLE` (Foreign Keys). O script divide o conteúdo do arquivo na **primeira ocorrência** de `ALTER TABLE`, separando as etapas propositalmente.

Esse design é fundamental para garantir a **ordem correta de execução**:

1. Primeiro, criar todas as tabelas base (sem restrições relacionais).
2. Depois, popular todas as tabelas com dados.
3. Por último, aplicar as Foreign Keys — que só podem ser validadas após os dados estarem presentes nas tabelas referenciadas.

---

### 4. Ingestão em Lote com `executemany`

Para cada arquivo `.csv` encontrado no diretório, o script:

- Extrai o nome da tabela a partir do nome do arquivo (sem extensão).
- Lê o CSV usando `csv.DictReader`, preservando os cabeçalhos como nomes de colunas.
- Converte campos vazios `""` em `None` (equivalente ao `NULL` do SQL), preservando os dados brutos.
- Constrói dinamicamente o `INSERT INTO` com os nomes de colunas entre aspas (evitando conflito com palavras reservadas do SQL).
- Executa a inserção em lote com `cursor.executemany()` para máxima performance.

---

### 5. Tratamento de Erros e Rollback de Segurança

O script implementa um bloco `try/except/finally` robusto que cobre os principais cenários de falha:

| Exceção Capturada | Cenário |
| --- | --- |
| `psycopg2.Error` | Falha na conexão ou erro durante execução SQL |
| `FileNotFoundError` | CSV ou diretório não encontrado |
| `PermissionError` | Sem permissão de leitura no arquivo |
| `UnicodeDecodeError` | Arquivo CSV não está em `utf-8` |
| `csv.Error` | Arquivo CSV malformado |

Em qualquer falha durante a ingestão, o script executa `conn.rollback()` para desfazer todas as alterações parciais, garantindo a **integridade transacional** do banco de dados. O bloco `finally` garante que a conexão seja sempre fechada ao final, independentemente do resultado.

---

## ⚙️ Como Executar o Script

### Pré-requisitos

1. **Python 3** instalado no sistema.
2. **PostgreSQL** rodando localmente (ou acessível via rede).
3. Instalar a biblioteca `psycopg2`:

```bash
pip install psycopg2-binary
```

1. Copiar para a **mesma pasta** do script:
   - O arquivo `schema.sql`
   - Todos os **arquivos `.csv`**

### Configuração das Credenciais (Opcional)

Se o seu PostgreSQL **não usa as credenciais padrão** (`localhost / 5432 / postgres / postgres`), defina as variáveis de ambiente antes de executar:

```bash
# Linux / macOS
export PGHOST=seu_host
export PGPORT=5432
export PGDATABASE=nome_do_banco
export PGUSER=seu_usuario
export PGPASSWORD=sua_senha
```

```powershell
# Windows (PowerShell)
$env:PGHOST="seu_host"
$env:PGPORT="5432"
$env:PGDATABASE="nome_do_banco"
$env:PGUSER="seu_usuario"
$env:PGPASSWORD="sua_senha"
```

### Execução

Abra um terminal a partir da pasta do script e execute:

```bash
# Execução direta no terminal
python carregar_dados.py
```

> **Atenção:** O banco de dados **não pode conter tabelas pré-existentes** com os mesmos nomes das tabelas do `schema.sql`. Caso existam, crie um banco limpo ou remova as tabelas antes de executar o script.
