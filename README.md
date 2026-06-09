# 🛒 BI E-Commerce — Arquitetura Medalhão com PySpark + Delta Lake

Projeto acadêmico de Engenharia de Dados e Business Intelligence para uma empresa de e-commerce de eletrônicos.

## 🎯 Objetivo

Transformar dados transacionais de **clientes, produtos e pedidos** em um **modelo dimensional (Star Schema)** e um **dashboard executivo no Power BI**, utilizando **Arquitetura Medalhão (Bronze → Silver → Gold)**.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA MEDALHÃO                          │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  BRONZE  │ →  │  SILVER  │ →  │   GOLD   │ →  │  POWER   │  │
│  │  ─────── │    │  ─────── │    │  ─────── │    │   BI     │  │
│  │  Parquet │    │  Delta   │    │  Delta   │    │ Dashboar │  │
│  │  Dados   │    │  Curados │    │  Star    │    │  3 Págs  │  │
│  │  Brutos  │    │  Limpos  │    │  Schema  │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                                 │
│  3 tabelas       3 tabelas       4 dims +         Medidas DAX   │
│  origem          transformadas   1 fato          Visuais        │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Dados

| Entidade  | Registros | Descrição |
|-----------|-----------|-----------|
| Clientes  | 1.500     | Cadastro de clientes com localização |
| Produtos  | 250       | Catálogo de produtos eletrônicos |
| Pedidos   | 8.000     | Transações de venda (itens de pedido) |

**Período:** 2 anos de dados (calendário com ~730 dias)

## 🚀 Execução Rápida

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Gerar dados e executar pipeline completo
python src/run_pipeline.py

# 3. Verificar qualidade
python src/40_quality_checks.py

# 4. (Opcional) Abrir notebooks
jupyter notebook notebooks/
```

## 📁 Estrutura do Projeto

```
bi_ecommerce/
├── data/
│   ├── raw/             # Dados gerados (Parquet)
│   │   ├── clientes.parquet
│   │   ├── produtos.parquet
│   │   └── pedidos.parquet
│   ├── bronze/          # Camada Bronze (Delta)
│   │   ├── clientes/
│   │   ├── produtos/
│   │   └── pedidos/
│   ├── silver/          # Camada Silver (Delta)
│   │   ├── clientes/
│   │   ├── produtos/
│   │   └── pedidos/
│   └── gold/            # Camada Gold | Star Schema (Delta)
│       ├── dim_clientes/
│       ├── dim_produtos/
│       ├── dim_calendario/
│       ├── dim_vendedores/
│       └── fact_vendas/
├── src/                 # Scripts Python do pipeline
│   ├── 00_generate_data.py
│   ├── 01_validate_inputs.py
│   ├── 10_bronze_ingestion.py
│   ├── 20_silver_transform.py
│   ├── 30_gold_model.py
│   ├── 40_quality_checks.py
│   └── run_pipeline.py
├── notebooks/           # Jupyter Notebooks PySpark
├── diagrams/            # Diagramas (Mermaid)
│   ├── architecture_medallion.md
│   ├── dimensional_model.md
│   ├── pipeline_flow.md
│   └── dashboard_layout.md
├── powerbi/             # Especificação do Dashboard
│   ├── dax_measures.txt
│   ├── model_relationships.txt
│   └── dashboard_spec.txt
├── sql/                 # Scripts SQL de referência
│   ├── create_tables.sql
│   └── validation_queries.sql
├── docs/                # Documentação técnica e funcional
├── requirements.txt     # Dependências Python
└── README.md            # Este arquivo
```

## 🔗 Modelo Dimensional (Star Schema)

```
                 ┌─────────────────┐
                 │  dim_clientes   │
                 │  ─────────────  │
                 │  PK: id_cliente │
                 └────────┬────────┘
                          │ (1:N)
                 ┌────────┴────────┐
                 │  dim_produtos   │
                 │  ─────────────  │
                 │  PK: id_produto │
                 └────────┬────────┘
                          │ (1:N)
    ┌─────────────────────┼─────────────────────┐
    │              ┌──────┴──────┐              │
    │              │ fact_vendas  │              │
    │              │ ─────────── │              │
    │              │ pedido_id    │              │
    │              │ id_cliente FK│              │
    │              │ id_produto FK│              │
    │              │data_pedido FK│              │
    │              │id_vendedor FK│              │
    │              └──────┬──────┘              │
    │                     │ (1:N)               │
    │  ┌──────────────────┴──────────────────┐  │
    │  │           dim_calendario            │  │
    │  │           ─────────────             │  │
    │  │           PK: data                  │  │
    │  └─────────────────────────────────────┘  │
    │                                           │
    │  ┌──────────────────┐                     │
    │  │ dim_vendedores   │                     │
    │  │ ─────────────    │                     │
    │  │ PK: id_vendedor  │                     │
    │  └──────────────────┘                     │
    └───────────────────────────────────────────┘
