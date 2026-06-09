# 🏗️ Arquitetura Medalhão — BI E-Commerce

## 1. Fluxo Completo da Arquitetura Medalhão

```mermaid
flowchart LR
    subgraph ORIGEM["🔵 CAMADA DE ORIGEM"]
        direction TB
        GERADOR["00_generate_data.py<br/>Faker + Python"]
    end

    subgraph BRONZE["🟤 CAMADA BRONZE<br/>Dados Brutos | Parquet"]
        direction TB
        B_CLI["bronze_clientes"]
        B_PROD["bronze_produtos"]
        B_PED["bronze_pedidos"]
    end

    subgraph SILVER["⚪ CAMADA SILVER<br/>Dados Curados | Delta Lake"]
        direction TB
        S_CLI["silver_clientes<br/>✔ Tipagem<br/>✔ Deduplicação<br/>✔ Validação"]
        S_PROD["silver_produtos<br/>✔ Tipagem<br/>✔ Deduplicação<br/>✔ Validação"]
        S_PED["silver_pedidos<br/>✔ Tipagem<br/>✔ Join com dimensões<br/>✔ Enriquecimento"]
    end

    subgraph GOLD["🟡 CAMADA GOLD<br/>Modelo Dimensional | Delta Lake"]
        direction TB
        D_CLI["dim_clientes<br/>PK: id_cliente"]
        D_PROD["dim_produtos<br/>PK: id_produto"]
        D_CAL["dim_calendario<br/>PK: data"]
        D_VEN["dim_vendedores<br/>PK: id_vendedor"]
        F_VEN["fact_vendas<br/>FKs → 4 dimensões"]
    end

    subgraph CONSUMO["📊 CAMADA DE CONSUMO"]
        direction TB
        PBI["Power BI<br/>Dashboard Executivo"]
    end

    GERADOR -->|"clientes.parquet<br/>produtos.parquet<br/>pedidos.parquet"| BRONZE
    B_CLI -->|"01_validate_inputs.py"| S_CLI
    B_PROD -->|"01_validate_inputs.py"| S_PROD
    B_PED -->|"01_validate_inputs.py"| S_PED
    S_CLI -->|"30_gold_model.py"| D_CLI
    S_PROD -->|"30_gold_model.py"| D_PROD
    S_CLI -->|"gerar calendário"| D_CAL
    S_PED -->|"extrair vendedores"| D_VEN
    S_CLI --> F_VEN
    S_PROD --> F_VEN
    S_PED --> F_VEN
    D_CLI --> F_VEN
    D_PROD --> F_VEN
    D_CAL --> F_VEN
    D_VEN --> F_VEN
    F_VEN -->|"Importar Parquet/Delta"| PBI
    D_CLI -.->|"Importar Parquet/Delta"| PBI
    D_PROD -.->|"Importar Parquet/Delta"| PBI
    D_CAL -.->|"Importar Parquet/Delta"| PBI
    D_VEN -.->|"Importar Parquet/Delta"| PBI

    style ORIGEM fill:#1A3A5C,stroke:#4A90D9,color:#FFFFFF
    style BRONZE fill:#4A3620,stroke:#B8860B,color:#FFFFFF
    style SILVER fill:#3A3A3A,stroke:#C0C0C0,color:#FFFFFF
    style GOLD fill:#5C4A1A,stroke:#FFD700,color:#FFFFFF
    style CONSUMO fill:#1A4A2A,stroke:#50B86C,color:#FFFFFF
```

## 2. Arquitetura Detalhada (Byte-Level)

