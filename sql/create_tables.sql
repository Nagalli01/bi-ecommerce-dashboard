-- ============================================
-- DDL — MODELO DIMENSIONAL BI E-COMMERCE
-- ============================================
-- Script de referência. As tabelas são criadas via PySpark/Delta Lake.
-- Este SQL serve como documentação da estrutura do modelo dimensional.

-- ============================================
-- DIMENSÃO: CLIENTES
-- ============================================
-- Granularidade: 1 linha por cliente
-- Registros esperados: ~1.500
-- Tipo SCD: Tipo 1 (sobrescrever alterações)
CREATE TABLE dim_clientes (
    id_cliente   INT            NOT NULL,
    nome         VARCHAR(200)   NOT NULL,
    cidade       VARCHAR(100),
    estado       CHAR(2),
    regiao       VARCHAR(50),
    CONSTRAINT pk_dim_clientes PRIMARY KEY (id_cliente)
);

-- ============================================
-- DIMENSÃO: PRODUTOS
-- ============================================
-- Granularidade: 1 linha por produto
-- Registros esperados: ~250
-- Tipo SCD: Tipo 1 (sobrescrever alterações)
CREATE TABLE dim_produtos (
    id_produto   VARCHAR(20)    NOT NULL,
    nome_produto VARCHAR(200)   NOT NULL,
    categoria    VARCHAR(100),
    preco_venda  DECIMAL(10,2)  NOT NULL,
    CONSTRAINT pk_dim_produtos PRIMARY KEY (id_produto)
);

-- ============================================
-- DIMENSÃO: CALENDÁRIO
-- ============================================
-- Granularidade: 1 linha por dia
-- Registros esperados: ~730 (2 anos)
-- Tipo SCD: Não se aplica (dimensão estática de data)
CREATE TABLE dim_calendario (
    data         DATE           NOT NULL,
    dia          INT,
    mes          INT,
    nome_mes     VARCHAR(20),
    mes_num      INT,
    trimestre    INT,
    ano          INT,
    CONSTRAINT pk_dim_calendario PRIMARY KEY (data)
);

-- ============================================
-- DIMENSÃO: VENDEDORES
-- ============================================
-- Granularidade: 1 linha por vendedor
-- Registros esperados: 15
-- Tipo SCD: Tipo 1 (sobrescrever alterações)
CREATE TABLE dim_vendedores (
    id_vendedor  INT            NOT NULL,
    nome         VARCHAR(200)   NOT NULL,
    regiao       VARCHAR(50),
    CONSTRAINT pk_dim_vendedores PRIMARY KEY (id_vendedor)
);

-- ============================================
-- FATO: VENDAS
-- ============================================
-- Granularidade: 1 linha por item de pedido
-- Registros esperados: ~8.000
-- Particionamento sugerido: por ano/mês da data_pedido
-- Granularidade da fato: Item do pedido (pedido_id + id_produto = chave degenerada)
CREATE TABLE fact_vendas (
    pedido_id    INT            NOT NULL,
    id_cliente   INT            NOT NULL,
    id_produto   VARCHAR(20)    NOT NULL,
    data_pedido  DATE           NOT NULL,
    id_vendedor  INT            NOT NULL,
    quantidade   INT            NOT NULL,
    valor_frete  DECIMAL(10,2),
    total_pedido DECIMAL(10,2)  NOT NULL,
    municipio    VARCHAR(100),
    estado       CHAR(2),
    regiao       VARCHAR(50),

    -- Chaves estrangeiras
    CONSTRAINT fk_fact_cliente   FOREIGN KEY (id_cliente)  REFERENCES dim_clientes(id_cliente),
    CONSTRAINT fk_fact_produto   FOREIGN KEY (id_produto)  REFERENCES dim_produtos(id_produto),
    CONSTRAINT fk_fact_data      FOREIGN KEY (data_pedido) REFERENCES dim_calendario(data),
    CONSTRAINT fk_fact_vendedor  FOREIGN KEY (id_vendedor) REFERENCES dim_vendedores(id_vendedor)
);

-- ============================================
-- ÍNDICES PARA PERFORMANCE DE CONSULTA
-- ============================================
CREATE INDEX idx_fact_cliente   ON fact_vendas(id_cliente);
CREATE INDEX idx_fact_produto   ON fact_vendas(id_produto);
CREATE INDEX idx_fact_data      ON fact_vendas(data_pedido);
CREATE INDEX idx_fact_vendedor  ON fact_vendas(id_vendedor);
CREATE INDEX idx_fact_pedido    ON fact_vendas(pedido_id);

-- Índices nas dimensões para buscas por nome/região
CREATE INDEX idx_dim_cliente_nome   ON dim_clientes(nome);
CREATE INDEX idx_dim_cliente_estado ON dim_clientes(estado);
CREATE INDEX idx_dim_cliente_regiao ON dim_clientes(regiao);
CREATE INDEX idx_dim_produto_nome   ON dim_produtos(nome_produto);
CREATE INDEX idx_dim_produto_cat    ON dim_produtos(categoria);
CREATE INDEX idx_dim_cal_ano_mes    ON dim_calendario(ano, mes);
CREATE INDEX idx_dim_vend_regiao    ON dim_vendedores(regiao);
CREATE INDEX idx_dim_vend_nome      ON dim_vendedores(nome);

-- ============================================
-- EQUIVALENTE PYSPARK/DELTA LAKE
-- ============================================
-- As tabelas acima são criadas via PySpark com Delta Lake.
-- Exemplo de criação no PySpark:
--
-- from pyspark.sql import SparkSession
-- from delta.tables import DeltaTable
--
-- spark = SparkSession.builder \
--     .appName("BI-Ecommerce") \
--     .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
--     .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
--     .getOrCreate()
--
-- # Criar dim_clientes
-- spark.sql("""
--     CREATE TABLE IF NOT EXISTS gold.dim_clientes (
--         id_cliente INT,
--         nome STRING,
--         cidade STRING,
--         estado STRING,
--         regiao STRING
--     ) USING DELTA
-- """)
--
-- # Criar fact_vendas com particionamento
-- spark.sql("""
--     CREATE TABLE IF NOT EXISTS gold.fact_vendas (
--         pedido_id INT,
--         id_cliente INT,
--         id_produto STRING,
--         data_pedido DATE,
--         id_vendedor INT,
--         quantidade INT,
--         valor_frete DECIMAL(10,2),
--         total_pedido DECIMAL(10,2),
--         municipio STRING,
--         estado STRING,
--         regiao STRING
--     ) USING DELTA
--     PARTITIONED BY (estado)
-- """)
-- ============================================
