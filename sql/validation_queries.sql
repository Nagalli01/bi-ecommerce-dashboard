-- ============================================
-- QUERIES DE VALIDAÇÃO — BI E-COMMERCE
-- ============================================
-- Queries para validação dos dados em cada camada
-- da Arquitetura Medalhão (Bronze → Silver → Gold).
-- Sintaxe: SQL padrão compatível com Spark SQL.

-- ============================================
-- 1. CONTAGEM DE REGISTROS POR CAMADA
-- ============================================
-- Verifica a preservação de registros através das camadas.
-- Esperado: contagens iguais ou muito próximas entre Bronze e Silver,
-- e Gold deve refletir o modelo dimensional esperado.
SELECT 'BRONZE - Clientes'        AS tabela, COUNT(*) AS registros FROM bronze_clientes
UNION ALL
SELECT 'BRONZE - Produtos',       COUNT(*) FROM bronze_produtos
UNION ALL
SELECT 'BRONZE - Pedidos',        COUNT(*) FROM bronze_pedidos
UNION ALL
SELECT 'SILVER - Clientes',       COUNT(*) FROM silver_clientes
UNION ALL
SELECT 'SILVER - Produtos',       COUNT(*) FROM silver_produtos
UNION ALL
SELECT 'SILVER - Pedidos',        COUNT(*) FROM silver_pedidos
UNION ALL
SELECT 'GOLD - dim_clientes',     COUNT(*) FROM gold.dim_clientes
UNION ALL
SELECT 'GOLD - dim_produtos',     COUNT(*) FROM gold.dim_produtos
UNION ALL
SELECT 'GOLD - dim_calendario',   COUNT(*) FROM gold.dim_calendario
UNION ALL
SELECT 'GOLD - dim_vendedores',   COUNT(*) FROM gold.dim_vendedores
UNION ALL
SELECT 'GOLD - fact_vendas',      COUNT(*) FROM gold.fact_vendas
ORDER BY tabela;

-- ============================================
-- 2. VERIFICAÇÃO DE CHAVES PRIMÁRIAS ÚNICAS
-- ============================================
-- Garante que não há duplicatas nas dimensões.

-- dim_clientes: PK deve ser única
SELECT 
    'dim_clientes - PK duplicadas' AS verificacao,
    COUNT(*) AS total_linhas,
    COUNT(DISTINCT id_cliente) AS valores_distintos,
    COUNT(*) - COUNT(DISTINCT id_cliente) AS duplicatas
FROM gold.dim_clientes;

-- dim_produtos: PK deve ser única
SELECT 
    'dim_produtos - PK duplicadas' AS verificacao,
    COUNT(*) AS total_linhas,
    COUNT(DISTINCT id_produto) AS valores_distintos,
    COUNT(*) - COUNT(DISTINCT id_produto) AS duplicatas
FROM gold.dim_produtos;

-- dim_calendario: PK deve ser única
SELECT 
    'dim_calendario - PK duplicadas' AS verificacao,
    COUNT(*) AS total_linhas,
    COUNT(DISTINCT data) AS valores_distintos,
    COUNT(*) - COUNT(DISTINCT data) AS duplicatas
FROM gold.dim_calendario;

-- dim_vendedores: PK deve ser única
SELECT 
    'dim_vendedores - PK duplicadas' AS verificacao,
    COUNT(*) AS total_linhas,
    COUNT(DISTINCT id_vendedor) AS valores_distintos,
    COUNT(*) - COUNT(DISTINCT id_vendedor) AS duplicatas
FROM gold.dim_vendedores;

-- ============================================
-- 3. VERIFICAÇÃO DE INTEGRIDADE REFERENCIAL
-- ============================================
-- Garante que todas as FKs na fato têm correspondência nas dimensões.

-- 3a. Pedidos sem cliente correspondente (órfãos)
SELECT 
    'Orfãos - Cliente' AS tipo_orfao,
    COUNT(*) AS quantidade
FROM gold.fact_vendas f
LEFT ANTI JOIN gold.dim_clientes d 
    ON f.id_cliente = d.id_cliente;

-- 3b. Pedidos sem produto correspondente
SELECT 
    'Orfãos - Produto' AS tipo_orfao,
    COUNT(*) AS quantidade
FROM gold.fact_vendas f
LEFT ANTI JOIN gold.dim_produtos d 
    ON f.id_produto = d.id_produto;

-- 3c. Pedidos sem data no calendário
SELECT 
    'Orfãos - Calendario' AS tipo_orfao,
    COUNT(*) AS quantidade
FROM gold.fact_vendas f
LEFT ANTI JOIN gold.dim_calendario d 
    ON f.data_pedido = d.data;

-- 3d. Pedidos sem vendedor correspondente
SELECT 
    'Orfãos - Vendedor' AS tipo_orfao,
    COUNT(*) AS quantidade
