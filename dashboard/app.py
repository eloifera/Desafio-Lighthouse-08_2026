"""
==============================================================================
Dashboard Executivo Interativo (Streamlit + Plotly + PostgreSQL)
==============================================================================
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg
import streamlit as st

# ------------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="LH Nautical | Executive Analytics Dashboard",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Customizada para Design Premium
st.markdown(
    """
    <style>
    .main {
        background-color: #0b0f19;
    }
    .stMetric {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .metric-card-title {
        color: #8b9bb4;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card-value {
        color: #00f2fe;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .badge-pior-dia {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
    }
    .readme-card {
        background-color: #161b26;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# CONEXÃO EXCLUSIVA COM O BANCO DE DADOS POSTGRESQL
# ------------------------------------------------------------------------------
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = os.getenv("PGPORT", "5432")
PG_DB = os.getenv("PGDATABASE", "postgres")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASS = os.getenv("PGPASSWORD", "postgres")


@st.cache_resource
def obter_conexao_postgresql():
    """Conecta-se estritamente ao servidor PostgreSQL (Docker ou Local)."""
    try:
        conexao = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
        )
        return conexao
    except psycopg2.Error as e:
        st.error(f"Erro ao conectar ao PostgreSQL ({PG_HOST}:{PG_PORT}/{PG_DB}): {e}")
        st.stop()


conn = obter_conexao_postgresql()


# Helper para leitura de SQL via psycopg2
def ler_sql(sql_query):
    """Lê uma consulta SQL e retorna um DataFrame pandas."""
    return pd.read_sql_query(sql_query, conn)


# ------------------------------------------------------------------------------
# CABEÇALHO DO DASHBOARD
# ------------------------------------------------------------------------------
st.title("⚓ LH Nautical | Dashboard de Inteligência & Analytics")
st.caption("Candidato: **Eloi Ferreira**")
st.markdown("---")


# ------------------------------------------------------------------------------
# CARREGAMENTO E CACHEAR DADOS DAS CONSULTAS (POSTGRESQL)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def carregar_kpis_gerais():
    """
    Carrega os KPIs gerais do banco de dados.
    """
    query = """
    SELECT 
        SUM(CAST(total AS NUMERIC)) AS faturamento_total,
        COUNT(DISTINCT id) AS total_pedidos,
        SUM(CAST(total AS NUMERIC)) / COUNT(DISTINCT id) AS ticket_medio,
        COUNT(DISTINCT customer_id) AS total_clientes
    FROM orders;
    """
    return ler_sql(query).iloc[0]


@st.cache_data(ttl=3600)
def carregar_vendas_temporais():
    """
    Carrega os dados de vendas temporais do banco de dados.
    """
    query = """
    SELECT 
        TO_CHAR(created_at, 'YYYY-MM') AS ano_mes,
        SUM(CAST(total AS NUMERIC)) AS faturamento,
        COUNT(DISTINCT id) AS quantidade_pedidos
    FROM orders
    GROUP BY TO_CHAR(created_at, 'YYYY-MM')
    ORDER BY ano_mes ASC;
    """
    return ler_sql(query)


@st.cache_data(ttl=3600)
def carregar_vendas_dia_semana():
    """
    Carrega os dados de vendas por dia da semana do banco de dados.
    """
    query = """
    WITH calendario AS (
        SELECT generate_series(
            (SELECT MIN(created_at::date) FROM orders WHERE channel = 'pos'),
            (SELECT MAX(created_at::date) FROM orders WHERE channel = 'pos'),
            '1 day'::interval
        )::date AS data
    ),
    vendas_diarias AS (
        SELECT 
            created_at::date AS data_venda,
            SUM(CAST(total AS NUMERIC)) AS valor_venda_dia
        FROM orders
        WHERE channel = 'pos'
        GROUP BY created_at::date
    ),
    calendario_com_vendas AS (
        SELECT 
            c.data,
            EXTRACT(DOW FROM c.data) AS num_dia,
            CASE EXTRACT(DOW FROM c.data)
                WHEN 0 THEN 'Domingo'
                WHEN 1 THEN 'Segunda-feira'
                WHEN 2 THEN 'Terça-feira'
                WHEN 3 THEN 'Quarta-feira'
                WHEN 4 THEN 'Quinta-feira'
                WHEN 5 THEN 'Sexta-feira'
                WHEN 6 THEN 'Sábado'
            END AS dia_semana,
            COALESCE(v.valor_venda_dia, 0.0) AS valor_venda
        FROM calendario c
        LEFT JOIN vendas_diarias v ON c.data = v.data_venda
    )
    SELECT 
        dia_semana,
        num_dia,
        COUNT(*) AS total_dias,
        ROUND(AVG(valor_venda), 2) AS media_real,
        ROUND(SUM(valor_venda) / NULLIF(SUM(CASE WHEN valor_venda > 0 THEN 1 ELSE 0 END), 0), 2) AS media_errada
    FROM calendario_com_vendas
    GROUP BY dia_semana, num_dia
    ORDER BY num_dia ASC;
    """
    return ler_sql(query)


@st.cache_data(ttl=3600)
def carregar_top10_clientes():
    """Carrega os 10 clientes de elite com maior ticket médio e diversidade de categorias."""
    query = """
    WITH metricas_pedidos AS (
        SELECT customer_id, SUM(CAST(total AS NUMERIC)) AS faturamento_total, COUNT(DISTINCT id) AS frequencia
        FROM orders GROUP BY customer_id
    ),
    metricas_categorias AS (
        SELECT o.customer_id, COUNT(DISTINCT p.category_id) AS diversidade_categorias
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN product_variants pv ON pv.id = oi.product_variant_id
        JOIN products p ON p.id = pv.product_id
        GROUP BY o.customer_id
    )
    SELECT 
        mp.customer_id,
        ROUND(mp.faturamento_total, 2) AS faturamento_total,
        mp.frequencia,
        ROUND(mp.faturamento_total / mp.frequencia, 2) AS ticket_medio,
        mc.diversidade_categorias
    FROM metricas_pedidos mp
    JOIN metricas_categorias mc ON mc.customer_id = mp.customer_id
    WHERE mc.diversidade_categorias >= 13
    ORDER BY ticket_medio DESC, mp.customer_id ASC
    LIMIT 10;
    """
    return ler_sql(query)


@st.cache_data(ttl=3600)
def carregar_categorias_top10():
    """Carrega as categorias mais compradas pelos 10 clientes de elite."""
    query = """
    WITH metricas_pedidos AS (
        SELECT customer_id, SUM(CAST(total AS NUMERIC)) AS faturamento_total, COUNT(DISTINCT id) AS frequencia
        FROM orders GROUP BY customer_id
    ),
    metricas_categorias AS (
        SELECT o.customer_id, COUNT(DISTINCT p.category_id) AS diversidade_categorias
        FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN product_variants pv ON pv.id = oi.product_variant_id JOIN products p ON p.id = pv.product_id GROUP BY o.customer_id
    ),
    top10_clientes AS (
        SELECT mp.customer_id FROM metricas_pedidos mp JOIN metricas_categorias mc ON mc.customer_id = mp.customer_id WHERE mc.diversidade_categorias >= 13 ORDER BY (mp.faturamento_total / mp.frequencia) DESC, mp.customer_id ASC LIMIT 10
    )
    SELECT c.id AS category_id, c.name AS nome_categoria, SUM(CAST(oi.quantity AS NUMERIC)) AS total_itens
    FROM top10_clientes t JOIN orders o ON o.customer_id = t.customer_id JOIN order_items oi ON oi.order_id = o.id JOIN product_variants pv ON pv.id = oi.product_variant_id JOIN products p ON p.id = pv.product_id JOIN categories c ON c.id = p.category_id
    GROUP BY c.id, c.name ORDER BY total_itens DESC;
    """
    return ler_sql(query)


# --- CONSULTAS DA ABA 5 (INTELIGÊNCIA REGIONAL & LOGÍSTICA) ---
@st.cache_data(ttl=3600)
def carregar_top10_produtos_globais():
    """Carrega os 10 produtos mais vendidos globalmente (volume de unidades vendidas)."""
    query = """
    SELECT 
        p.id AS product_id,
        p.name AS nome_produto,
        c.name AS nome_categoria,
        SUM(CAST(oi.quantity AS NUMERIC)) AS total_unidades_vendidas,
        ROUND(SUM(CAST(oi.quantity * oi.unit_price AS NUMERIC)), 2) AS faturamento_total
    FROM order_items oi
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    GROUP BY p.id, p.name, c.name
    ORDER BY total_unidades_vendidas DESC
    LIMIT 10;
    """
    return ler_sql(query)


@st.cache_data(ttl=3600)
def carregar_top5_clientes_por_estado():
    """Carrega os 5 melhores clientes por estado."""
    query = """
    WITH vendas_cliente_estado AS (
        SELECT 
            COALESCE(a.state, 'Não Informado') AS estado,
            o.customer_id,
            SUM(CAST(o.total AS NUMERIC)) AS faturamento_total,
            COUNT(DISTINCT o.id) AS total_pedidos
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN addresses a ON c.id = a.customer_id
        GROUP BY COALESCE(a.state, 'Não Informado'), o.customer_id
    ),
    ranking_estado AS (
        SELECT 
            estado,
            customer_id,
            ROUND(faturamento_total, 2) AS faturamento_total,
            total_pedidos,
            ROW_NUMBER() OVER (PARTITION BY estado ORDER BY faturamento_total DESC) AS pos
        FROM vendas_cliente_estado
    )
    SELECT estado, pos AS ranking, customer_id, faturamento_total, total_pedidos
    FROM ranking_estado
    WHERE pos <= 5
    ORDER BY estado ASC, pos ASC;
    """
    return ler_sql(query)


@st.cache_data(ttl=3600)
def carregar_clientes_multiregiao():
    """Carrega os clientes que compraram em mais de um estado (UF) e suas métricas."""
    query = """
    SELECT 
        c.id AS customer_id,
        COUNT(DISTINCT a.state) AS estados_distintos,
        STRING_AGG(DISTINCT a.state, ', ') AS estados_cadastrados,
        SUM(CAST(o.total AS NUMERIC)) AS faturamento_total,
        COUNT(DISTINCT o.id) AS total_pedidos
    FROM customers c
    JOIN addresses a ON c.id = a.customer_id
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id
    HAVING COUNT(DISTINCT a.state) > 1
    ORDER BY faturamento_total DESC;
    """
    return ler_sql(query)


@st.cache_data(ttl=3600)
def carregar_top5_produtos_por_estado_filtro(estado_selecionado):
    """Carrega os 5 produtos mais vendidos em um estado específico (UF) selecionado."""
    query = f"""
    SELECT 
        p.name AS nome_produto,
        c.name AS nome_categoria,
        SUM(CAST(oi.quantity AS NUMERIC)) AS quantidade_vendida,
        ROUND(SUM(CAST(oi.quantity * oi.unit_price AS NUMERIC)), 2) AS faturamento_gerado
    FROM orders o
    JOIN customers cust ON o.customer_id = cust.id
    JOIN addresses a ON cust.id = a.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    WHERE a.state = '{estado_selecionado}'
    GROUP BY p.id, p.name, c.name
    ORDER BY quantidade_vendida DESC
    LIMIT 5;
    """
    return ler_sql(query)


# ------------------------------------------------------------------------------
# ESTRUTURA DE ABAS INTERATIVAS
# ------------------------------------------------------------------------------
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏠 Apresentação & Arquitetura",
        "📊 Visão Geral Executiva & Vendas",
        "👑 Clientes de Elite & Categorias",
        "📈 Previsão de Demanda & Estoque",
        "🤖 Recomendador Inteligente de Produtos",
        "🗺️ Inteligência Logística & Vendas Regionais",
    ]
)

