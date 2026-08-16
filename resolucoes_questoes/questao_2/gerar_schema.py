"""
Gerador de Schema SQL com Foreign Keys Posteriores (PostgreSQL)

Este script:
1. Primeira Etapa: Gera todos os 'CREATE TABLE IF NOT EXISTS' sem restrições de Foreign Key inline.
    Isso permite que todas as tabelas sejam criadas em
    qualquer ordem, eliminando problemas de dependência circular.
2. Segunda Etapa: Acumula todas as restrições relacionais e as emite ao final do arquivo
    utilizando 'ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY (...) REFERENCES ...'.

Premissas Respeitadas:
- Utiliza Apenas bibliotecas padrão do Python 3 (csv, os, re).
- Gera DDL 100% compatível com PostgreSQL.
- Preserva identificadores textuais (tax_id, phone, postal_code, etc.) como VARCHAR.
- Define chaves primárias simples (id) e compostas para tabelas associativas N:N.

Personalização:
As seguintes constantes e variáveis podem ser ajustadas
    para atender a diferentes convenções de nomenclatura:
- A constante TEXT_IDENTIFIER_KEYWORDS (utilizada para identificar
    colunas específicas que serão tratadas como identificadores textuais)
- A constante TABELAS_JUNCAO_PK(utilizada para primary keys compostas para tabelas associativas N:N)
- A variável mapeamentos_especificos (utilizada para definir mapeamentos
    específicos do usuário para foreign keys)
"""

import csv
import os
import re

# 1. Pega a pasta onde o próprio script .py está salvo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. Verifica se existem arquivos .csv na mesma pasta do script
csvs_no_diretorio_atual = [f for f in os.listdir(SCRIPT_DIR) if f.endswith(".csv")]
if csvs_no_diretorio_atual:
    # Se encontrou CSVs na mesma pasta do script, usa o diretório atual automaticamente
    CSV_DIR = SCRIPT_DIR
else:
    # Caso não encontre, retorna erro:
    print("Nenhum arquivo .csv encontrado na pasta do script.")
    exit(1)
# O arquivo schema.sql será gerado na mesma pasta do script
OUTPUT_SQL = os.path.join(SCRIPT_DIR, "schema.sql")

# Lista de palavras-chave para identificar colunas que devem ser VARCHAR
TEXT_IDENTIFIER_KEYWORDS = [
    "postal_code",
    "zip",
    "cep",
    "phone",
    "telefone",
    "mobile",
    "tax_id",
    "cpf",
    "cnpj",
    "nfe",
    "access_key",
    "barcode",
    "ean",
    "ncm",
    "sku",
    "code",
]

# Constantes e Variáveis para personalização de convenções de nomenclatura
# Chaves primárias compostas para tabelas associativas N:N
TABELAS_JUNCAO_PK = {
    "product_suppliers": ["product_variant_id", "supplier_id"],
    "stock_levels": ["product_variant_id", "location_id"],
    "variant_attribute_values": ["product_variant_id", "attribute_id"],
}

# Mapeamentos específicos para Foreign Keys (quando o nome da coluna não segue a convenção padrão)
mapeamentos_especificos = {
    "salesperson": ("employees", "id"),
    "created_by_employee": ("employees", "id"),
    "received_by_employee": ("employees", "id"),
    "buyer": ("employees", "id"),
    "employee": ("employees", "id"),
    "customer": ("customers", "id"),
    "supplier": ("suppliers", "id"),
    "location": ("locations", "id"),
    "primary_location": ("locations", "id"),
    "destination_location": ("locations", "id"),
    "received_at_location": ("locations", "id"),
    "order": ("orders", "id"),
    "order_item": ("order_items", "id"),
    "product": ("products", "id"),
    "product_variant": ("product_variants", "id"),
    "exchange_variant": ("product_variants", "id"),
    "purchase_order": ("purchase_orders", "id"),
    "purchase_order_item": ("purchase_order_items", "id"),
    "goods_receipt": ("goods_receipts", "id"),
    "return": ("returns", "id"),
    "parent_category": ("categories", "id"),
    "category": ("categories", "id"),
    "brand": ("brands", "id"),
    "attribute": ("attributes", "id"),
}