FROM gold.fact_vendas f
LEFT ANTI JOIN gold.dim_vendedores d 
    ON f.id_vendedor = d.id_vendedor;

-- 3e. Verificação de FKs nulas
SELECT 
    'FKs Nulas' AS verificacao,
    SUM(CASE WHEN id_cliente IS NULL THEN 1 ELSE 0 END)  AS id_cliente_nulos,
    SUM(CASE WHEN id_produto IS NULL THEN 1 ELSE 0 END)  AS id_produto_nulos,
    SUM(CASE WHEN data_pedido IS NULL THEN 1 ELSE 0 END) AS data_pedido_nulos,
    SUM(CASE WHEN id_vendedor IS NULL THEN 1 ELSE 0 END) AS id_vendedor_nulos
FROM gold.fact_vendas;

-- ============================================
-- 4. KPIs PRINCIPAIS (VALIDAÇÃO DE NEGÓCIO)
-- ============================================
-- Valida os valores principais do dashboard.
SELECT 
    SUM(total_pedido)                        AS faturamento_total,
    COUNT(*)                                 AS total_itens_vendidos,
    COUNT(DISTINCT pedido_id)                AS total_pedidos_unicos,
    ROUND(SUM(total_pedido) / COUNT(DISTINCT pedido_id), 2) AS ticket_medio,
    COUNT(DISTINCT id_vendedor)              AS total_vendedores,
    COUNT(DISTINCT id_cliente)               AS total_clientes_ativos,
    ROUND(AVG(valor_frete), 2)               AS frete_medio,
    ROUND(SUM(quantidade) * 1.0 / COUNT(DISTINCT pedido_id), 2) AS media_itens_pedido
FROM gold.fact_vendas;

-- ============================================
-- 5. TOP 5 ESTADOS POR FATURAMENTO
-- ============================================
-- Valida a distribuição geográfica.
SELECT 
    f.estado,
    SUM(f.total_pedido)                   AS faturamento,
    COUNT(DISTINCT f.pedido_id)            AS pedidos,
    COUNT(DISTINCT f.id_cliente)           AS clientes,
    ROUND(SUM(f.total_pedido) / COUNT(DISTINCT f.pedido_id), 2) AS ticket_medio_estado
FROM gold.fact_vendas f
GROUP BY f.estado
ORDER BY faturamento DESC
LIMIT 5;

-- ============================================
-- 6. TOP 5 CATEGORIAS POR FATURAMENTO
-- ============================================
-- Valida a distribuição por categoria de produto.
SELECT 
    p.categoria,
    SUM(f.total_pedido)                    AS faturamento,
    COUNT(*)                               AS itens_vendidos,
    COUNT(DISTINCT f.pedido_id)            AS pedidos,
    COUNT(DISTINCT p.id_produto)           AS produtos_distintos
FROM gold.fact_vendas f
JOIN gold.dim_produtos p ON f.id_produto = p.id_produto
GROUP BY p.categoria
ORDER BY faturamento DESC
LIMIT 5;

-- ============================================
-- 7. EVOLUÇÃO MENSAL DE FATURAMENTO
-- ============================================
-- Valida os dados para o gráfico de evolução mensal.
SELECT 
    c.ano,
    c.nome_mes,
    c.mes_num,
    SUM(f.total_pedido)                    AS faturamento,
    COUNT(DISTINCT f.pedido_id)            AS pedidos,
    ROUND(SUM(f.total_pedido) / COUNT(DISTINCT f.pedido_id), 2) AS ticket_medio
FROM gold.fact_vendas f
JOIN gold.dim_calendario c ON f.data_pedido = c.data
GROUP BY c.ano, c.nome_mes, c.mes_num
ORDER BY c.ano, c.mes_num;

-- ============================================
-- 8. RANKING COMPLETO DE VENDEDORES
-- ============================================
-- Valida os dados para a tabela de ranking.
SELECT 
    ROW_NUMBER() OVER (ORDER BY SUM(f.total_pedido) DESC) AS ranking,
    v.nome,
    v.regiao,
    SUM(f.total_pedido)                    AS faturamento,
    COUNT(DISTINCT f.pedido_id)            AS pedidos,
    ROUND(SUM(f.total_pedido) * 100.0 / 
          SUM(SUM(f.total_pedido)) OVER (), 2) AS participacao_pct
FROM gold.fact_vendas f
JOIN gold.dim_vendedores v ON f.id_vendedor = v.id_vendedor
GROUP BY v.nome, v.regiao
ORDER BY faturamento DESC;

