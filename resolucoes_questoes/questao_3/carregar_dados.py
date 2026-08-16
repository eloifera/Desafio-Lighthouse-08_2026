"""
Script Python de Carregamento de CSVs no PostgreSQL seguindo o schema.sql fornecido.

Este script realiza as seguintes operações:
1. Conecta-se diretamente ao banco de dados PostgreSQL.
2. Cria tabelas e ingere 100% dos dados dos arquivos CSV
seguindo o schema.sql fornecido, preservando nulos e caracteres brutos intactos.
3. Lê o arquivo 'schema.sql' localizado na mesma pasta, extrai dinamicamente todas as declarações
   de Foreign Keys (REFERENCES) via Expressão Regular e as aplica no PostgreSQL após a carga.

Premissas Respeitadas:
- O arquivo 'schema.sql' e os arquivos '.csv' ficam na MESMA PASTA do script.
- Banco de Destino: PostgreSQL (banco padrão 'postgres' ou via variáveis de ambiente).
- Sem listas pré-escritas de tabelas ou fallbacks hardcodados.
- Utiliza Python 3 com a biblioteca 'psycopg2' e expressão regular 're'.

Lembre-se de instalar a biblioteca 'psycopg2' antes de executar o script e definir
as variáveis de conexão do PostgreSQL, se necessário, pelas constantes PG_HOST,
PG_PORT, PG_DB, PG_USER e PG_PASS.
"""

import csv
import os
import re
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


def ler_schema_sql():
    """Lê o conteúdo do arquivo schema.sql localizado na mesma pasta do script."""
    if not os.path.exists(SCHEMA_SQL_PATH):
        raise FileNotFoundError(
            f"Arquivo de schema não encontrado em: {SCHEMA_SQL_PATH}"
        )  # retornando erro caso o arquivo schema.sql não seja encontrado

    with open(SCHEMA_SQL_PATH, mode="r", encoding="utf-8-sig") as f:
        return f.read()  # retorna o conteúdo do arquivo schema.sql como uma string


