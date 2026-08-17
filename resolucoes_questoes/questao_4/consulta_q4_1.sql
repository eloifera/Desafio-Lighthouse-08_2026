-- 1. Identificação dos Top 10 Clientes de Elite
WITH cliente_metricas AS (
    SELECT o.customer_id,
        SUM(CAST(o.total AS NUMERIC)) AS faturamento_total,
        COUNT(DISTINCT o.id) AS frequencia,
        SUM(CAST(o.total AS NUMERIC)) / COUNT(DISTINCT o.id) AS ticket_medio,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN product_variants pv ON oi.product_variant_id = pv.id
        JOIN products p ON pv.product_id = p.id
    GROUP BY o.customer_id
    HAVING COUNT(DISTINCT p.category_id) >= 13
)
SELECT customer_id,
    ROUND(faturamento_total, 2) AS faturamento_total,
    frequencia,
    ROUND(ticket_medio, 2) AS ticket_medio,
    diversidade_categorias
FROM cliente_metricas
ORDER BY ticket_medio DESC,
    customer_id ASC
LIMIT 10;
-- 2. Categoria mais vendida em quantidade para os Top 10 Clientes
WITH cliente_metricas AS (
    SELECT o.customer_id,
        SUM(CAST(o.total AS NUMERIC)) AS faturamento_total,
        COUNT(DISTINCT o.id) AS frequencia,
        SUM(CAST(o.total AS NUMERIC)) / COUNT(DISTINCT o.id) AS ticket_medio,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN product_variants pv ON oi.product_variant_id = pv.id
        JOIN products p ON pv.product_id = p.id
    GROUP BY o.customer_id
    HAVING COUNT(DISTINCT p.category_id) >= 13
),
top10_clientes AS (
    SELECT customer_id,
        ticket_medio
    FROM cliente_metricas
    ORDER BY ticket_medio DESC,
        customer_id ASC
    LIMIT 10
)
SELECT c.id AS category_id,
    c.name AS nome_categoria,
    SUM(CAST(oi.quantity AS NUMERIC)) AS total_itens_comprados
FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    JOIN categories c ON p.category_id = c.id
WHERE o.customer_id IN (
        SELECT customer_id
        FROM top10_clientes
    )
GROUP BY c.id,
    c.name
ORDER BY total_itens_comprados DESC;