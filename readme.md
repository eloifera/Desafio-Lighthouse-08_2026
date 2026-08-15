# ⚓ Resolução do Desafio Lighthouse de 08/2026

* **Candidato:** Eloi Ferreira
* **Empresa Fictícia:** LH Nautical
* **Área:** Dados e IA

---

## 📌 Sobre o Repositório

Neste repositório, você encontrará a resolução completa e detalhada de cada uma das 7 questões do **Desafio Lighthouse** de Agosto de 2026, organizadas na pasta [`resolucoes_questoes/`](./resolucoes_questoes/).
Cada subpasta contém a solução técnica acompanhada de documentação explicativa (`README.md` ou `notebook.ipynb`), além de todos os scripts de código, modelos e arquivos de apoio necessários para auditoria e reprodução dos resultados

---

## 🛠️ Tecnologias e Recursos Utilizados

### 💻 IDEs e Ambientes de Desenvolvimento

* **VS Code** (Visual Studio Code)
* **Antigravity IDE**
* **Jupyter Notebook** (Ambiente interativo de análise)

### 🐳 Contêineres e Banco de Dados

* **Docker** (Execução de container do **PostgreSQL**)
* **PostgreSQL** (Banco de dados relacional do projeto)
* **SQLite 3** (Banco relacional para pré desenvolvimento local e validações)

### 🗄️ Gerenciadores e Clientes de Banco de Dados (GUI)

* **DBeaver**
* **DataGrip**

### 🐍 Linguagens e Bibliotecas

* **Python 3.13.7**
  * *Bibliotecas Nativas:* `csv`, `os`, `re`, `sqlite3`
  * *Bibliotecas Externas:* `pandas`, `numpy`
* **SQL** (ANSI SQL / PostgreSQL Dialect)

---

## 📁 Estrutura do Repositório

```text
.
├── README.md                           <-- Documentação principal do repositório
└── resolucoes_questoes/                <-- Pasta contendo a entrega de todas as questões
    ├── questao_1/                      <-- Análise Exploratória de Dados (EDA)
    ├── questao_2/                      <-- Modelagem e Geração do Schema SQL
    ├── questao_3/                      <-- Ingestão e Carga dos CSVs no PostgreSQL
    ├── questao_4/                      <-- Análise de Clientes Fiéis (Elite)
    ├── questao_5/                      <-- Análise de Vendas com Dimensão de Calendário
    ├── questao_6/                      <-- Previsão de Demanda Mensal
    └── questao_7/                      <-- Sistema de Recomendação por Similaridade de Cosseno
