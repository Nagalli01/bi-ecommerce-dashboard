# 📐 Modelo Dimensional — Star Schema

## Diagrama Entidade-Relacionamento (ER)

```mermaid
erDiagram
    dim_clientes {
        INT id_cliente PK "Chave primária"
        VARCHAR nome "Nome completo do cliente"
        VARCHAR cidade "Cidade de residência"
        CHAR estado "UF — 2 caracteres"
        VARCHAR regiao "Norte|Nordeste|Centro-Oeste|Sudeste|Sul"
    }

    dim_produtos {
        VARCHAR id_produto PK "Chave primária — código alfanumérico"
        VARCHAR nome_produto "Nome descritivo do produto"
        VARCHAR categoria "Categoria do produto eletrônico"
        DECIMAL preco_venda "Preço unitário de venda em R$"
    }

    dim_calendario {
        DATE data PK "Chave primária — data completa"
        INT dia "Dia do mês (1-31)"
        INT mes "Número do mês (1-12)"
        VARCHAR nome_mes "Nome do mês em português (Jan-Dez)"
        INT mes_num "Número do mês para ordenação (1-12)"
        INT trimestre "Trimestre (1-4)"
        INT ano "Ano (ex: 2024, 2025)"
    }

    dim_vendedores {
        INT id_vendedor PK "Chave primária"
        VARCHAR nome "Nome do vendedor"
        VARCHAR regiao "Região de atuação do vendedor"
    }

    fact_vendas {
        INT pedido_id "ID do pedido (não único — chave degenerada)"
        INT id_cliente FK "FK → dim_clientes"
        VARCHAR id_produto FK "FK → dim_produtos"
        DATE data_pedido FK "FK → dim_calendario"
        INT id_vendedor FK "FK → dim_vendedores"
        INT quantidade "Quantidade de itens"
        DECIMAL valor_frete "Valor do frete em R$"
        DECIMAL total_pedido "Valor total do pedido em R$"
        VARCHAR municipio "Município da entrega"
        CHAR estado "UF da entrega"
        VARCHAR regiao "Região da entrega"
    }

    dim_clientes ||--o{ fact_vendas : "id_cliente (1:N)"
    dim_produtos ||--o{ fact_vendas : "id_produto (1:N)"
    dim_calendario ||--o{ fact_vendas : "data → data_pedido (1:N)"
    dim_vendedores ||--o{ fact_vendas : "id_vendedor (1:N)"
```

## Diagrama Esquemático (Estilo Flowchart)

```mermaid
flowchart LR
    subgraph DIMS["📦 DIMENSÕES"]
        direction TB
        D_CLI["**dim_clientes**<br/>───<br/>🔑 id_cliente<br/>nome<br/>cidade<br/>estado<br/>regiao<br/>───<br/>~1.500 registros"]

        D_PROD["**dim_produtos**<br/>───<br/>🔑 id_produto<br/>nome_produto<br/>categoria<br/>preco_venda<br/>───<br/>~250 registros"]

        D_CAL["**dim_calendario**<br/>───<br/>🔑 data<br/>dia • mes<br/>nome_mes<br/>mes_num • trimestre<br/>ano<br/>───<br/>~730 registros (2 anos)"]

        D_VEN["**dim_vendedores**<br/>───<br/>🔑 id_vendedor<br/>nome<br/>regiao<br/>───<br/>15 registros"]
    end

    FACT["**fact_vendas**<br/>───<br/>pedido_id<br/>🔗 id_cliente (FK)<br/>🔗 id_produto (FK)<br/>🔗 data_pedido (FK)<br/>🔗 id_vendedor (FK)<br/>quantidade<br/>valor_frete<br/>total_pedido<br/>municipio<br/>estado<br/>regiao<br/>───<br/>~8.000 registros"]

    D_CLI -- "N:1" --> FACT
    D_PROD -- "N:1" --> FACT
    D_CAL -- "N:1" --> FACT
    D_VEN -- "N:1" --> FACT

    style D_CLI fill:#1A3A5C,stroke:#4A90D9,color:#FFFFFF
    style D_PROD fill:#1A3A5C,stroke:#4A90D9,color:#FFFFFF
    style D_CAL fill:#1A3A5C,stroke:#4A90D9,color:#FFFFFF
    style D_VEN fill:#1A3A5C,stroke:#4A90D9,color:#FFFFFF
    style FACT fill:#5C1A1A,stroke:#E05A5A,color:#FFFFFF
```

## Tabela de Relacionamentos

| Tabela Fato | Chave Estrangeira | Tabela Dimensão | Chave Primária | Cardinalidade | Tipo de Relacionamento |
|-------------|-------------------|-----------------|----------------|---------------|------------------------|
| fact_vendas | id_cliente | dim_clientes | id_cliente | N:1 | Muitos-para-Um |
| fact_vendas | id_produto | dim_produtos | id_produto | N:1 | Muitos-para-Um |
| fact_vendas | data_pedido | dim_calendario | data | N:1 | Muitos-para-Um |
| fact_vendas | id_vendedor | dim_vendedores | id_vendedor | N:1 | Muitos-para-Um |

## Regras de Integridade Referencial

| Regra | Descrição | Verificação |
|-------|-----------|-------------|
| PK Única — dim_clientes | Cada id_cliente aparece uma única vez | `COUNT(id_cliente) = COUNT(DISTINCT id_cliente)` |
| PK Única — dim_produtos | Cada id_produto aparece uma única vez | `COUNT(id_produto) = COUNT(DISTINCT id_produto)` |
| PK Única — dim_calendario | Cada data aparece uma única vez | `COUNT(data) = COUNT(DISTINCT data)` |
| PK Única — dim_vendedores | Cada id_vendedor aparece uma única vez | `COUNT(id_vendedor) = COUNT(DISTINCT id_vendedor)` |
| FK NOT NULL — id_cliente | Nenhum pedido sem cliente | `COUNT(*) WHERE id_cliente IS NULL = 0` |
| FK NOT NULL — id_produto | Nenhum pedido sem produto | `COUNT(*) WHERE id_produto IS NULL = 0` |
| FK NOT NULL — data_pedido | Nenhum pedido sem data | `COUNT(*) WHERE data_pedido IS NULL = 0` |
| FK NOT NULL — id_vendedor | Nenhum pedido sem vendedor | `COUNT(*) WHERE id_vendedor IS NULL = 0` |
| FK Válida — id_cliente | Todo id_cliente existe em dim_clientes | LEFT ANTI JOIN = 0 |
| FK Válida — id_produto | Todo id_produto existe em dim_produtos | LEFT ANTI JOIN = 0 |
| FK Válida — data_pedido | Toda data_pedido existe em dim_calendario | LEFT ANTI JOIN = 0 |
| FK Válida — id_vendedor | Todo id_vendedor existe em dim_vendedores | LEFT ANTI JOIN = 0 |

## Distribuição Estimada de Dados

| Dimensão | Registros | Granularidade |
|----------|-----------|---------------|
| dim_clientes | 1.500 | 1 linha por cliente |
| dim_produtos | 250 | 1 linha por produto |
| dim_calendario | 730 | 1 linha por dia (2 anos) |
| dim_vendedores | 15 | 1 linha por vendedor |
| fact_vendas | ~8.000 | 1 linha por item de pedido |