```

### Relacionamentos

| Fato | Chave | Dimensão | Chave | Card. |
|------|-------|----------|-------|-------|
| fact_vendas | id_cliente | dim_clientes | id_cliente | N:1 |
| fact_vendas | id_produto | dim_produtos | id_produto | N:1 |
| fact_vendas | data_pedido | dim_calendario | data | N:1 |
| fact_vendas | id_vendedor | dim_vendedores | id_vendedor | N:1 |

## 📈 KPIs

| KPI | Medida DAX | Descrição |
|-----|-----------|-----------|
| **Faturamento** | `SUM(total_pedido)` | Receita total |
| **Total Pedidos** | `COUNTROWS(fact_vendas)` | Volume de transações |
| **Ticket Médio** | `DIVIDE(Faturamento, Pedidos)` | Valor médio por pedido |
| **Total Vendedores** | `DISTINCTCOUNT(id_vendedor)` | Força de vendas (15) |
| **Crescimento MoM** | Variação mês a mês | Tendência mensal |

## 📊 Dashboard (Power BI)

### Página 1 — Visão Executiva
- 4 KPI Cards (Faturamento, Pedidos, Ticket Médio, Vendedores)
- Faturamento por Estado e Região (barras horizontais)
- Top 10 Municípios e Ranking de Vendedores
- Evolução Mensal (gráfico de área)

### Página 2 — Vendedores
- Melhor Vendedor e Faturamento Médio
- Ranking completo (15 vendedores)
- Participação % (gráfico de rosca) e Faturamento por Região

### Página 3 — Geográfica
- Faturamento por Estado e Região
- Top 15 Municípios

**Tema:** Dark mode (#262626 fundo, #323130 visuais, branco texto, Segoe UI)

## 🛠️ Tecnologias

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **PySpark** | 3.4+ | Processamento distribuído (modo local) |
| **Delta Lake** | 3.0+ | Armazenamento transacional ACID |
| **Python** | 3.10+ | Orquestração do pipeline |
| **Pandas** | 2.0+ | Manipulação de dados auxiliar |
| **Faker** | 22.0+ | Geração de dados sintéticos |
| **Power BI Desktop** | — | Visualização e dashboard |

## 🔄 Pipeline de Dados

| Etapa | Script | Entrada | Saída |
|-------|--------|---------|-------|
| Geração | `00_generate_data.py` | — | `data/raw/*.parquet` |
| Validação | `01_validate_inputs.py` | `data/raw/` | `validation_log.txt` |
| Bronze | `10_bronze_ingestion.py` | `data/raw/` | `data/bronze/*/` (Delta) |
| Silver | `20_silver_transform.py` | `data/bronze/` | `data/silver/*/` (Delta) |
| Gold | `30_gold_model.py` | `data/silver/` | `data/gold/*/` (Delta) |
| Qualidade | `40_quality_checks.py` | `data/gold/` | `quality_report.txt` |

## 📚 Documentação

| Documento | Conteúdo |
|-----------|----------|
| [diagrams/architecture_medallion.md](diagrams/architecture_medallion.md) | Diagrama da Arquitetura Medalhão |
| [diagrams/dimensional_model.md](diagrams/dimensional_model.md) | Diagrama do Modelo Dimensional |
| [diagrams/pipeline_flow.md](diagrams/pipeline_flow.md) | Fluxo de Execução do Pipeline |
| [diagrams/dashboard_layout.md](diagrams/dashboard_layout.md) | Layout do Dashboard |
| [powerbi/dax_measures.txt](powerbi/dax_measures.txt) | Medidas DAX completas |
| [powerbi/model_relationships.txt](powerbi/model_relationships.txt) | Especificação do Modelo Semântico |
| [powerbi/dashboard_spec.txt](powerbi/dashboard_spec.txt) | Especificação de Construção |
| [sql/create_tables.sql](sql/create_tables.sql) | Scripts DDL de referência |
| [sql/validation_queries.sql](sql/validation_queries.sql) | Queries de Validação |

## 👥 Equipe

Projeto acadêmico — 4 integrantes.

## 📝 Licença

Projeto acadêmico — uso livre para fins educacionais.