# ==============================================================================
# ABA 0: APRESENTAÇÃO & ARQUITETURA DO PROJETO (README INTERATIVO)
# ==============================================================================
with tab0:
    st.markdown("""
    ## ⚓ Bem-vindo ao Dashboard de Engenharia de Dados & Analytics — LH Nautical
    
    Este Dashboard Executivo Interativo foi desenvolvido como solução integrada para o **Desafio Lighthouse 08/2026**, apresentando a jornada completa de ingestão, modelagem relacional, inteligência de negócios, previsão de demanda e filtragem colaborativa.
    
    ---
    
    ### 🎯 Objetivo do Projeto
    Fornecer à diretoria da **LH Nautical** uma visão única e acionável sobre o faturamento da empresa, comportamento de consumo dos clientes de elite, diagnóstico de desempenho de lojas físicas, previsão de estoque para o verão e recomendação personalizada de produtos.
    
    ---
    
    ### 🧠 Estrutura e Linha de Raciocínio das Abas:
    
    #### 1. **📊 Visão Geral Executiva & Vendas:**

       - **Métricas Globais:** Apresenta o faturamento acumulado, total de pedidos e ticket médio.
       - **Diagnóstico da Dimensão de Calendário:** Revela o dia com a menor média de vendas.
       

    #### 2. **👑 Clientes de Elite & Categorias:**

       - **Ranking dos Top 10 Clientes Fiéis: Clientes que navegaram e compraram em mais categorias distintas, ordenando pelo maior Ticket Médio.
       - **Categoria Campeã:** Identifica a categoria campeã em quantidade comprada pelo grupo de elite.
       

    #### 3. **📈 Previsão de Demanda & Estoque:**
       - **Modelo Baseline Autoregressivo (MA3):** Realiza a previsão mensal de vendas de um produto para o 1º Trimestre de 2026.
       - **Métrica de Avaliação MAE:** Avalia a acurácia e alerta para o risco de *stockout* no trimestre de verão.
       

    #### 4. **🤖 Recomendador Inteligente de Produtos:**
       - **Filtragem Colaborativa Item-Item:** Constrói a Matriz de Interação Usuário x Produto Binária e calcula a **Similaridade de Cosseno**.
       - **Motor de Ofertas:** Recomenda 5 produtos para clientes que compram o produto selecionado.
       

    #### 5. **🗺️ Inteligência Logística & Vendas Regionais:**
       - **Desempenho Geográfico:** Apresenta os 10 produtos mais vendidos no geral, os Top 5 Clientes de cada Estado (UF) e filtro dinâmico de produtos mais vendidos por Estado.
    
    """)

