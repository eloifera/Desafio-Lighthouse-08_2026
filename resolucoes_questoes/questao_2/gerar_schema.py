"""
Este script:
1. Varre todos os arquivos CSV presentes no diretório atual
(ou diretório indicado caso não haja arquivos csv na pasta atual) e mapeia a estrutura relacional.
2. Aplica a detecção de identificadores textuais (preservando colunas como CEP,
Telefone, CPF/CNPJ como VARCHAR).
3. Infere a escala real das colunas decimais a partir dos dados, evitando arredondamento
   silencioso na carga.
4. Mapeia automaticamente as restrições de Chaves Estrangeiras (FOREIGN KEY / REFERENCES)
   entre as tabelas baseando-se nas convenções relacionais de nomes, inclusive quando a
   coluna carrega um qualificador de papel (buyer_id, received_by_employee_id, ...).
5. Declara PRIMARY KEY composta nas tabelas de junção, validando a unicidade nos dados.
6. Gera um arquivo de saída chamado 'schema.sql' com os DDLs completos.

A constante de configuração TEXT_IDENTIFIER_KEYWORDS (utilizada para identificar colunas específicas
que serão tratadas como identificadores textuais) e a variável mapeamentos_especificos (utilizada
para definir mapeamentos específicos do usuário para foreign keys) podem ser ajustadas para atender
a diferentes convenções de nomenclatura.
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
    # Caso não encontre, pede para o usuário digitar/colar o caminho no terminal:
    caminho_informado = input(
        "Nenhum arquivo .csv encontrado na pasta do script.\nPor favor, digite"
        " ou cole o caminho da pasta onde estão os arquivos CSV: "
    )
    # Limpa espaços e aspas (caso o usuário cole um caminho entre aspas)
    CSV_DIR = os.path.abspath(caminho_informado.strip().strip("\"'"))
# O arquivo schema.sql será gerado na mesma pasta do script
OUTPUT_SQL = os.path.join(SCRIPT_DIR, "schema.sql")

# Lista de palavras-chave de colunas para preservar identificadores textuais como VARCHAR
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


def eh_identificador_textual(nome_coluna):
    """Verifica se o nome da coluna é um identificador textual (como CEP, telefone, CPF/CNPJ...)."""
    nome_col = nome_coluna.lower()
    return any(kw in nome_col for kw in TEXT_IDENTIFIER_KEYWORDS)


def inferir_tipo_pg(nome_coluna, valores):
    """Infere o tipo de dado PostgreSQL apropriado da coluna com base nos valores amostrados."""
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

    if all(v.upper() in ["TRUE", "FALSE", "1", "0", "T", "F"] for v in valores_validos):
        if set(v.upper() for v in valores_validos).issubset(
            {"TRUE", "FALSE", "T", "F"}
        ):
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
    """Mapeia dinamicamente a referência de FOREIGN KEY baseando-se no nome da coluna."""
    if not nome_coluna.endswith("_id") or nome_coluna == "id":
        return None
        # Se a coluna não termina com '_id' ou é a própria coluna 'id', não é considerada uma FK.

    # tax_id, ncm_code etc. são identificadores de negócio, não chaves estrangeiras
    if eh_identificador_textual(nome_coluna):
        return None

    entidade = nome_coluna[:-3].lower()  # Remove '_id'

    # Exceções e mapeamentos específicos de nomenclatura para
    # relacionar foreign keys com tabelas corretas.
    mapeamentos_especificos = {
        "salesperson": "employees",
        "created_by_employee": "employees",
        "employee": "employees",
        "buyer": "employees",
        "variant": "product_variants",
        "customer": "customers",
        "supplier": "suppliers",
        "location": "locations",
        "order": "orders",
        "order_item": "order_items",
        "product": "products",
        "product_variant": "product_variants",
        "purchase_order": "purchase_orders",
        "purchase_order_item": "purchase_order_items",
        "goods_receipt": "goods_receipts",
        "return": "returns",
        "category": "categories",
        "brand": "brands",
        "attribute": "attributes",
    }

    # Testa a entidade inteira e, em seguida, sufixos progressivamente menores.
    # Isso resolve os qualificadores de papel usados nos CSVs:
    #   received_by_employee -> by_employee -> employee  (employees)
    #   primary_location / destination_location          (locations)
    #   parent_category                                  (categories, auto-referência)
    partes = entidade.split("_")  # divide a entidade em partes separadas por '_'
    for i in range(len(partes)):
        candidato = "_".join(
            partes[i:]
        )  # junta as partes restantes para formar o candidato a tabela alvo

        if candidato in mapeamentos_especificos:
            tabela_alvo = mapeamentos_especificos[candidato]
            if tabela_alvo in tabelas_existentes:
                return f"REFERENCES {tabela_alvo}(id)"
                # Retorna a referência de FOREIGN KEY para a tabela
                # mapeada no dicionário de mapeamentos específicos.

        # Testa os padrões genéricos de plural (ex: 'user_id' -> 'users')
        if f"{candidato}s" in tabelas_existentes:
            return f"REFERENCES {candidato}s(id)"

        if candidato in tabelas_existentes:
            return f"REFERENCES {candidato}(id)"

    return None


def chave_composta_valida(caminho_csv, colunas_chave):
    """Confirma nos dados que as colunas formam uma chave: sem nulos e sem repetição."""
    vistos = set()
    with open(caminho_csv, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            chave = tuple(row[c] for c in colunas_chave)
            if any(v == "" for v in chave) or chave in vistos:
                return False
            vistos.add(chave)
    return bool(vistos)
    # Checa se todas as combinações de valores nas colunas_chave forem únicas e não nulas.


def gerar_schema_com_fks():
    """Gera o schema SQL com detecção automática de FOREIGN KEYS e PRIMARY KEYS compostas."""
    if not os.path.exists(CSV_DIR):
        print(f"Erro: O diretório '{CSV_DIR}' não foi encontrado.")
        return
        # alerta o usuário caso o diretório informado não exista.
    arquivos_csv = sorted(
        [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    )  # lista os arquivos CSV no diretório
    tabelas_existentes = [
        os.path.splitext(f)[0] for f in arquivos_csv
    ]  # lista os nomes das tabelas existentes com base nos arquivos CSV encontrados

    print("=" * 80)
    print("GERANDO SCHEMA SQL COM DETECÇÃO AUTOMÁTICA DE FOREIGN KEYS")
    print("=" * 80)
    print(f" -> Diretório dos CSVs: {CSV_DIR}")
    print(f" -> Total de tabelas mapeadas: {len(tabelas_existentes)}\n")

    ddl_statements = []
    ddl_statements.append(
        "-- =============================================================================="
    )
    ddl_statements.append("-- Schema Relacional com Foreign Keys")
    ddl_statements.append(
        "-- Gerado via Python (Bibliotecas Nativas + Mapeamento de Referências)"
    )
    ddl_statements.append(
        "-- ==============================================================================\n"
    )

    for arq in arquivos_csv:
        nome_tabela = os.path.splitext(arq)[0]
        caminho_csv = os.path.join(CSV_DIR, arq)

        with open(caminho_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            colunas = reader.fieldnames or []
            amostras = {
                col: [] for col in colunas
            }  # cria um dicionário para armazenar amostras de valores de cada coluna

            for row in reader:
                for col in colunas:
                    if row[col] != "":
                        amostras[col].append(
                            row[col]
                        )  # armazena apenas valores não nulos para inferência de tipo

        defs_colunas = []  # lista para armazenar as definições de colunas no DDL
        colunas_fk = []  # lista para armazenar as colunas que são chaves estrangeiras
        for col in colunas:
            tipo_sql = inferir_tipo_pg(col, amostras[col])

            # Checa se a coluna possui relacionamento de Foreign Key
            ref_fk = obter_referencia_fk(col, tabelas_existentes)
            if ref_fk:
                tipo_sql = f"{tipo_sql} {ref_fk}"
                colunas_fk.append(col)

            defs_colunas.append(
                f"    {col:<26} {tipo_sql}"
            )  # adiciona a definição da coluna ao DDL,
            # alinhando o tipo SQL à direita para melhor legibilidade

        # Tabelas de junção não têm coluna 'id': a chave primária é o conjunto de FKs.
        # Só declaramos a PK se os dados comprovarem que a combinação é única e não nula.
        if "id" not in colunas and len(colunas_fk) >= 2:
            if chave_composta_valida(caminho_csv, colunas_fk):
                defs_colunas.append(f"    PRIMARY KEY ({', '.join(colunas_fk)})")
                print(f" -> {nome_tabela}: PRIMARY KEY ({', '.join(colunas_fk)})")
            else:
                print(
                    f" -> {nome_tabela}: ({', '.join(colunas_fk)}) não é única nos dados; "
                    f"tabela permanece sem PRIMARY KEY"
                )  # alerta o usuário caso a combinação de colunas FK não seja única
                # nos dados, indicando que a tabela não terá uma PRIMARY KEY definida.

        corpo_tabela = ",\n".join(defs_colunas)
        sql_tabela = "-- -----------------------------------------------------------------------\n"
        sql_tabela += f"-- Tabela: {nome_tabela}\n"
        sql_tabela += "-- -----------------------------------------------------------------------\n"
        sql_tabela += f"CREATE TABLE IF NOT EXISTS {nome_tabela} (\n{corpo_tabela}\n);"
        # declara a criação da tabela com as definições de colunas e chaves primárias/estrangeiras,
        # garantindo que a tabela só será criada se não existir previamente.

        ddl_statements.append(
            sql_tabela
        )  # adiciona o DDL da tabela à lista de statements que serão gravados no arquivo final.

    conteudo_final = (
        "\n\n".join(ddl_statements) + "\n"
    )  # junta todos os statements DDL em um único conteúdo final,
    # separando-os por duas linhas em branco para melhor legibilidade.

    with open(OUTPUT_SQL, mode="w", encoding="utf-8") as f:
        f.write(
            conteudo_final
        )  # grava o conteúdo final no arquivo de saída 'schema_new.sql',
        # sobrescrevendo qualquer conteúdo existente.

    print(f"Sucesso! Schema SQL com Foreign Keys gerado em:\n -> {OUTPUT_SQL}")
    print("=" * 80)


if __name__ == "__main__":
    gerar_schema_com_fks()
