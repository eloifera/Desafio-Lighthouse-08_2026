"""
Previsão de Demanda Mensal (Modelo Baseline de Média Móvel)

Este script:
1. Conecta-se diretamente ao servidor PostgreSQL no Docker.
2. Carrega e unifica as tabelas 'products', 'product_variants', 'orders' e 'order_items'.
3. Filtra as vendas exclusivamente para o produto "Bússola de Bordo 702".
4. Constrói o modelo Baseline de Média Móvel dos últimos 3 meses (MA3) de forma autoregressiva:
    - Jan/26: Média das vendas reais dos últimos 3 meses do treino (Out/25, Nov/25, Dez/25).
    - Fev/26: Média de Nov/25, Dez/25 e a previsão de Jan/26.
    - Mar/26: Média de Dez/25, previsão de Jan/26 e previsão de Fev/26.
5. Avalia o desempenho do modelo no 1º trimestre de 2026 através da métrica
    MAE (Mean Absolute Error).

Lembre-se de instalar a biblioteca 'psycopg2' antes de executar o script e definir
as variáveis de conexão do PostgreSQL, se necessário, pelas constantes PG_HOST,
PG_PORT, PG_DB, PG_USER e PG_PASS.
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


def executar_previsao_demanda_postgresql():
    """Executa a previsão de demanda mensal para o produto
    'Bússola de Bordo 702' usando o modelo baseline de Média Móvel."""
    print("=" * 85)
    print("PREVISÃO DE DEMANDA MENSAL (MODELO BASELINE MA3)")
    print("=" * 85)

    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
        )  # Conecta ao banco de dados PostgreSQL
        print(
            f" -> Conectado com sucesso ao PostgreSQL ({PG_HOST}:{PG_PORT}/{PG_DB})\n"
        )
    except (
        psycopg2.Error
    ) as e:  # erro caso haja algum problema ao conectar ao banco de dados PostgreSQL
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return

    # Query unificada com sintaxe nativa do PostgreSQL (TO_CHAR para ano-mês)
    query_postgresql = """
    SELECT 
        TO_CHAR(o.created_at, 'YYYY-MM') AS ano_mes,
        p.name AS nome_produto,
        SUM(CAST(oi.quantity AS NUMERIC)) AS quantidade_vendida
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    WHERE p.name = 'Bússola de Bordo 702'
      AND o.status IN ('paid', 'confirmed')
    GROUP BY TO_CHAR(o.created_at, 'YYYY-MM'), p.name
    ORDER BY ano_mes ASC;
    """  # Query SQL para extrair o histórico de vendas do produto "Bússola de Bordo 702"

    df = pd.read_sql_query(
        query_postgresql, conn
    )  # Executa a query SQL e armazena o resultado em um DataFrame do Pandas
    conn.close()  # Fecha a conexão com o banco de dados PostgreSQL

    df["ano_mes_dt"] = pd.to_datetime(
        df["ano_mes"] + "-01"
    )  # Converte a coluna 'ano_mes' para o tipo datetime
    df = df.sort_values("ano_mes_dt").reset_index(
        drop=True
    )  # Ordena o DataFrame pelo datetime e reseta o índice

    full_series = df.set_index("ano_mes")[
        "quantidade_vendida"
    ]  # Cria uma série temporal com o índice sendo 'ano_mes' e os valores sendo 'quantidade_vendida'

    # Vendas reais do treino (final de 2025)
    v_oct = float(full_series["2025-10"])
    v_nov = float(full_series["2025-11"])
    v_dec = float(full_series["2025-12"])

    # Vendas reais do período de teste (1º trimestre de 2026)
    real_jan = float(full_series["2026-01"])
    real_fev = float(full_series["2026-02"])
    real_mar = float(full_series["2026-03"])

    # Modelo Baseline Autoregressivo (Média Móvel de 3 Meses)
    pred_jan = (v_oct + v_nov + v_dec) / 3.0
    pred_fev = (v_nov + v_dec + pred_jan) / 3.0
    pred_mar = (v_dec + pred_jan + pred_fev) / 3.0

    # Cálculo do erro absoluto e do MAE (Mean Absolute Error)
    err_jan = abs(pred_jan - real_jan)
    err_fev = abs(pred_fev - real_fev)
    err_mar = abs(pred_mar - real_mar)

    soma_previsoes = (
        pred_jan + pred_fev + pred_mar
    )  # Soma total das previsões para o 1º trimestre de 2026
    mae = np.mean(
        [err_jan, err_fev, err_mar]
    )  # Cálculo do MAE (Mean Absolute Error) para o 1º trimestre de 2026

    print(" - Produto Analisado: 'Bússola de Bordo 702'")
    print(
        f" - Histórico de Vendas (Treino Final 2025): Out/25 = {v_oct:.0f},"
        f" Nov/25 = {v_nov:.0f}, Dez/25 = {v_dec:.0f}\n"
    )
    print("-" * 85)
    print(
        f"{'Mês / Ano':<12} | {'Venda Real':<15} | {'Previsão MA3':<20} | {'Erro Absoluto |Y - Yhat|':<25}"
    )
    print("-" * 85)
    print(f"{'2026-01':<12} | {real_jan:<15.0f} | {pred_jan:<20.2f} | {err_jan:<25.2f}")
    print(f"{'2026-02':<12} | {real_fev:<15.0f} | {pred_fev:<20.2f} | {err_fev:<25.2f}")
    print(f"{'2026-03':<12} | {real_mar:<15.0f} | {pred_mar:<20.2f} | {err_mar:<25.2f}")
    print("-" * 85)
    print(
        f" SOMA TOTAL DA PREVISÃO NO 1º TRIMESTRE DE 2026 (INTEIRO): {round(soma_previsoes)} unidades ({soma_previsoes:.2f})"
    )
    print(
        f" MAE FINAL (MEAN ABSOLUTE ERROR) NO 1º TRIMESTRE DE 2026: {mae:.2f} unidades"
    )
    print("=" * 85)


if __name__ == "__main__":
    executar_previsao_demanda_postgresql()