```mermaid
flowchart TB
    subgraph FS["💾 SISTEMA DE ARQUIVOS LOCAL"]
        direction LR
        subgraph RAW["data/raw/"]
            CLI_PQT["clientes.parquet"]
            PROD_PQT["produtos.parquet"]
            PED_PQT["pedidos.parquet"]
        end
        subgraph BZ_DELTA["data/bronze/"]
            B_CLI_D["clientes/"]
            B_PROD_D["produtos/"]
            B_PED_D["pedidos/"]
        end
        subgraph SV_DELTA["data/silver/"]
            S_CLI_D["clientes/"]
            S_PROD_D["produtos/"]
            S_PED_D["pedidos/"]
        end
        subgraph GD_DELTA["data/gold/"]
            D_CLI_D["dim_clientes/"]
            D_PROD_D["dim_produtos/"]
            D_CAL_D["dim_calendario/"]
            D_VEN_D["dim_vendedores/"]
            F_VEN_D["fact_vendas/"]
        end
    end

    subgraph PROC["🐍 PROCESSAMENTO PYTHON/PYSPARK"]
        direction TB
        GEN["00_generate_data.py<br/>──<br/>Gera dados sintéticos<br/>via biblioteca Faker<br/>──<br/>Output: Parquet"]
        VAL["01_validate_inputs.py<br/>──<br/>Valida schemas<br/>Conta registros<br/>Verifica integridade<br/>──<br/>Output: Validation Log"]
        BRZ["10_bronze_ingestion.py<br/>──<br/>Lê Parquet → Delta<br/>Schema-on-read<br/>Registro de metadados<br/>──<br/>Output: Delta bronze_*"]
        SLV["20_silver_transform.py<br/>──<br/>Limpeza e tipagem<br/>Deduplicação<br/>Joins de enriquecimento<br/>──<br/>Output: Delta silver_*"]
        GLD["30_gold_model.py<br/>──<br/>SCD Tipo 1 em dims<br/>Construção da fato<br/>Geração de calendário<br/>──<br/>Output: Delta dim_*, fact_*"]
        QLT["40_quality_checks.py<br/>──<br/>Verifica PKs únicas<br/>Verifica FKs não nulas<br/>Contagem cross-camada<br/>──<br/>Output: Quality Report"]
    end

    GEN --> RAW
    RAW --> BRZ
    BRZ --> BZ_DELTA
    BZ_DELTA --> SLV
    SLV --> SV_DELTA
    SV_DELTA --> GLD
    GLD --> GD_DELTA
    GD_DELTA --> QLT

    subgraph PBI_CONN["📊 CONEXÃO POWER BI"]
        direction LR
        IMPORT["Importar diretórios<br/>data/gold/<br/>via Conector Parquet/Delta"]
        MODEL["Modelo Semântico<br/>Relacionamentos Star Schema"]
        DASH["Dashboard<br/>3 Páginas"]
        IMPORT --> MODEL --> DASH
    end

    GD_DELTA --> PBI_CONN

    style FS fill:#1E1E1E,stroke:#666666,color:#FFFFFF
    style PROC fill:#0D3B66,stroke:#4A90D9,color:#FFFFFF
    style PBI_CONN fill:#1B4332,stroke:#50B86C,color:#FFFFFF
    style RAW fill:#2D2D2D,stroke:#888888,color:#FFFFFF
    style BZ_DELTA fill:#3D2E1A,stroke:#B8860B,color:#FFFFFF
    style SV_DELTA fill:#2D2D2D,stroke:#C0C0C0,color:#FFFFFF
    style GD_DELTA fill:#3D3520,stroke:#FFD700,color:#FFFFFF
```