def eh_identificador_textual(nome_coluna):
    """Verifica se o nome da coluna corresponde a um identificador ou documento textual."""
    nome_col = nome_coluna.lower()
    return any(kw in nome_col for kw in TEXT_IDENTIFIER_KEYWORDS)
    # Verifica se o nome da coluna contém alguma das palavras-chave definidas


def inferir_tipo_pg(nome_coluna, valores):
    """Infere o tipo de dado compatível com PostgreSQL com base nos valores observados."""
    if nome_coluna.lower() == "id":
        return "INTEGER PRIMARY KEY"
        # define que a coluna 'id' é a chave primária da tabela, caso exista.

    if eh_identificador_textual(nome_coluna):
        max_len = max([len(v) for v in valores if v != ""] or [50])
        tam_varchar = 50 if max_len <= 50 else (255 if max_len <= 255 else 500)
        return f"VARCHAR({tam_varchar})"
        # define que colunas com identificadores textuais (como CEP, telefone, CPF/CNPJ)
        # serão do tipo VARCHAR com tamanho apropriado.

    valores_validos = [v.strip() for v in valores if v != ""]
    if not valores_validos:
        return "VARCHAR(255)"
        # Se não houver valores válidos, assume-se VARCHAR(255) como padrão.

    regex_ts = re.compile(
        r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"
    )  # detecta timestamps no formato 'YYYY-MM-DD HH:MM:SS'
    regex_date = re.compile(
        r"^\d{4}-\d{2}-\d{2}$"
    )  # detecta datas no formato 'YYYY-MM-DD'

    if all(regex_ts.match(v) for v in valores_validos):
        return "TIMESTAMP"  # define que valores no formato 'YYYY-MM-DD HH:MM:SS' são TIMESTAMP.
    if all(regex_date.match(v) for v in valores_validos):
        return "DATE"  # define que colunas com valores no formato 'YYYY-MM-DD' serão do tipo DATE.

    if all(v.upper() in ["TRUE", "FALSE", "T", "F"] for v in valores_validos):
        return "BOOLEAN"
        # define que colunas com valores booleanos (TRUE/FALSE, T/F) serão do tipo BOOLEAN.
    eh_inteiro = True  # variavel para testar inteiros.
    eh_numeric = True  # variavel para testar números (inteiros ou decimais).

    for v in valores_validos:
        if eh_inteiro:
            try:
                int(v)
            except ValueError:
                eh_inteiro = False
                # Se não for possível converter para inteiro, marca como False.

        if eh_numeric:
            try:
                float(v)
            except ValueError:
                eh_numeric = False
                # Se não for possível converter para float, marca como False.

    if eh_inteiro:
        max_val = max(abs(int(v)) for v in valores_validos)
        return "BIGINT" if max_val > 2147483647 else "INTEGER"
        # define que valores inteiros serão do tipo INTEGER ou BIGINT dependendo do valor máximo.

    if eh_numeric:
        escala = 0
        digitos_inteiros = 1
        for v in valores_validos:
            if (
                "e" in v.lower()
            ):  # notação científica: cai no padrão conservado de escala mínima de 6 casas decimais.
                escala = max(escala, 6)
                continue
            parte_int, _, parte_dec = v.lstrip("+-").partition(".")
            escala = max(escala, len(parte_dec))
            digitos_inteiros = max(digitos_inteiros, len(parte_int))
        escala = min(max(escala, 2), 6)
        precisao = max(12, digitos_inteiros + escala)
        return f"NUMERIC({precisao}, {escala})"
        # define que colunas com valores numéricos decimais
        # serão do tipo NUMERIC com precisão e escala apropriadas.

    max_len = max(len(v) for v in valores_validos)
    if max_len <= 50:
        return "VARCHAR(50)"
    elif max_len <= 255:
        return "VARCHAR(255)"
    else:
        return "TEXT"
    # define que colunas com valores de texto serão
    # do tipo VARCHAR ou TEXT dependendo do tamanho máximo dos valores.