def extrair_tabelas_e_fks_do_schema(conteudo_sql):
    """Extrai DDL das tabelas sem REFERENCES e lista de FKs a partir do schema.sql."""
    padrao_tabela = re.compile(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"?([A-Za-z_][A-Za-z0-9_]*)"?\s*\((.*?)\)\s*;',
        re.DOTALL | re.IGNORECASE,
    )  # Cria um padrão regex para identificar a criação de tabelas no
    # schema.sql, capturando o nome da tabela e seu corpo (colunas e constraints).

    padrao_fk_inline = re.compile(
        r'^\s*"?([A-Za-z_][A-Za-z0-9_]*)"?\s+.+?\s+REFERENCES\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s*\(\s*"?([A-Za-z_][A-Za-z0-9_]*)"?\s*\)\s*(.*)$',
        re.IGNORECASE,
    )  # Cria um padrão regex para identificar Foreign Keys inline nas colunas das tabelas,
    # capturando coluna de origem, tabela de destino, coluna de destino e qualquer sufixo adicional
    # (como ON DELETE/UPDATE).

    padrao_remove_references = re.compile(
        r'\s+REFERENCES\s+"?[A-Za-z_][A-Za-z0-9_]*"?\s*\(\s*"?[A-Za-z_][A-Za-z0-9_]*"?\s*\)\s*(?:ON\s+DELETE\s+[A-Z\s]+)?\s*(?:ON\s+UPDATE\s+[A-Z\s]+)?',
        re.IGNORECASE,
    )  # Cria um padrão regex para remover a parte de REFERENCES das
    # linhas de definição de colunas, incluindo possíveis cláusulas ON DELETE/UPDATE.

    tabelas_sem_fk = (
        {}
    )  # Dicionário para armazenar o DDL das tabelas sem as constraints de Foreign Key.
    foreign_keys = (
        []
    )  # Lista para armazenar informações sobre as Foreign Keys extraídas do schema.sql.

    for match in padrao_tabela.finditer(conteudo_sql):
        nome_tabela = match.group(1)
        corpo_tabela = match.group(
            2
        )  # Captura o corpo da tabela (colunas e constraints) para processamento posterior.

        linhas_limpa = []
        for linha in corpo_tabela.splitlines():
            original = linha.strip()
            if not original:
                continue  # Ignora linhas vazias no corpo da tabela.

            linha_sem_virgula = original.rstrip(
                ","
            )  # Remove a vírgula final da linha, se presente, para facilitar a análise.
            m_fk = padrao_fk_inline.match(
                linha_sem_virgula
            )  # Verifica se a linha corresponde ao padrão de Foreign Key inline.

            if (
                m_fk
            ):  # Se a linha corresponde a uma Foreign Key inline, extrai as informações relevantes.
                coluna_origem = m_fk.group(1)
                tabela_destino = m_fk.group(2)
                coluna_destino = m_fk.group(3)
                sufixo = (
                    m_fk.group(4) or ""
                ).strip()  # Captura qualquer sufixo adicional (como ON DELETE/UPDATE)
                # e remove espaços em branco.

                foreign_keys.append(
                    {
                        "tabela_origem": nome_tabela,
                        "coluna_origem": coluna_origem,
                        "tabela_destino": tabela_destino,
                        "coluna_destino": coluna_destino,
                        "sufixo": sufixo,
                    }
                )  # Adiciona as informações da Foreign Key à lista de foreign_keys
                # para aplicação posterior.

                linha_base = padrao_remove_references.sub("", linha_sem_virgula).strip()
                if sufixo:
                    linha_base = f"{linha_base} {sufixo}".strip()
                linhas_limpa.append(
                    linha_base
                )  # Adiciona a linha limpa (sem REFERENCES) à lista de linhas_limpa
                # para reconstruir o DDL da tabela sem Foreign Keys.
            else:
                linhas_limpa.append(
                    linha_sem_virgula
                )  # Se a linha não for uma Foreign Key inline, adiciona-a diretamente
                # à lista de linhas_limpa.

        ddl = (
            f'CREATE TABLE IF NOT EXISTS "{nome_tabela}" (\n'
            + ",\n".join([f"    {l}" for l in linhas_limpa])
            + "\n);"
        )  # Reconstrói o DDL da tabela sem as constraints de Foreign Key,
        # utilizando as linhas limpas.
        tabelas_sem_fk[nome_tabela] = (
            ddl  # Adiciona o DDL da tabela sem Foreign Keys ao dicionário tabelas_sem_fk.
        )

    return tabelas_sem_fk, foreign_keys


def recriar_tabelas_sem_fks(cursor, tabelas_sem_fk):
    """Recria todas as tabelas usando o schema, porém sem as constraints de FK."""
    for nome_tabela in tabelas_sem_fk:
        cursor.execute(
            f'DROP TABLE IF EXISTS "{nome_tabela}" CASCADE;'
        )  # Remove a tabela se ela já existir.

    for ddl in tabelas_sem_fk.values():
        cursor.execute(
            ddl
        )  # Executa o DDL para criar a tabela sem as constraints de Foreign Key.