# ==============================================================================
# ABA 1: VISÃO GERAL EXECUTIVA & VENDAS
# ==============================================================================
with tab1:
    kpi = carregar_kpis_gerais()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Faturamento Acumulado", f"R$ {kpi['faturamento_total']:,.2f}")
    with col2:
        st.metric("Total de Pedidos", f"{int(kpi['total_pedidos']):,}")
    with col3:
        st.metric("Ticket Médio Geral", f"R$ {kpi['ticket_medio']:,.2f}")
    with col4:
        st.metric("Clientes Cadastrados", f"{int(kpi['total_clientes']):,}")

    st.markdown("### 📈 Evolução Histórica do Faturamento Mensal (2020 - 2026)")
    df_temp = carregar_vendas_temporais()
    fig_temp = px.line(
        df_temp,
        x="ano_mes",
        y="faturamento",
        labels={"ano_mes": "Mês/Ano", "faturamento": "Faturamento (R$)"},
        template="plotly_dark",
        color_discrete_sequence=["#00f2fe"],
    )
    fig_temp.update_traces(mode="lines+markers", line=dict(width=3))
    st.plotly_chart(fig_temp, width="stretch")

    st.markdown("### 🗓️ Análise de Vendas por Dia da Semana (Lojas Físicas - POS)")
    df_dia = carregar_vendas_dia_semana()

    col_chart, col_exp = st.columns([2, 1])
    with col_chart:
        fig_dia = px.bar(
            df_dia,
            x="dia_semana",
            y="media_real",
            text="media_real",
            labels={
                "dia_semana": "Dia da Semana",
                "media_real": "Média Real de Vendas (R$)",
            },
            template="plotly_dark",
            color="media_real",
            color_continuous_scale="Viridis",
        )
        fig_dia.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
        st.plotly_chart(fig_dia, width="stretch")

    with col_exp:
        pior_row = df_dia.sort_values("media_real").iloc[0]
        st.error(f"🔴 Alerta: **Pior Dia:** {pior_row['dia_semana']}")
        st.write(f"- **Média Real:** R$ {pior_row['media_real']:,.2f}")

