# 🛒 BI E-Commerce — Pipeline ETL + Dashboard

Projeto acadêmico de Engenharia de Dados e Business Intelligence para e-commerce de eletrônicos.

**Dashboard online:** https://Nagalli-01-bi-ecommerce-dashboard.hf.space

## Arquitetura

Medallion (Bronze -> Silver -> Gold -> Star Schema), pandas + pyarrow, MySQL/SQLite.

## Dados

| Entidade  | Registros | Descrição |
|-----------|-----------|-----------|
| Clientes  | 1.500     | Cadastro com localização |
| Produtos  | 250       | Catálogo de eletrônicos |
| Pedidos   | 8.000     | Transações de venda |

Faturamento: R\$ 179,6M | Pipeline: 3,9s end-to-end

## Execução Rápida

```bash
pip install -r requirements.txt
python src/run_pipeline.py        # pipeline completo
streamlit run src/dashboard_app.py # dashboard local
# ou: run_dashboard.bat
```

## Estrutura

```
bi_ecommerce/
├── src/              # Pipeline ETL + Dashboard
│   ├── *.py          # 00 a 40 pipeline scripts
│   ├── run_pipeline.py
│   ├── dashboard_app.py   # Streamlit (MySQL)
│   ├── dashboard_web.py   # Streamlit (SQLite)
│   ├── setup_mysql.py
│   └── export_sqlite.py
├── deploy/           # Deploy Hugging Face Spaces
│   ├── app.py, Dockerfile, requirements.txt
│   └── bi_ecommerce.db
├── data/             # Dados gerados
├── notebooks/        # Jupyter Notebooks
├── diagrams/         # Diagramas Mermaid
├── powerbi/          # Especificacao Power BI
├── docs/             # Documentacao
├── sql/              # Scripts DDL
└── requirements.txt
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

## Dashboard (Streamlit)

4 páginas profissionais com KPIs, filtros interativos e gráficos Plotly.
Dark theme (#262626 / #323130), paleta de cores por tipo de gráfico.

| Página | Conteúdo |
|--------|----------|
| Visão Executiva | 4 KPIs + Fat. Estado/Região + Top 10 Municípios + Ranking Vendedores + Evolução Mensal (MoM) |
| Vendedores | 2 KPIs + Ranking com medalhas 🥇🥈🥉 + Donut + Barras Empilhadas por Região |
| Produtos | 3 KPIs + Fat. Categoria + Top 10 Produtos + Detalhamento |
| Geográfica | Fat. Estado + Fat. Região + Top 15 Municípios |

**Online:** https://Nagalli-01-bi-ecommerce-dashboard.hf.space
**GitHub:** https://github.com/Nagalli01/bi-ecommerce-dashboard

## Dashboard Online

**URL:** https://Nagalli-01-bi-ecommerce-dashboard.hf.space

3 páginas: Visão Executiva | Vendedores | Produtos & Categorias
Dark theme, filtros por ano/região/estado/categoria, Plotly interativo.

## Deploy

O deploy foi feito no Hugging Face Spaces (Docker + Streamlit).
Para deploy próprio, veja `docs/DEPLOY_GUIDE.md`.

## Tecnologias

Python, pandas, pyarrow, Streamlit, Plotly, SQLite, MySQL.

## Pipeline

| Etapa | Script |
|-------|--------|
| Geração | `00_generate_data.py` |
| Validação | `01_validate_inputs.py` |
| Bronze | `10_bronze_ingestion.py` |
| Silver | `20_silver_transform.py` |
| Gold | `30_gold_model.py` |
| Qualidade | `40_quality_checks.py` |

## Documentação

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
