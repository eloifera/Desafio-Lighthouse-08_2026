-- 1. Dimensão de Calendário contendo todos os dias corridos entre a menor e a maior data
WITH calendario AS (
    SELECT generate_series(
        (SELECT MIN(created_at::date) FROM orders WHERE channel = 'pos'),
        (SELECT MAX(created_at::date) FROM orders WHERE channel = 'pos'),
        '1 day'::interval
    )::date AS data
),

-- 2. Agregação das vendas diárias por data na loja física (pos)
vendas_diarias AS (
    SELECT 
        created_at::date AS data_venda,
        SUM(CAST(total AS NUMERIC)) AS valor_venda_dia
    FROM orders
    WHERE channel = 'pos'
    GROUP BY created_at::date
),

-- 3. LEFT JOIN entre o Calendário e as Vendas Diárias (Dias sem vendas recebem 0)
calendario_com_vendas AS (
    SELECT 
        c.data,
        EXTRACT(DOW FROM c.data) AS num_dia_semana,
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

-- 4. Cálculo da média real diária considerando todos os dias do calendário
SELECT 
    dia_semana,
    COUNT(*) AS total_dias_no_calendario,
    SUM(CASE WHEN valor_venda > 0 THEN 1 ELSE 0 END) AS dias_com_venda,
    SUM(CASE WHEN valor_venda = 0 THEN 1 ELSE 0 END) AS dias_sem_venda,
    ROUND(SUM(valor_venda), 2) AS faturamento_total,
    ROUND(AVG(valor_venda), 2) AS media_vendas_correta
FROM calendario_com_vendas
GROUP BY dia_semana, num_dia_semana
ORDER BY media_vendas_correta ASC;