# ==============================================================================
# ABA 2: CLIENTES DE ELITE & CATEGORIAS (QUESTÃO 4)
# ==============================================================================
with tab2:
    st.markdown(
        "### 👑 Ranking dos 10 Clientes de Elite (Diversidade de Categorias >= 13)"
    )
    df_top10 = carregar_top10_clientes()

    col_tabela, col_graf = st.columns([1.2, 1])
    with col_tabela:
        st.dataframe(
            df_top10.style.format(
                {"faturamento_total": "R$ {:,.2f}", "ticket_medio": "R$ {:,.2f}"}
            ),
            width="stretch",
        )

    with col_graf:
        df_top10_graf = df_top10.copy()
        df_top10_graf["customer_str"] = "Cliente " + df_top10_graf[
            "customer_id"
        ].astype(str)
        fig_top10 = px.bar(
            df_top10_graf,
            x="customer_str",
            y="ticket_medio",
            text="ticket_medio",
            labels={
                "ticket_medio": "Ticket Médio (R$)",
                "customer_str": "Cliente",
            },
            template="plotly_dark",
            color="ticket_medio",
            color_continuous_scale="Teal",
        )
        fig_top10.update_traces(
            texttemplate="R$ %{text:,.2f}", textposition="outside", width=0.6
        )
        fig_top10.update_layout(
            xaxis_title="Cliente de Elite",
            yaxis_title="Ticket Médio (R$)",
            showlegend=False,
        )
        st.plotly_chart(fig_top10, width="stretch")

    st.markdown("### 🏆 Categoria Mais Vendida para o Grupo de Elite")
    df_cat = carregar_categorias_top10()
    cat_vencedora = df_cat.iloc[0]

    col_cat_graf, col_cat_info = st.columns([2, 1])
    with col_cat_graf:
        fig_cat = px.bar(
            df_cat,
            x="total_itens",
            y="nome_categoria",
            orientation="h",
            text="total_itens",
            labels={
                "total_itens": "Total de Itens Comprados",
                "nome_categoria": "Categoria",
            },
            template="plotly_dark",
            color="total_itens",
            color_continuous_scale="Viridis",
        )
        fig_cat.update_layout(yaxis=dict(autorange="reversed"))
        fig_cat.update_traces(textposition="outside")
        st.plotly_chart(fig_cat, width="stretch")

    with col_cat_info:
        st.success(f"🥇 **Categoria Campeã:** {cat_vencedora['nome_categoria']}")
        st.metric(
            "Total de Itens Comprados pelo Top 10",
            f"{int(cat_vencedora['total_itens']):,} unidades",
        )
        st.caption(
            "Esta categoria concentra a maior demanda entre os clientes fiéis de alta renda."
        )