def aplicar_fks_dinamicas(cursor, conn, foreign_keys):
    """Aplica as FKs extraídas do schema.sql após carga dos dados."""
    print(" -> Aplicando Foreign Keys no PostgreSQL...")

    fks_aplicadas = (
        0  # Contador para rastrear o número de Foreign Keys aplicadas com sucesso.
    )
    falhas = (
        []
    )  # Lista para armazenar mensagens de erro caso a aplicação de uma Foreign Key falhe.

    for fk in foreign_keys:
        nome_constraint = f"fk_{fk['tabela_origem']}_{fk['coluna_origem']}"
        sufixo = f" {fk['sufixo']}" if fk["sufixo"] else ""
        # Tenta aplicar a Foreign Key no banco de dados, utilizando um savepoint
        # para permitir rollback em caso de falha.
        try:
            cursor.execute("SAVEPOINT sp_fk;")
            cursor.execute(
                f'ALTER TABLE "{fk["tabela_origem"]}" '
                f'DROP CONSTRAINT IF EXISTS "{nome_constraint}";'
            )  # Remove a constraint existente, se houver, para evitar conflitos.
            cursor.execute(
                f'ALTER TABLE "{fk["tabela_origem"]}" '
                f'ADD CONSTRAINT "{nome_constraint}" '
                f'FOREIGN KEY ("{fk["coluna_origem"]}") '
                f'REFERENCES "{fk["tabela_destino"]}"("{fk["coluna_destino"]}"){sufixo};'
            )  # Adiciona a nova Foreign Key ao banco de dados,
            # utilizando as informações extraídas do schema.sql.
            cursor.execute(
                "RELEASE SAVEPOINT sp_fk;"
            )  # Libera o savepoint após a aplicação bem-sucedida da Foreign Key.
            fks_aplicadas += 1
        except psycopg2.Error as e:
            cursor.execute(
                "ROLLBACK TO SAVEPOINT sp_fk;"
            )  # Reverte para o savepoint em caso de falha na aplicação da Foreign Key.
            cursor.execute(
                "RELEASE SAVEPOINT sp_fk;"
            )  # Libera o savepoint após o rollback para evitar bloqueios.
            falhas.append(
                f"{nome_constraint}: {e}"
            )  # Adiciona a mensagem de erro à lista de falhas para posterior exibição.

    conn.commit()

    print(f" -> {len(foreign_keys)} Foreign Keys extraídas do 'schema.sql'.")
    print(f" -> {fks_aplicadas} Foreign Keys aplicadas com sucesso.")

    if falhas:
        print(f" -> {len(falhas)} Foreign Keys falharam ao aplicar:")
        for falha in falhas:
            print(f"    - {falha}")
    print()


