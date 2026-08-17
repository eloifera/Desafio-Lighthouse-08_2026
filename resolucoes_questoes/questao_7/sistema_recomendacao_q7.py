"""
Sistema de Recomendação de Produtos (Similaridade de Cosseno)

Este script:
1. Conecta-se diretamente ao servidor PostgreSQL (Docker ou Localhost).
2. Lê os históricos de transações entre Clientes e Produtos (`orders`,
    `order_items`, `product_variants`, `products`).
3. Constrói uma Matriz de Interação Usuário x Produto (Binária: 1 se
    comprou ao menos uma vez, 0 caso contrário).
4. Calcula a Similaridade de Cosseno (Cosine Similarity) entre todos
    os pares de produtos (Item-Item Collaborative Filtering).
5. Define como produto de referência o "Motor de Popa 1949".
6. Gera o ranking dos 5 produtos mais similares a ele (excluindo o
    próprio motor).

Personalização:
As seguintes constantes e variáveis podem ser ajustadas
    para atender a diferentes cenários de teste:
- target_product: Nome do produto de referência para o qual se deseja
    encontrar produtos similares.
- product_untreated: Lista de produtos que não são válidos e devem ser
    removidos do ranking final (ex.: registros de teste, produtos de demonstração).

Lembre-se de instalar a biblioteca 'psycopg2', 'pandas' e 'numpy'
    antes de executar o script e definir as variáveis de conexão do
    PostgreSQL, se necessário, pelas constantes PG_HOST, PG_PORT, PG_DB,
    PG_USER e PG_PASS.
"""

import os
import psycopg2
import pandas as pd
import numpy as np

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


def calcular_similaridade_cosseno(matrix_df):
    """Calcula a similaridade de cosseno produto x produto a partir da matriz usuário x produto."""
    matrix = matrix_df.values.astype(
        float
    )  # Converte a matriz para float para evitar problemas de tipo
    dot_product = np.dot(
        matrix.T, matrix
    )  # Calcula o produto escalar entre os vetores de produtos
    norms = np.linalg.norm(
        matrix, axis=0
    )  # Calcula a norma (magnitude) de cada vetor de produto
    outer_norms = np.outer(
        norms, norms
    )  # Calcula o produto externo das normas para normalizar o produto escalar

    with np.errstate(divide="ignore", invalid="ignore"):
        cosine_sim = np.true_divide(
            dot_product, outer_norms
        )  # Calcula a similaridade de cosseno dividindo o produto escalar pelo produto das normas
        cosine_sim[np.isnan(cosine_sim)] = (
            0.0  # Substitui NaN por 0.0 para evitar problemas de similaridade indefinida
        )

    return pd.DataFrame(
        cosine_sim, index=matrix_df.columns, columns=matrix_df.columns
    )  # Retorna a matriz de similaridade de cosseno como um DataFrame
    # com os nomes dos produtos como índice e colunas


def executar_sistema_recomendacao_postgresql():
    """Executa o sistema de recomendação de produtos
    baseado em similaridade de cosseno no PostgreSQL."""
    print("=" * 85)
    print("SISTEMA DE RECOMENDAÇÃO EM POSTGRESQL (SIMILARIDADE DE COSSENO)")
    print("=" * 85)

    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
        )  # Conecta ao banco de dados PostgreSQL
        print(
            f" -> Conectado com sucesso ao PostgreSQL ({PG_HOST}:{PG_PORT}/{PG_DB})\n"
        )
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return  # retorna erro caso haja algum problema ao conectar ao banco de dados PostgreSQL

    # 1. Leitura dos dados de presença/ausência de compra por cliente no PostgreSQL
    query = """
    SELECT DISTINCT
        o.customer_id,
        p.name AS product_name
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    WHERE o.status IN ('paid', 'confirmed');
    """  # Query SQL para extrair o histórico de compras dos clientes e produtos das tabelas
    # orders, order_items, product_variants e products do PostgreSQL

    df = pd.read_sql_query(query, conn)  # Executa a query SQL e armazena o resultado
    # em um DataFrame do Pandas
    conn.close()  # Fecha a conexão com o banco de dados PostgreSQL

    # 2. Matriz Usuário x Produto (Binária: 1 se comprou, 0 se não comprou)
    matrix_user_item = pd.crosstab(
        df["customer_id"], df["product_name"]
    )  # Cria uma matriz de interação usuário x produto
    matrix_user_item_binary = (matrix_user_item > 0).astype(
        int
    )  # Converte a matriz de interação para binária (1 comprou, 0 não comprou)

    # 3. Matriz de Similaridade de Cosseno Produto x Produto
    sim_df = calcular_similaridade_cosseno(
        matrix_user_item_binary
    )  # Calcula a similaridade de
    # cosseno entre os produtos a partir da matriz binária de interação

    target_product = (
        "Motor de Popa 1949"  # Produto que se deseja encontrar produtos similares
    )
    product_untreated = [
        "asdf"
    ]  # Produtos que não são válidos e devem ser removidos do ranking

    print(
        f" - Matriz de Interação: {matrix_user_item_binary.shape[0]} "
        f" Clientes x {matrix_user_item_binary.shape[1]} Produtos"
    )
    print(f" - Produto de Referência: '{target_product}'\n")

    if target_product in sim_df.columns:
        # Ranking Bruto de Similaridade (excluindo o próprio motor)
        top_raw = (
            sim_df[target_product].drop(target_product).sort_values(ascending=False)
        )  # Ordena os produtos por similaridade de cosseno em relação ao produto de referência

        print("-" * 85)
        print(
            "RANKING BRUTO DOS TOP 5 PRODUTOS MAIS SIMILARES (TOLERANDO RUÍDOS DAS TABELAS):"
        )
        print("-" * 85)
        print(
            f"{'Ranking':<8} | {'Nome do Produto':<45} | {'Similaridade de Cosseno':<25}"
        )
        print("-" * 85)
        for rank, (prod_name, score) in enumerate(top_raw.head(5).items(), 1):
            print(
                f"{rank:<8} | {prod_name:<45} | {score:.4f}"
            )  # Imprime o ranking bruto dos 5 produtos mais similares ao produto de referência
        print("-" * 85)

        # Removendo o registro de produtos inválidos encontrados anteriormente,caso exista
        top_clean = top_raw.drop(labels=product_untreated, errors="ignore").head(5)

        print("\n" + "-" * 85)
        print(
            "RANKING TRATADO DOS TOP 5 PRODUTOS MAIS SIMILARES (PRODUTOS VÁLIDOS DA LOJA):"
        )
        print("-" * 85)
        print(
            f"{'Ranking':<8} | {'Nome do Produto':<45} | {'Similaridade de Cosseno':<25}"
        )
        print("-" * 85)
        for rank, (prod_name, score) in enumerate(top_clean.items(), 1):
            print(
                f"{rank:<8} | {prod_name:<45} | {score:.4f}"
            )  # Imprime o ranking limpo dos 5 produtos mais similares ao produto de referência
        print("=" * 85)

        vencedor_top1 = top_clean.index[
            0
        ]  # Nome do produto mais recomendado (top 1) após a limpeza do ranking
        vencedor_score = top_clean.iloc[
            0
        ]  # Similaridade de cosseno do produto mais recomendado (top 1) após a limpeza do ranking
        print(f"\n -> PRODUTO MAIS RECOMENDADO PARA QUEM COMPRA '{target_product}':")
        print(f"    - Produto: '{vencedor_top1}'")
        print(f"    - Índice de Similaridade de Cosseno: {vencedor_score:.4f}")


if __name__ == "__main__":
    executar_sistema_recomendacao_postgresql()
