"""
Script Python de Carregamento de CSVs no PostgreSQL seguindo o schema.sql fornecido.

Recomendações:
- O Banco Postgre não pode conter tabelas pré-existentes com o mesmo nome das tabelas do schema.sql.
- Caso haja tabelas pré-existentes, recomenda-se
    -criar um banco de dados limpo ou
    -remover as tabelas existentes antes de executar este script.

Este script realiza as seguintes operações:
1. Conecta-se diretamente ao banco de dados PostgreSQL.
2. Cria primeiro todas as tabelas base (CREATE TABLE).
3. Ingestão de Dados: Carrega os arquivos CSV em lote (executemany)
preservando nulos e caracteres brutos intactos.
4. Aplica todas as constraints de Foreign Key (ALTER TABLE) diretamente do arquivo SQL.

Premissas Respeitadas:
- O arquivo 'schema.sql' e os arquivos '.csv' ficam na MESMA PASTA do script.
- Banco de Destino: PostgreSQL (banco padrão 'postgres' ou via variáveis de ambiente).
- Utiliza Python 3 com a biblioteca 'psycopg2'.

Lembre-se de instalar a biblioteca 'psycopg2' antes de executar o script e definir
as variáveis de conexão do PostgreSQL, se necessário, pelas constantes PG_HOST,
PG_PORT, PG_DB, PG_USER e PG_PASS.
"""

import csv
import os
import psycopg2

# ------------------------------------------------------------------------------
# CONFIGURAÇÃO DE CONEXÃO COM O BANCO DE DADOS POSTGRESQL
# ------------------------------------------------------------------------------
PG_HOST = os.getenv(
    "PGHOST", "localhost"
)  # define o host do PostgreSQL, padrão localhost
PG_PORT = os.getenv("PGPORT", "5432")  # define a porta do PostgreSQL, padrão 5432
PG_DB = os.getenv(
    "PGDATABASE", "postgres"
)  # define o nome do banco de dados, padrão postgres
PG_USER = os.getenv(
    "PGUSER", "postgres"
)  # define o usuário do PostgreSQL, padrão postgres
PG_PASS = os.getenv(
    "PGPASSWORD", "postgres"
)  # define a senha do PostgreSQL, padrão postgres


# ------------------------------------------------------------------------------
# RESOLUÇÃO DE CAMINHOS NA MESMA PASTA DO SCRIPT
# ------------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)  # define o diretório do script atual
SCHEMA_SQL_PATH = os.path.join(
    SCRIPT_DIR, "schema.sql"
)  # define o que o diretório do script é o mesmo do schema.sql
CSV_DIR = SCRIPT_DIR  # define que o diretório dos arquivos CSV e do script é o mesmo