# ==============================================================================
# ABA 3: PREVISÃO DE DEMANDA & ESTOQUE (QUESTÃO 6)
# ==============================================================================
with tab3:
    st.markdown("### 📈 Previsão de Demanda Mensal (Modelo Baseline MA3)")
    st.caption(
        "Selecione o produto para ver a previsão autoregressiva e a métrica MAE no 1º Trimestre de 2026."
    )

    @st.cache_data(ttl=3600)
    def carregar_lista_produtos_previsao():
        """Carrega a lista de produtos distintos disponíveis para previsão de demanda."""
        query = "SELECT DISTINCT name FROM products ORDER BY name ASC;"
        return ler_sql(query)["name"].tolist()

    @st.cache_data(ttl=3600)
    def carregar_serie_temporal_produto(nome_produto):
        """Carrega a série temporal de vendas mensais para um produto específico."""
        query = f"""
        SELECT 
            TO_CHAR(o.created_at, 'YYYY-MM') AS ano_mes,
            SUM(CAST(oi.quantity AS NUMERIC)) AS quantidade_vendida
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN product_variants pv ON oi.product_variant_id = pv.id
        JOIN products p ON pv.product_id = p.id
        WHERE p.name = '{nome_produto.replace("'", "''")}'
          AND o.status IN ('paid', 'confirmed')
        GROUP BY TO_CHAR(o.created_at, 'YYYY-MM')
        ORDER BY ano_mes ASC;
        """
        return ler_sql(query)

    lista_prods_q6 = carregar_lista_produtos_previsao()
    index_padrao_q6 = (
        lista_prods_q6.index("Bússola de Bordo 702")
        if "Bússola de Bordo 702" in lista_prods_q6
        else 0
    )

    produto_sel_q6 = st.selectbox(
        "Selecione um Produto para Simular a Previsão de Demanda Mensal (MA3):",
        lista_prods_q6,
        index=index_padrao_q6,
    )

    df_hist_q6 = carregar_serie_temporal_produto(produto_sel_q6)

    if not df_hist_q6.empty:
        df_hist_series = df_hist_q6.set_index("ano_mes")["quantidade_vendida"].astype(
            float
        )

        # Histórico de Treino (Final de 2025)
        v_oct = float(df_hist_series.get("2025-10", 0.0))
        v_nov = float(df_hist_series.get("2025-11", 0.0))
        v_dec = float(df_hist_series.get("2025-12", 0.0))

        # Vendas Reais do Teste (1º Trimestre de 2026)
        real_jan = float(df_hist_series.get("2026-01", 0.0))
        real_fev = float(df_hist_series.get("2026-02", 0.0))
        real_mar = float(df_hist_series.get("2026-03", 0.0))

        # Previsão Autoregressiva (MA3)
        pred_jan = (v_oct + v_nov + v_dec) / 3.0
        pred_fev = (v_nov + v_dec + pred_jan) / 3.0
        pred_mar = (v_dec + pred_jan + pred_fev) / 3.0

        df_q6 = pd.DataFrame(
            {
                "Mes_Ano": ["2026-01", "2026-02", "2026-03"],
                "Venda_Real": [real_jan, real_fev, real_mar],
                "Previsao_MA3": [pred_jan, pred_fev, pred_mar],
            }
        )
        df_q6["Erro_Absoluto"] = abs(df_q6["Venda_Real"] - df_q6["Previsao_MA3"])

        soma_pred = df_q6["Previsao_MA3"].sum()
        mae_val = df_q6["Erro_Absoluto"].mean()

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(
                "Soma Total Prevista (Trimestre)",
                f"{round(soma_pred)} unidades",
                f"{soma_pred:.2f} exatas",
            )
        with col_m2:
            st.metric("MAE Final (Mean Absolute Error)", f"{mae_val:.2f} unidades")
        with col_m3:
            if produto_sel_q6 == "Bússola de Bordo 702":
                st.error(
                    "⚠️ Alerta da Q6: O modelo subestimou a demanda de verão em Jan/26 por >57%!"
                )
            else:
                st.info(f"Simulação para: **{produto_sel_q6}**")

        fig_q6 = gg.Figure()
        fig_q6.add_trace(
            gg.Scatter(
                x=df_q6["Mes_Ano"],
                y=df_q6["Venda_Real"],
                mode="lines+markers+text",
                name="Venda Real",
                text=df_q6["Venda_Real"].astype(int),
                textposition="top center",
                line=dict(color="#00f2fe", width=3),
            )
        )
        fig_q6.add_trace(
            gg.Scatter(
                x=df_q6["Mes_Ano"],
                y=df_q6["Previsao_MA3"],
                mode="lines+markers+text",
                name="Previsão MA3",
                text=df_q6["Previsao_MA3"].round(2),
                textposition="bottom center",
                line=dict(color="#ff4b4b", width=3, dash="dash"),
            )
        )
        fig_q6.update_layout(
            template="plotly_dark",
            xaxis_title="Mês/Ano",
            yaxis_title="Unidades Vendidas",
        )
        st.plotly_chart(fig_q6, width="stretch")
    else:
        st.warning(
            f"Sem dados de vendas encontrados para o produto '{produto_sel_q6}'."
        )