## 3. Diagrama de Sequência — Ordem de Execução do Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor U as 👤 Usuário
    participant GEN as 00_generate_data.py
    participant RAW as data/raw/
    participant VAL as 01_validate_inputs.py
    participant BRZ as 10_bronze_ingestion.py
    participant BZ_D as data/bronze/
    participant SLV as 20_silver_transform.py
    participant SV_D as data/silver/
    participant GLD as 30_gold_model.py
    participant GD_D as data/gold/
    participant QLT as 40_quality_checks.py
    participant PBI as Power BI

    U->>GEN: Executa geração de dados
    GEN->>RAW: Escreve clientes.parquet
    GEN->>RAW: Escreve produtos.parquet
    GEN->>RAW: Escreve pedidos.parquet
    GEN-->>U: ✔ Dados gerados (3 arquivos)

    U->>VAL: Executa validação
    VAL->>RAW: Lê todos os arquivos
    VAL->>VAL: Verifica schemas<br/>Conta registros<br/>Valida ranges
    VAL-->>U: ✔ Validação concluída<br/>Relatório de validação

    U->>BRZ: Executa ingestão Bronze
    BRZ->>RAW: Lê Parquet
    BRZ->>BZ_D: Escreve bronze_clientes (Delta)
    BRZ->>BZ_D: Escreve bronze_produtos (Delta)
    BRZ->>BZ_D: Escreve bronze_pedidos (Delta)
    BRZ-->>U: ✔ Camada Bronze pronta

    U->>SLV: Executa transformação Silver
    SLV->>BZ_D: Lê bronze_clientes
    SLV->>BZ_D: Lê bronze_produtos
    SLV->>BZ_D: Lê bronze_pedidos
    SLV->>SLV: Limpeza, tipagem<br/>Deduplicação
    SLV->>SV_D: Escreve silver_clientes (Delta)
    SLV->>SV_D: Escreve silver_produtos (Delta)
    SLV->>SV_D: Escreve silver_pedidos (Delta)
    SLV-->>U: ✔ Camada Silver pronta

    U->>GLD: Executa modelagem Gold
    GLD->>SV_D: Lê silver_clientes
    GLD->>SV_D: Lê silver_produtos
    GLD->>SV_D: Lê silver_pedidos
    GLD->>GLD: Gera dim_calendario
    GLD->>GLD: Extrai dim_vendedores
    GLD->>GD_D: Escreve dim_clientes (Delta)
    GLD->>GD_D: Escreve dim_produtos (Delta)
    GLD->>GD_D: Escreve dim_calendario (Delta)
    GLD->>GD_D: Escreve dim_vendedores (Delta)
    GLD->>GD_D: Escreve fact_vendas (Delta)
    GLD-->>U: ✔ Camada Gold pronta

    U->>QLT: Executa validação de qualidade
    QLT->>GD_D: Lê todas tabelas Gold
    QLT->>QLT: Verifica PKs únicas<br/>FKs não nulas<br/>Contagem cross-camada
    QLT-->>U: ✔ Relatório de qualidade<br/>0 órfãos | PKs únicas

    U->>PBI: Abre arquivo .pbix
    PBI->>GD_D: Importa dados (Parquet/Delta)
    PBI->>PBI: Configura relacionamentos<br/>Cria medidas DAX<br/>Monta visuais
    PBI-->>U: ✔ Dashboard pronto
```

## 4. Resumo das Transformações por Camada

```mermaid
flowchart TB
    subgraph L1["CAMADA BRONZE — Ingestão"]
        direction LR
        T1A["📥 Leitura de Parquet"]
        T1B["📝 Registro de metadados<br/>(data_ingestao, origem)"]
        T1C["💾 Escrita Delta"]
        T1A --> T1B --> T1C
    end

    subgraph L2["CAMADA SILVER — Transformação"]
        direction LR
        T2A["🧹 Limpeza de strings<br/>(trim, título)"]
        T2B["📐 Correção de tipos<br/>(decimal, data)"]
        T2C["🔄 Deduplicação<br/>(dropDuplicates)"]
        T2D["🔗 Enriquecimento<br/>(joins com dimensões)"]
        T2A --> T2B --> T2C --> T2D
    end

    subgraph L3["CAMADA GOLD — Modelagem"]
        direction LR
        T3A["🗓️ Geração de calendário<br/>(2 anos, 730 dias)"]
        T3B["👤 Extração de vendedores<br/>(15 únicos)"]
        T3C["📊 Construção da fato<br/>(join 4 dimensões)"]
        T3D["🔑 Aplicação de PKs/FKs<br/>(integridade referencial)"]
        T3A --> T3C
        T3B --> T3C
        T3C --> T3D
    end

    L1 --> L2 --> L3

    style L1 fill:#3A2618,stroke:#B8860B,color:#FFFFFF
    style L2 fill:#2D2D2D,stroke:#C0C0C0,color:#FFFFFF
    style L3 fill:#3D3520,stroke:#FFD700,color:#FFFFFF
```