def carregar_dados_postgresql():
    """
    Função principal para carregar os dados dos arquivos CSV no PostgreSQL
    seguindo o schema definido no arquivo 'schema.sql'."""
    print("=" * 80)
    print("CARREGAMENTO DE TABELAS NO POSTGRESQL SEGUINDO SCHEMA")
    print("=" * 80)
    print(f" -> Diretorio dos CSVs: {CSV_DIR}")
    print(f" -> Arquivo de Schema:  {SCHEMA_SQL_PATH}\n")

    if not os.path.exists(SCHEMA_SQL_PATH):
        print(f"Erro: Arquivo de schema nao encontrado em '{SCHEMA_SQL_PATH}'.")
        return  # retorna erro caso o arquivo de schema não seja encontrado

    # Le o conteudo completo do schema
    with open(SCHEMA_SQL_PATH, mode="r", encoding="utf-8-sig") as f:
        conteudo_sql = f.read()

    # Divide o schema nas duas etapas principais (CREATE TABLEs e ALTER TABLEs)
    divisor_etapa_2 = "ALTER TABLE"  # Define o divisor entre as etapas
    if (
        divisor_etapa_2 in conteudo_sql
    ):  # Separa o conteúdo do schema em duas partes: antes e depois do divisor
        # O argumento '1' força o split a dividir APENAS na 1ª ocorrência
        partes = conteudo_sql.split(divisor_etapa_2, 1)
        sql_create_tables = partes[0]
        sql_foreign_keys = divisor_etapa_2 + partes[1]
    else:  # Se não houver ALTER TABLE, considera que não há FKs
        sql_create_tables = conteudo_sql
        sql_foreign_keys = None

    # 1. Conexao direta com o PostgreSQL
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
        )  # Conecta ao banco de dados PostgreSQL usando as variáveis de ambiente ou valores padrão
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        print(
            f" -> Conectado com sucesso ao PostgreSQL ({PG_HOST}:{PG_PORT}/{PG_DB})\n"
        )  # Imprime mensagem de sucesso na conexão
    except psycopg2.Error as e:
        print(f"Erro de conexao com o PostgreSQL: {e}")
        return  # Retorna erro caso haja erro na conexão

    try:
        arquivos_csv = sorted(
            [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
        )  # Lista e ordena todos os arquivos CSV no diretório definido

        # ----------------------------------------------------------------------
        # ETAPA 1: CRIACAO LIMPA DAS TABELAS BASE (SEM FKS)
        # ----------------------------------------------------------------------
        print(f" [1/3] Criando as {len(arquivos_csv)} tabelas base...")
        cursor.execute(sql_create_tables)  # Executa o SQL de criação das tabelas base
        conn.commit()  # Confirma as alterações no banco de dados
        print(f"       [OK] {len(arquivos_csv)} Tabelas criadas com sucesso.\n")

        # ----------------------------------------------------------------------
        # ETAPA 2: INGESTAO DOS 24 ARQUIVOS CSV EM LOTE
        # ----------------------------------------------------------------------
        total_linhas_geral = 0
        print(f" [2/3] Inserindo dados dos {len(arquivos_csv)} arquivos CSV em lote...")

        for arq in arquivos_csv:
            nome_tabela = os.path.splitext(arq)[
                0
            ]  # Extrai o nome da tabela a partir do nome do arquivo CSV
            caminho_csv = os.path.join(
                CSV_DIR, arq
            )  # Cria o caminho completo para o arquivo CSV

            with open(caminho_csv, mode="r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(
                    f
                )  # Cria um leitor de CSV que mapeia os dados para dicionários,
                # usando a primeira linha como cabeçalho
                colunas = (
                    reader.fieldnames or []
                )  # Obtém os nomes das colunas a partir do cabeçalho do CSV

                # Preserva dados brutos e converte vazios em None (SQL NULL)
                linhas = [
                    tuple(row[c] if row[c] != "" else None for c in colunas)
                    for row in reader
                ]

                colunas_quoted = ", ".join(
                    [f'"{c}"' for c in colunas]
                )  # Cria uma string com os nomes das colunas entre aspas, separados por vírgulas
                placeholders = ", ".join(
                    ["%s"] * len(colunas)
                )  # Cria uma string de placeholders (%s) para cada coluna, separados por vírgulas
                sql_insert = f'INSERT INTO "{nome_tabela}" ({colunas_quoted}) VALUES ({placeholders});'
                # Cria a instrução SQL de inserção de dados na tabela

                cursor.executemany(
                    sql_insert, linhas
                )  # Executa a inserção em lote de todas as linhas lidas
                # do CSV na tabela correspondente
                total_linhas_geral += len(
                    linhas
                )  # Atualiza o contador total de linhas inseridas no banco de dados
                print(
                    f"       [OK] '{nome_tabela:<26}': {len(linhas):>7} linhas inseridas."
                )

        conn.commit()  # Confirma todas as inserções no banco de dados
        print(
            f"\n       -> Ingestao concluida: {total_linhas_geral} linhas inseridas com sucesso.\n"
        )

        # ----------------------------------------------------------------------
        # ETAPA 3: APLICACAO DAS RESTRICOES DE FOREIGN KEY (ALTER TABLE)
        # ----------------------------------------------------------------------
        if (
            sql_foreign_keys
        ):  # Se houver instruções de ALTER TABLE no schema, aplica as Foreign Keys
            print(" [3/3] Aplicando Foreign Keys via ALTER TABLE...")
            cursor.execute(
                sql_foreign_keys
            )  # Executa as instruções de ALTER TABLE para aplicar as restrições de Foreign Key
            conn.commit()  # Confirma as alterações no banco de dados
            print(
                "       [OK] Todas as Foreign Keys foram aplicadas e validadas com sucesso.\n"
            )
        else:
            print(" [3/3] Nenhuma secao de ALTER TABLE separada detectada.\n")
            # retorna mensagem caso não haja instruções de ALTER TABLE no schema

        print("=" * 80)
        print(
            f"SUCESSO TOTAL: {len(arquivos_csv)} tabelas carregadas e relacionadas no PostgreSQL!"
        )
        print(f"TOTAL DE LINHAS CARREGADAS: {total_linhas_geral}")
        print("=" * 80)

    except FileNotFoundError as e: # erro caso o CSV ou diretório não seja encontrado
        print(f"\n[ERRO] Arquivo CSV ou diretório não encontrado: {e}")
        conn.rollback() # rollback para desfazer qualquer alteração feita antes do erro

    except PermissionError as e: # erro caso não haja permissão para ler o arquivo CSV
        print(f"\n[ERRO] Sem permissão para ler o arquivo: {e}")
        conn.rollback()  # rollback para desfazer qualquer alteração feita antes do erro

    except UnicodeDecodeError as e: # erro caso o arquivo CSV não possa ser decodificado
        print(f"\n[ERRO] Falha ao decodificar arquivo CSV (não está em utf-8): {e}")
        conn.rollback()  # rollback para desfazer qualquer alteração feita antes do erro

    except csv.Error as e: # erro caso o arquivo CSV esteja malformado
        print(f"\n[ERRO] Arquivo CSV malformado: {e}")
        conn.rollback()  # rollback para desfazer qualquer alteração feita antes do erro

    except psycopg2.Error as e: # erro caso haja algum problema com o banco de dados PostgreSQL
        print(f"\n[ERRO] Erro no banco de dados: {e}")
        conn.rollback()  # rollback para desfazer qualquer alteração feita antes do erro

    finally:
        cursor.close() # fecha o cursor do banco de dados
        conn.close() # fecha a conexão com o banco de dados


if __name__ == "__main__":
    carregar_dados_postgresql()