# ==============================================================================
# ABA 4: RECOMENDADOR INTELIGENTE DE PRODUTOS (QUESTÃO 7)
# ==============================================================================
with tab4:
    st.markdown("### 🤖 Motor de Recomendação por Similaridade de Cosseno (Item-Item)")

    @st.cache_data(ttl=3600)
    def calcular_recomendacoes_produtos():
        """Calcula a matriz de cosseno entre produtos com base nas compras dos clientes."""
        query = """
        SELECT DISTINCT o.customer_id, p.name AS product_name
        FROM orders o 
        JOIN order_items oi ON o.id = oi.order_id 
        JOIN product_variants pv ON oi.product_variant_id = pv.id 
        JOIN products p ON pv.product_id = p.id
        WHERE o.status IN ('paid', 'confirmed');
        """
        df_rec = ler_sql(query)
        matrix = pd.crosstab(df_rec["customer_id"], df_rec["product_name"])
        matrix_bin = (matrix > 0).astype(int).values.astype(float)

        dot_product = np.dot(matrix_bin.T, matrix_bin)
        norms = np.linalg.norm(matrix_bin, axis=0)
        outer_norms = np.outer(norms, norms)
        with np.errstate(divide="ignore", invalid="ignore"):
            cosine_sim = np.true_divide(dot_product, outer_norms)
            cosine_sim[np.isnan(cosine_sim)] = 0.0
        return pd.DataFrame(cosine_sim, index=matrix.columns, columns=matrix.columns)

    sim_df = calcular_recomendacoes_produtos()
    produtos_lista = sorted(list(sim_df.columns))

    prod_selecionado = st.selectbox(
        "Selecione um Produto de Referência:",
        produtos_lista,
        index=(
            produtos_lista.index("Motor de Popa 1949")
            if "Motor de Popa 1949" in produtos_lista
            else 0
        ),
    )

    if prod_selecionado:
        top_rec = (
            sim_df[prod_selecionado]
            .drop(prod_selecionado)
            .drop(labels=["asdf"], errors="ignore")
            .sort_values(ascending=False)
            .head(5)
        )

        st.markdown(
            f"#### 🎯 Top 5 Recomendações para quem compra **'{prod_selecionado}'**:"
        )

        cols_rec = st.columns(5)
        # Converte os itens para uma lista limpa limitando a 5
        items_list = list(top_rec.items())[:5]
        for idx, (p_name, p_score) in enumerate(items_list):
            # Garante que o nome e os valores são strings/tipos primitivos seguros
            safe_name = str(p_name)
            with cols_rec[idx]:
                st.metric(
                    label=f"#{idx+1} {safe_name[:20]}...",
                    value=f"{p_score:.4f}",
                    delta=f"Score {p_score:.2%}",
                )
                st.caption(safe_name)