-- ============================================
-- 9. DISTRIBUIÇÃO DE PEDIDOS POR REGIÃO
-- ============================================
-- Valida a distribuição regional.
SELECT 
    regiao,
    COUNT(DISTINCT pedido_id)              AS pedidos,
    SUM(total_pedido)                      AS faturamento,
    COUNT(DISTINCT id_cliente)             AS clientes,
    COUNT(DISTINCT estado)                 AS estados_atendidos,
    COUNT(DISTINCT municipio)              AS municipios_atendidos,
    ROUND(SUM(valor_frete) / COUNT(DISTINCT pedido_id), 2) AS frete_medio
FROM gold.fact_vendas
GROUP BY regiao
ORDER BY faturamento DESC;

-- ============================================
-- 10. ANÁLISE DE ITENS POR PEDIDO
-- ============================================
-- Valida a quantidade de itens por pedido.
SELECT 
    ROUND(AVG(itens), 2)                    AS media_itens_pedido,
    MIN(itens)                              AS min_itens,
    MAX(itens)                              AS max_itens,
    PERCENTILE(itens, 0.5)                  AS mediana_itens,
    PERCENTILE(itens, 0.25)                 AS q1_itens,
    PERCENTILE(itens, 0.75)                 AS q3_itens
FROM (
    SELECT 
        pedido_id, 
        SUM(quantidade) AS itens
    FROM gold.fact_vendas
    GROUP BY pedido_id
) t;

-- ============================================
-- 11. VALIDAÇÃO DE RANGES (VALORES NEGATIVOS OU ZERADOS)
-- ============================================
SELECT 
    'Valores zerados ou negativos' AS verificacao,
    SUM(CASE WHEN total_pedido <= 0 THEN 1 ELSE 0 END)    AS total_pedido_invalido,
    SUM(CASE WHEN quantidade <= 0 THEN 1 ELSE 0 END)      AS quantidade_invalida,
    SUM(CASE WHEN preco_venda <= 0 THEN 1 ELSE 0 END)     AS preco_venda_invalido,
    SUM(CASE WHEN valor_frete < 0 THEN 1 ELSE 0 END)      AS frete_negativo
FROM gold.fact_vendas f
JOIN gold.dim_produtos p ON f.id_produto = p.id_produto;

-- ============================================
-- 12. VERIFICAÇÃO DE COBERTURA DO CALENDÁRIO
-- ============================================
-- Garante que o calendário cobre todo o período da fato.
SELECT 
    MIN(f.data_pedido) AS primeira_data_pedido,
    MAX(f.data_pedido) AS ultima_data_pedido,
    MIN(c.data)       AS primeira_data_calendario,
    MAX(c.data)       AS ultima_data_calendario,
    DATEDIFF(MAX(f.data_pedido), MIN(f.data_pedido)) AS intervalo_pedidos_dias,
    DATEDIFF(MAX(c.data), MIN(c.data))               AS intervalo_calendario_dias
FROM gold.fact_vendas f
CROSS JOIN (
    SELECT MIN(data) AS data FROM gold.dim_calendario
    UNION ALL
    SELECT MAX(data) AS data FROM gold.dim_calendario
) c;

-- ============================================
-- 13. CARDINALIDADE DAS DIMENSÕES
-- ============================================
-- Resumo do modelo dimensional.
SELECT 'dim_clientes'    AS dimensao, COUNT(*) AS registros, COUNT(DISTINCT id_cliente)   AS pk_unicas FROM gold.dim_clientes
UNION ALL
SELECT 'dim_produtos',              COUNT(*), COUNT(DISTINCT id_produto)                 FROM gold.dim_produtos
UNION ALL
SELECT 'dim_calendario',            COUNT(*), COUNT(DISTINCT data)                       FROM gold.dim_calendario
UNION ALL
SELECT 'dim_vendedores',            COUNT(*), COUNT(DISTINCT id_vendedor)                FROM gold.dim_vendedores;

-- ============================================
-- 14. TOP 10 MUNICÍPIOS POR FATURAMENTO
-- ============================================
SELECT 
    municipio,
    estado,
    SUM(total_pedido)                      AS faturamento,
    COUNT(DISTINCT pedido_id)              AS pedidos,
    COUNT(DISTINCT id_cliente)             AS clientes
FROM gold.fact_vendas
GROUP BY municipio, estado
ORDER BY faturamento DESC
LIMIT 10;

-- ============================================
-- 15. VENDEDORES POR REGIÃO (VALIDAÇÃO CRUZADA)
-- ============================================
-- Verifica se todos os vendedores de uma região
-- realmente operam naquela região.
SELECT 
    v.id_vendedor,
    v.nome,
    v.regiao AS regiao_cadastro,
    f.regiao AS regiao_venda,
    COUNT(DISTINCT f.pedido_id) AS total_pedidos
FROM gold.dim_vendedores v
JOIN gold.fact_vendas f ON v.id_vendedor = f.id_vendedor
GROUP BY v.id_vendedor, v.nome, v.regiao, f.regiao
ORDER BY v.id_vendedor, total_pedidos DESC;