def obter_referencia_fk(nome_coluna, tabelas_existentes):
    """Mapeia dinamicamente a tabela e coluna de destino para colunas de chave estrangeira."""
    if not nome_coluna.endswith("_id") or nome_coluna == "id":
        return None
        # Se a coluna não termina com '_id' ou é a própria coluna 'id', não é considerada uma FK.

    entidade = nome_coluna[
        :-3
    ].lower()  # remove o sufixo '_id' para obter o nome da entidade relacionada.

    if (
        entidade in mapeamentos_especificos
    ):  # verifica se há um mapeamento específico definido para a entidade.
        tabela_alvo, coluna_alvo = mapeamentos_especificos[entidade]
        if (
            tabela_alvo in tabelas_existentes
        ):  # verifica se a tabela alvo existe entre as tabelas detectadas.
            return tabela_alvo, coluna_alvo

    tabela_plural = f"{entidade}s"
    if tabela_plural in tabelas_existentes:
        return (
            tabela_plural,
            "id",
        )  # retorna a tabela pluralizada e a coluna 'id' como referência de FK.

    return None


def gerar_schema_com_fks_posteriores():
    """Gera o arquivo SQL em duas etapas: CREATE TABLEs limpos e ALTER TABLEs com FKs ao final."""
    if not os.path.exists(CSV_DIR):  # retorna erro se o diretório dos CSVs não existir.
        print(f"Erro: O diretorio dos CSVs '{CSV_DIR}' não foi encontrado.")
        return

    arquivos_csv = sorted([f for f in os.listdir(CSV_DIR) if f.endswith(".csv")])
    if not arquivos_csv:  # retorna erro se não houver arquivos CSV no diretório.
        print(f"Aviso: Nenhum arquivo .csv encontrado em '{CSV_DIR}'.")
        return

    tabelas_existentes = [
        os.path.splitext(f)[0] for f in arquivos_csv
    ]  # cria uma lista com os nomes das tabelas
    # detectadas a partir dos arquivos CSV (sem a extensão .csv).

    print("=" * 80)
    print("GERANDO SCHEMA SQL (ETAPA 1: ESTRUTURA DAS TABELAS | ETAPA 2: FOREIGN KEYS)")
    print("=" * 80)
    print(f" -> Diretorio de Origem: {CSV_DIR}")
    print(f" -> Tabelas Detectadas: {len(tabelas_existentes)}\n")

    ddl_create_tables = []
    foreign_keys_acumuladas = []

    ddl_create_tables.append(
        "-- =============================================================================="
    )
    ddl_create_tables.append("-- Schema Relacional PostgreSQL com Foreign Keys")
    ddl_create_tables.append(
        "-- ==============================================================================\n"
    )

    # --------------------------------------------------------------------------
    # ETAPA 1: CRIAÇÃO DAS TABELAS (SEM FKS INLINE)
    # --------------------------------------------------------------------------
    ddl_create_tables.append(
        "-- =============================================================================="
    )
    ddl_create_tables.append("-- ETAPA 1: ESTRUTURA DAS TABELAS")
    ddl_create_tables.append(
        "-- ==============================================================================\n"
    )

    for arq in arquivos_csv:
        nome_tabela = os.path.splitext(arq)[
            0
        ]  # nome da tabela é derivado do nome do arquivo CSV (sem a extensão .csv)
        caminho_csv = os.path.join(CSV_DIR, arq)  # caminho completo do arquivo CSV

        with open(caminho_csv, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(
                f
            )  # cria um leitor que le cada linha como dicionário, e a primeira linha como cabeçalho
            colunas = (
                reader.fieldnames or []
            )  # obtém os nomes das colunas a partir do cabeçalho do CSV
            amostras = {
                col: [] for col in colunas
            }  # cria um dicionário para armazenar amostras de valores de cada coluna

            for row in reader:
                for col in colunas:
                    if row[col] != "":
                        amostras[col].append(
                            row[col]
                        )  # armazena apenas valores não vazios para inferência de tipo

        defs_colunas = (
            []
        )  # lista para armazenar as definições de colunas para a tabela atual
        for col in colunas:
            tipo_sql = inferir_tipo_pg(col, amostras[col])
            defs_colunas.append(
                f"    {col:<26} {tipo_sql}"
            )  # adiciona a definição da coluna à lista, formatando o nome da coluna e o tipo SQL

            # Identifica e acumula FKs para a Etapa 2
            ref_fk = obter_referencia_fk(col, tabelas_existentes)
            if ref_fk:
                tabela_destino, coluna_destino = ref_fk
                foreign_keys_acumuladas.append(
                    {
                        "tabela_origem": nome_tabela,
                        "coluna_origem": col,
                        "tabela_destino": tabela_destino,
                        "coluna_destino": coluna_destino,
                    }
                )  # adiciona a FK à lista de FKs acumuladas para serem aplicadas na Etapa 2

        # Adiciona Chave Primária composta se for tabela associativa N:N
        if nome_tabela in TABELAS_JUNCAO_PK:
            cols_pk = ", ".join(
                TABELAS_JUNCAO_PK[nome_tabela]
            )  # cria a definição da chave primária composta para tabelas associativas N:N
            defs_colunas.append(
                f"    PRIMARY KEY ({cols_pk})"
            )  # adiciona a definição da chave primária composta à lista de definições de colunas

        corpo_tabela = ",\n".join(
            defs_colunas
        )  # cria o corpo da tabela unindo todas as definições de colunas
        sql_tabela = "-- ------------------------------------------------------------------------\n"
        sql_tabela += f"-- Tabela: {nome_tabela}\n"
        sql_tabela += "-- -----------------------------------------------------------------------\n"
        sql_tabela += f"CREATE TABLE IF NOT EXISTS {nome_tabela} (\n{corpo_tabela}\n);"

        ddl_create_tables.append(
            sql_tabela
        )  # adiciona a definição da tabela à lista de DDLs de criação de tabelas

    # --------------------------------------------------------------------------
    # ETAPA 2: ADIÇÃO DAS RESTRIÇÕES DE FOREIGN KEY (ALTER TABLE)
    # --------------------------------------------------------------------------
    ddl_alter_fks = (
        []
    )  # lista para armazenar as instruções de ALTER TABLE para adicionar FKs
    ddl_alter_fks.append(
        "\n-- =============================================================================="
    )
    ddl_alter_fks.append("-- ETAPA 2: FOREIGN KEYS")
    ddl_alter_fks.append(
        "-- ==============================================================================\n"
    )

    for fk in foreign_keys_acumuladas:
        nome_constraint = f"fk_{fk['tabela_origem']}_{fk['coluna_origem']}"
        sql_fk = (
            f"ALTER TABLE {fk['tabela_origem']} DROP CONSTRAINT IF EXISTS {nome_constraint};\n"
            f"ALTER TABLE {fk['tabela_origem']}\n"
            f"    ADD CONSTRAINT {nome_constraint}\n"
            f"    FOREIGN KEY ({fk['coluna_origem']})\n"
            f"    REFERENCES {fk['tabela_destino']}({fk['coluna_destino']});"
        )  # cria a instrução SQL para adicionar a FK, garantindo que qualquer constraint
        # existente com o mesmo nome seja removida antes de adicionar a nova.
        ddl_alter_fks.append(
            sql_fk
        )  # adiciona a instrução de ALTER TABLE à lista de DDLs de FKs

    conteudo_final = (
        "\n\n".join(ddl_create_tables) + "\n" + "\n\n".join(ddl_alter_fks) + "\n"
    )  # combina todas as instruções de criação de tabelas e FKs em um único conteúdo final

    with open(OUTPUT_SQL, mode="w", encoding="utf-8") as f:
        f.write(
            conteudo_final
        )  # escreve o conteúdo final no arquivo de saída schema.sql

    print(f" -> {len(arquivos_csv)} Tabelas geradas com CREATE TABLE.")
    print(
        f" -> {len(foreign_keys_acumuladas)} Constraints de Foreign Key geradas com ALTER TABLE."
    )
    print(f"\nSucesso! Schema SQL com FKs posteriores gerado em:\n -> {OUTPUT_SQL}")
    print("=" * 80)


if __name__ == "__main__":
    gerar_schema_com_fks_posteriores()