# ==============================================================================
# ABA 5: INTELIGÊNCIA LOGÍSTICA & VENDAS REGIONAIS (ANÁLISE COMPLEMENTAR)
# ==============================================================================
with tab5:
    st.markdown("### 🗺️ Inteligência Geográfica & Desempenho Regional")
    st.caption(
        "Visão estratégica por Estados (UF), Clientes Multi-Região e Mais Vendidos por Região."
    )

    # 1. Os 10 Produtos Mais Vendidos Globalmente
    st.markdown("#### 📦 1. Os 10 Produtos Mais Vendidos no Geral (Volume de Vendas)")
    df_p_global = carregar_top10_produtos_globais()
    fig_p_global = px.bar(
        df_p_global,
        x="total_unidades_vendidas",
        y="nome_produto",
        orientation="h",
        color="nome_categoria",
        text="total_unidades_vendidas",
        labels={
            "total_unidades_vendidas": "Unidades Vendidas",
            "nome_produto": "Produto",
            "nome_categoria": "Categoria",
        },
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig_p_global.update_layout(yaxis=dict(autorange="reversed"))
    fig_p_global.update_traces(textposition="outside")
    st.plotly_chart(fig_p_global, width="stretch")

    st.markdown("---")

    # 2. Quem comprou mais por Região (Top 5 Clientes por Estado)
    st.markdown("#### 🥇 2. Top 5 Clientes que Mais Compraram por Estado (UF)")
    df_cli_est = carregar_top5_clientes_por_estado()

    # Filtro de Estado para detalhamento da Tabela Top 5
    estados_disponiveis = sorted(list(df_cli_est["estado"].unique()))
    est_sel_tabela = st.selectbox(
        "Selecione o Estado para ver os Top 5 Clientes:",
        estados_disponiveis,
        index=0,
    )

    df_top5_est_filtrado = df_cli_est[df_cli_est["estado"] == est_sel_tabela]
    st.dataframe(
        df_top5_est_filtrado.style.format({"faturamento_total": "R$ {:,.2f}"}),
        width="stretch",
    )

    st.markdown("---")

    # 4. Os 5 Produtos Mais Vendidos na Região de Algum Estado (Filtro Dinâmico)
    st.markdown("#### 🎯 4. Os 5 Produtos Mais Vendidos em um Estado Específico")
    est_sel_prod = st.selectbox(
        "Selecione o Estado para Analisar os 5 Produtos Mais Vendidos:",
        estados_disponiveis,
        index=0,
        key="select_est_prod",
    )

    df_top5_prod_est = carregar_top5_produtos_por_estado_filtro(est_sel_prod)

    col_p_est_graf, col_p_est_tab = st.columns([1.5, 1])
    with col_p_est_graf:
        fig_p_est = px.bar(
            df_top5_prod_est,
            x="quantidade_vendida",
            y="nome_produto",
            orientation="h",
            color="faturamento_gerado",
            text="quantidade_vendida",
            labels={
                "quantidade_vendida": "Quantidade Vendida",
                "nome_produto": "Produto",
                "faturamento_gerado": "Faturamento (R$)",
            },
            template="plotly_dark",
            color_continuous_scale="Plasma",
        )
        fig_p_est.update_layout(yaxis=dict(autorange="reversed"))
        fig_p_est.update_traces(textposition="outside")
        st.plotly_chart(fig_p_est, width="stretch")

    with col_p_est_tab:
        st.write(f"**Detalhamento dos Produtos em {est_sel_prod}:**")
        st.dataframe(
            df_top5_prod_est.style.format({"faturamento_gerado": "R$ {:,.2f}"}),
            width="stretch",
        )