def carregar_dados_postgresql():
    """Carrega os arquivos CSV no PostgreSQL seguindo o schema.sql fornecido."""
    print("=" * 80)
    print("CARREGAMENTO DE CSVS E SCHEMA NO POSTGRESQL")
    print("=" * 80)
    print(f" -> Diretório do script e arquivos: {SCRIPT_DIR}\n")

    try:
        conteudo_sql = (
            ler_schema_sql()
        )  # Lê o conteúdo do arquivo schema.sql localizado
        # na mesma pasta do script.
        tabelas_sem_fk, foreign_keys = extrair_tabelas_e_fks_do_schema(
            conteudo_sql
        )  # Extrai o DDL das tabelas sem as constraints de Foreign Key e a lista de Foreign Keys
        # a partir do conteúdo do schema.sql.
    except FileNotFoundError as e:
        print(
            f"Arquivo do schema não encontrado: {e}"
        )  # Retorna erro caso o arquivo schema.sql não seja encontrado.
        return
    except OSError as e:
        print(
            f"Erro de leitura do schema: {e}"
        )  # Retorna erro caso ocorra algum problema ao ler o arquivo schema.sql.
        return
    except re.error as e:
        print(
            f"Erro na expressão regular do schema: {e}"
        )  # Retorna erro caso ocorra algum problema na expressão regular
        # utilizada para extrair as tabelas e Foreign Keys do schema.sql.
        return
    except ValueError as e:
        print(
            f"Dados do schema inválidos: {e}"
        )  # Retorna erro caso os dados extraídos do
        # schema.sql sejam inválidos ou inconsistentes.
        return

    print(
        " -> Analisando 'schema.sql' e extraindo estrutura e Foreign Keys dinamicamente..."
    )
    print(f" -> {len(tabelas_sem_fk)} tabelas extraídas para criação sem FKs.")
    print(f" -> {len(foreign_keys)} Foreign Keys extraídas para aplicação posterior.\n")

    # 1. Conexão direta com o PostgreSQL
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
        )
        cursor = conn.cursor()
        print(
            f" -> Conectado com sucesso ao PostgreSQL ({PG_HOST}:{PG_PORT}/{PG_DB})\n"
        )  # Indica que a conexão com o banco de dados PostgreSQL foi estabelecida com sucesso.
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return  # Retorna da função caso ocorra um erro na conexão com o banco de dados.

    try:
        print(" -> Recriando tabelas a partir do schema.sql (sem FKs)...\n")
        recriar_tabelas_sem_fks(cursor, tabelas_sem_fk)
        conn.commit()  # Confirma as alterações no banco de dados após
        # recriar as tabelas sem as constraints de Foreign Key.
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        print(f"Erro ao recriar tabelas sem FKs: {e}")
        return  # Retorna da função caso ocorra um erro ao recriar
        # as tabelas sem as constraints de Foreign Key.

    # 2. Carrega os 24 arquivos .csv da mesma pasta
    arquivos = sorted([f for f in os.listdir(CSV_DIR) if f.endswith(".csv")])
    total_linhas = 0

    print(" -> Criando tabelas e realizando o carregamento dos arquivos CSV:\n")

    for arq in arquivos:
        nome_tabela = os.path.splitext(arq)[
            0
        ]  # Obtém o nome da tabela a partir do nome do arquivo CSV (sem a extensão).
        caminho_csv = os.path.join(
            CSV_DIR, arq
        )  # Constrói o caminho completo para o arquivo CSV.

        with open(caminho_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(
                f
            )  # Cria um objeto DictReader para ler o arquivo CSV, permitindo
            # acessar os dados como dicionários.
            colunas = (
                reader.fieldnames or []
            )  # Obtém os nomes das colunas a partir do cabeçalho do arquivo CSV.

            # Preserva nulos (None) e dados brutos intactos
            linhas = [
                tuple(row[c] if row[c] != "" else None for c in colunas)
                for row in reader
            ]

            # Limpa dados antigos da tabela
            cursor.execute(
                f'DELETE FROM "{nome_tabela}";'
            )  # Remove todos os dados existentes
            # da tabela antes de inserir os novos dados do CSV.

            colunas_quoted = ", ".join(
                [f'"{c}"' for c in colunas]
            )  # Cria uma string com os nomes das colunas entre aspas, separadas por vírgulas,
            placeholders = ", ".join(
                ["%s"] * len(colunas)
            )  # Cria uma string de placeholders (%s) para cada coluna, separadas por vírgulas,

            sql_insert = f'INSERT INTO "{nome_tabela}" ({colunas_quoted}) VALUES ({placeholders})'
            # Cria a instrução SQL de inserção,
            # utilizando os nomes das colunas e os placeholders.
            cursor.executemany(
                sql_insert, linhas
            )  # Executa a instrução SQL de inserção para todas as linhas do CSV,

            count = len(
                linhas
            )  # Conta o número de linhas inseridas a partir do arquivo CSV.
            total_linhas += count
            print(
                f" [OK] Tabela '{nome_tabela:<26}': {count:>7} linhas inseridas no PostgreSQL."
            )

    conn.commit()  # Confirma as alterações no banco de dados após
    # a inserção de todas as linhas dos arquivos CSV.

    # 3. Extrai dinamicamente as Foreign Keys do schema.sql e as aplica no banco
    aplicar_fks_dinamicas(cursor, conn, foreign_keys)

    conn.close()  # Fecha a conexão com o banco de dados PostgreSQL após a conclusão do carregamento
    # e aplicação das Foreign Keys.

    print("-" * 80)
    print(
        f"SUCESSO: {len(arquivos)} tabelas carregadas no PostgreSQL ({total_linhas} linhas no total)."
    )
    print("=" * 80)


if __name__ == "__main__":
    carregar_dados_postgresql()
