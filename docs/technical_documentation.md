# Documentação Técnica — BI E-Commerce (Medallion Architecture)

## 1. Visão Geral do Projeto

O projeto **BI E-Commerce** consiste na implementação de uma solução completa de Business Intelligence para uma empresa fictícia de comércio eletrônico especializada na venda de produtos eletrônicos. A empresa atua em todo o território nacional brasileiro, abrangendo 10 estados (SP, RJ, MG, RS, PR, BA, PE, CE, AM, DF) distribuídos pelas cinco regiões geográficas, com uma força de vendas composta por 15 vendedores.

O catálogo da empresa compreende 250 produtos organizados em 8 categorias: Smartphones, Notebooks, Acessórios, Áudio, Tablets, Monitores, Periféricos e Armazenamento. A base de clientes é de 1.500 consumidores, e o histórico transacional contempla 8.000 pedidos realizados ao longo de um período de aproximadamente dois anos.

A solução foi desenvolvida utilizando a arquitetura Medallion (Bronze → Silver → Gold), padrão amplamente adotado na indústria para organização de _data lakes_ e _lakehouses_. O pipeline de dados foi implementado integralmente em Python com PySpark e Delta Lake, executando localmente em ambiente Windows. O consumo final dos dados é feito via Power BI Desktop, com um dashboard interativo de três páginas.

Embora o projeto utilize dados sintéticos gerados programaticamente, a arquitetura, as transformações, as verificações de qualidade e o modelo dimensional seguem rigorosamente padrões profissionais de engenharia de dados e inteligência de negócios.

---

## 2. Objetivos

### 2.1 Objetivos Técnicos

1. **Implementar arquitetura Medallion completa** com as três camadas (Bronze, Silver, Gold) utilizando PySpark e Delta Lake.
2. **Construir pipeline ETL/ELT reprodutível**, com scripts modulares para cada etapa do processo.
3. **Aplicar transformações de qualidade de dados** incluindo limpeza, padronização, deduplicação, validação e enriquecimento.
4. **Modelar Star Schema otimizado para análises multidimensionais** com 4 dimensões e 1 fato.
5. **Garantir integridade referencial** entre fato e dimensões via verificações automatizadas.
6. **Gerar dados sintéticos realistas** que simulem um ambiente de e-commerce brasileiro com todas as variabilidades esperadas.
7. **Disponibilizar os dados para ferramenta de visualização** (Power BI) em formato Delta/Parquet.

### 2.2 Objetivos de Negócio

1. **Fornecer visão consolidada de faturamento** por período, região, categoria e vendedor.
2. **Possibilitar análise de desempenho de vendedores** com ranking, ticket médio e participação percentual.
3. **Viabilizar análise geográfica das vendas** por estado, região e município.
4. **Permitir identificação de categorias e produtos mais rentáveis** com base em volume de vendas e margem.
5. **Instrumentar a tomada de decisão** em nível executivo, gerencial e operacional.

---

## 3. Arquitetura da Solução

### 3.1 Arquitetura Medallion

O projeto adota a arquitetura Medallion (_Bronze → Silver → Gold_), um padrão de organização de dados em camadas progressivas de qualidade e estruturação, originalmente proposto pela Databricks para _lakehouses_. Cada camada possui um propósito bem definido:

- **Camada Bronze (Ingestão Bruta):** Armazena os dados exatamente como foram recebidos das fontes. Nesta camada, não há transformações — os dados brutos são persistidos em formato Delta Lake com particionamento por região. A Bronze atua como _single source of truth_ imutável, permitindo reprocessamento futuro a qualquer momento. O schema é mantido fiel ao formato de origem (CSV sintético).

- **Camada Silver (Dados Limpos e Validados):** Aplica transformações de qualidade: remoção de duplicatas, padronização de strings (Title Case para nomes e cidades, UPPER para siglas de estado), validação de domínios (preços > 0, estoque >= 0, datas válidas), enriquecimento com dados calculados (total do pedido via JOIN com tabela de produtos, margem dos produtos). Nesta camada os dados tornam-se confiáveis e prontos para consumo analítico, ainda preservando granularidade transacional.

- **Camada Gold (Modelo Dimensional):** Implementa o Star Schema com dimensões desnormalizadas e tabela fato otimizada para consultas. As chaves naturais são mapeadas para chaves substitutas (surrogate keys), a dimensão calendário é gerada programaticamente, e a dimensão de vendedores é criada com dados mestres artificiais. Esta camada é o ponto de consumo para ferramentas de BI.

### 3.2 Diagrama Conceitual do Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────────┐
│  00_generate  │────▶│  01_validate  │────▶│  10_bronze    │────▶│  20_silver     │
│  _data.py     │     │  _inputs.py   │     │  _ingestion.py│     │  _transform.py │
│  (CSV sint.)  │     │  (validação)  │     │  (Delta raw)  │     │  (Delta clean) │
└──────────────┘     └──────────────┘     └──────────────┘     └───────┬───────┘
                                                                       │
                                                                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Power BI     │◀────│  40_quality    │◀────│  30_gold       │
│  Dashboard    │     │  _checks.py    │     │  _model.py     │
│  (pbix)       │     │  (auditoria)   │     │  (Star Schema) │
└───────────────┘     └───────────────┘     └───────────────┘
```

### 3.3 Fluxo de Dados Detalhado

1. **Geração de dados:** Script `00_generate_data.py` gera 3 arquivos CSV sintéticos com a biblioteca `faker` e dados controlados (produtos e vendedores fixos).
2. **Validação inicial:** Script `01_validate_inputs.py` verifica integridade dos CSVs (contagem de linhas, colunas esperadas, tipos, FK válidas).
3. **Ingestão Bronze:** Spark lê CSVs e grava como tabelas Delta em `data/bronze/` com particionamento por `regiao`.
4. **Transformação Silver:** Spark lê tabelas Bronze, aplica limpezas e enriquecimentos, grava Delta em `data/silver/`.
5. **Modelagem Gold:** Spark lê tabelas Silver, aplica mapeamento para chaves substitutas, gera dimensão calendário e vendedores, persiste Star Schema em `data/gold/`.
6. **Verificações de qualidade:** Spark executa bateria de asserts (integridade referencial, contagem, nulos, domínios) sobre a camada Gold.
7. **Consumo Power BI:** Power BI Desktop conecta-se aos arquivos Delta/Parquet em `data/gold/` para alimentar o dashboard.

---

## 4. Tecnologias Utilizadas

### 4.1 PySpark 3.x (Apache Spark)

O Apache Spark é o _engine_ de processamento distribuído escolhido por sua capacidade de lidar com grandes volumes de dados e por sua API rica para transformações complexas. Utilizamos a interface Python (PySpark) que combina a performance do motor Spark com a produtividade da linguagem Python. A versão utilizada é a 3.x, executando em modo _local_ (single-node) para simplificar o ambiente de desenvolvimento.

**Principais módulos utilizados:**
- `pyspark.sql.SparkSession`: ponto de entrada para todas as operações
- `pyspark.sql.functions`: coleção de funções built-in (`col`, `upper`, `initcap`, `sum`, `countDistinct`, `when`, `round`, `lit`, `sequence`, `explode`)
- `pyspark.sql.types`: definição explícita de schemas (`StructType`, `StructField`, `IntegerType`, `StringType`, `DateType`, `DecimalType`)
- `pyspark.sql.Window`: funções de janela para rankings e agregações analíticas

### 4.2 Delta Lake 3.x

Delta Lake é a camada de armazenamento que adiciona confiabilidade e performance ao Spark. Sobre arquivos Parquet, o Delta Lake oferece:

- **Transações ACID:** Garantia de atomicidade nas operações de escrita.
- **Versionamento (Time Travel):** Capacidade de consultar versões anteriores dos dados.
- **Schema enforcement:** Validação automática de schema na escrita.
- **Schema evolution:** Evolução controlada do schema.
- **Compaction e otimização:** Comando `OPTIMIZE` para compactação de pequenos arquivos.
- **Z-ordering:** Otimização de layout para consultas filtradas.

Utilizamos o formato Delta para todas as tabelas das três camadas, garantindo confiabilidade e reprodutibilidade.

### 4.3 Python 3.10+

Linguagem de script principal, utilizada para todos os módulos do pipeline. Python foi escolhido por sua expressividade, vasto ecossistema de bibliotecas e por ser a interface nativa do PySpark.

**Bibliotecas auxiliares:**
- `faker`: geração de dados sintéticos realistas (nomes brasileiros, cidades, telefones)
- `pandas`: (opcional) para inspeção rápida de resultados durante desenvolvimento
- `delta-spark`: conector Delta Lake para PySpark (versão compatível com Spark 3.x)

### 4.4 Power BI Desktop

Ferramenta de visualização e análise de dados da Microsoft, escolhida por:
- Conector nativo a arquivos Parquet/Delta (via pasta).
- Modelagem semântica rica com DAX (Data Analysis Expressions).
- Criação de dashboards interativos com drill-down e cross-filtering.
- Integração com o formato de saída do pipeline (Delta Lake).
- Ampla adoção no mercado corporativo brasileiro.

### 4.5 Justificativa das Escolhas Tecnológicas

| Tecnologia | Alternativa Considerada | Motivo da Escolha |
|------------|------------------------|-------------------|
| PySpark + Delta | Pandas puro | Escalabilidade, particionamento, transações ACID, simulação profissional de ambiente Big Data |
| Delta Lake | Parquet puro | Versionamento, schema enforcement, time travel |
| Python | Scala / Java | Curva de aprendizado, produtividade, ecossistema (faker, pandas) |
| Power BI | Tableau / Looker | Conector Parquet nativo, DAX, custo-benefício, mercado brasileiro |
| CSV sintético | Base real | Reprodutibilidade, ausência de dados sensíveis, controle total sobre distribuições |
| Execução local | Cluster Spark | Simplicidade para desenvolvimento acadêmico; arquitetura idêntica à de cluster |

---

## 5. Estrutura do Projeto

```
bi_ecommerce/
│
├── data/                          # Dados gerados e processados
│   ├── source/                    # CSVs sintéticos originais
│   │   ├── clientes.csv
│   │   ├── produtos.csv
│   │   └── pedidos.csv
│   ├── bronze/                    # Camada Bronze (Delta)
│   │   ├── bronze_clientes/
│   │   ├── bronze_produtos/
│   │   └── bronze_pedidos/
│   ├── silver/                    # Camada Silver (Delta)
│   │   ├── silver_clientes/
│   │   ├── silver_produtos/
│   │   └── silver_pedidos/
│   └── gold/                      # Camada Gold — Star Schema (Delta)
│       ├── dim_clientes/
│       ├── dim_produtos/
│       ├── dim_calendario/
│       ├── dim_vendedores/
│       └── fact_vendas/
│
├── src/                           # Código-fonte do pipeline
│   ├── 00_generate_data.py        # Geração de dados sintéticos
│   ├── 01_validate_inputs.py      # Validação de CSVs de entrada
│   ├── 10_bronze_ingestion.py     # Ingestão camada Bronze
│   ├── 20_silver_transform.py     # Transformação camada Silver
│   ├── 30_gold_model.py           # Modelagem Star Schema (Gold)
│   ├── 40_quality_checks.py       # Verificações de qualidade
│   ├── run_pipeline.py            # Orquestrador (master script)
│   └── spark_config.py            # Configuração centralizada do Spark
│
├── notebooks/                     # Jupyter Notebooks exploratórios
│   ├── 00_exploracao_dados.ipynb
│   ├── 01_validacao_quality.ipynb
│   └── 02_insights_preliminares.ipynb
│
├── powerbi/                       # Recursos Power BI
│   ├── bi_ecommerce.pbix          # Arquivo do dashboard
│   ├── dax_measures.txt           # Medidas DAX
│   └── dashboard_spec.txt         # Especificação dos visuais
│
├── docs/                          # Documentação do projeto
│   ├── data_dictionary.md
│   ├── technical_documentation.md
│   ├── functional_documentation.md
│   ├── presentation_script.md
│   ├── implementation_guide.md
│   ├── test_plan.md
│   └── HANDOFF.md
│
├── tests/                         # Testes automatizados
│   └── test_pipeline.py
│
├── requirements.txt               # Dependências Python
├── README.md                      # Visão geral do projeto
└── .gitignore                     # Arquivos ignorados pelo Git
```

### 5.1 Descrição dos Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `00_generate_data.py` | Gera dados sintéticos usando `faker` para clientes e pedidos, e dados hard-coded para produtos e vendedores. Salva em `data/source/` como CSV. |
| `01_validate_inputs.py` | Lê CSVs de origem e aplica validações: contagem de registros, colunas esperadas, tipos de dados, unicidade de chaves primárias, integridade de FKs. |
| `10_bronze_ingestion.py` | Lê CSVs validados com Spark, define schemas explícitos e grava como tabelas Delta em `data/bronze/` com particionamento. |
| `20_silver_transform.py` | Lê camada Bronze, aplica limpezas, validações, JOINs de enriquecimento, e grava Delta em `data/silver/`. |
| `30_gold_model.py` | Constrói dimensões (cliente, produto, calendário, vendedor) e fato (vendas), aplica mapeamento de chaves, grava Delta em `data/gold/`. |
| `40_quality_checks.py` | Executa verificações automatizadas: integridade referencial, contagens, métricas calculadas, nulos, domínios. |
| `run_pipeline.py` | Script orquestrador que executa todos os scripts na sequência correta. |
| `spark_config.py` | Módulo com a função `create_spark_session()` que centraliza a configuração do SparkSession com parâmetros do Delta Lake. |
| `dax_measures.txt` | Arquivo contendo todas as medidas DAX a serem importadas no Power BI. |
| `dashboard_spec.txt` | Especificação detalhada dos visuais do dashboard (posição, tipo, campos, formatação). |
| `test_pipeline.py` | Testes unitários para funções críticas do pipeline. |
| `requirements.txt` | Lista de dependências: `pyspark`, `delta-spark`, `faker`, `pandas`. |

---

## 6. Modelagem de Dados

### 6.1 Modelo de Origem (Normalizado)

O modelo de origem possui três entidades independentes:

- **clientes:** Entidade mestre com dados cadastrais. Chave: `cliente_id`.
- **produtos:** Entidade mestre com catálogo de produtos. Chave: `sku`.
- **pedidos:** Entidade transacional que referencia clientes e produtos. Chaves estrangeiras: `cliente_id` (→ clientes), `sku` (→ produtos) e `id_vendedor` (→ vendedores).

Não há tabela explícita de vendedores na origem — os IDs de 1 a 15 são referenciados diretamente nos pedidos.

### 6.2 Transformações na Silver

1. **Limpeza de clientes:** `nome`, `cidade` e `regiao` são convertidos para Title Case com a função `initcap()`. O campo `estado` é convertido para UPPER com `upper()`. Email é normalizado para minúsculas. Duplicatas de `cliente_id` são removidas.
2. **Limpeza de produtos:** SKU é deduplicado. Preços negativos ou zero são filtrados (registros removidos). Colunas de margem (`margem`, `margem_pct`) são calculadas.
3. **Enriquecimento de pedidos:** JOIN com `silver_produtos` via `sku` para obter `preco_venda`. Cálculo de `total_pedido = (quantidade × preco_venda) + valor_frete`. Limpeza de strings similar à de clientes.

### 6.3 Modelo Star Schema (Gold)

O modelo dimensional adota o esquema estrela clássico:

```
                    dim_clientes (1) ──── (N) fact_vendas (N) ──── (1) dim_produtos
                         │                       │
                    dim_calendario (1) ──── (N) ───┘
                         │
                    dim_vendedores (1) ──── (N) ───┘
```

**Características do Star Schema:**
- **Dimensões desnormalizadas:** Cada dimensão contém todos os atributos descritivos necessários, sem snowflaking.
- **Surrogate keys:** Chaves inteiras sequenciais nas dimensões (exceto `dim_calendario`, onde a própria `data` é a chave natural).
- **Tabela fato esparsa:** Contém apenas chaves estrangeiras e medidas numéricas.
- **Chave degenerada:** `pedido_id` é mantido na fato como degenerate dimension para contagem distinta de pedidos.
- **Granularidade da fato:** 1 linha por pedido (cada pedido contém exatamente 1 produto nesta versão simplificada).

---

## 7. Pipeline de Dados

### 7.1 Ordem de Execução e Dependências

```
00_generate_data.py
        │
        ▼
01_validate_inputs.py  ────── (depende de: CSVs em data/source/)
        │
        ▼
10_bronze_ingestion.py ────── (depende de: CSVs validados)
        │
        ▼
20_silver_transform.py ────── (depende de: Delta tables em data/bronze/)
        │
        ▼
30_gold_model.py      ────── (depende de: Delta tables em data/silver/)
        │
        ▼
40_quality_checks.py  ────── (depende de: Delta tables em data/gold/)
```

### 7.2 Script Orquestrador (`run_pipeline.py`)

O script `run_pipeline.py` executa todos os scripts na sequência correta utilizando `subprocess.run()`, com verificação de código de retorno a cada etapa. Caso uma etapa falhe (exit code != 0), o pipeline é interrompido e o erro é reportado. Parâmetros de configuração (como diretórios de dados e opções de Spark) são centralizados em `spark_config.py`.

### 7.3 Descrição de Cada Script

#### `00_generate_data.py`
- **Entrada:** Nenhuma (dados gerados programaticamente).
- **Processamento:** Utiliza a biblioteca `faker` com locale `pt_BR` para gerar nomes, e-mails, telefones e cidades brasileiras. Produtos são definidos em dicionário fixo (250 itens com SKU, nome, categoria, subcategoria, preços e estoque). Pedidos são gerados com distribuição aleatória controlada: cliente aleatório, produto aleatório, quantidade entre 1 e 5, data entre 2024-01-01 e 2025-12-01, frete proporcional. Vendedor é atribuído aleatoriamente (1-15). Região e estado do pedido são preenchidos a partir de uma distribuição baseada nos 10 estados cobertos.
- **Saída:** `data/source/clientes.csv` (1500 linhas), `data/source/produtos.csv` (250 linhas), `data/source/pedidos.csv` (8000 linhas).

#### `01_validate_inputs.py`
- **Entrada:** CSVs em `data/source/`.
- **Processamento:** Leitura com pandas. Verificações: (a) clientes: 1500 linhas, 8 colunas, `cliente_id` único; (b) produtos: 250 linhas, 7 colunas, `sku` único, `preco_venda > 0`; (c) pedidos: 8000 linhas, 10 colunas, `pedido_id` único, `cliente_id` existente em clientes, `sku` existente em produtos, `quantidade > 0`.
- **Saída:** Log de validações aprovadas/reprovadas no console.

#### `10_bronze_ingestion.py`
- **Entrada:** CSVs validados.
- **Processamento:** Cria SparkSession. Lê cada CSV com schema explícito (`StructType`). Grava como Delta com `mode("overwrite")` e particionamento `partitionBy("regiao")` para clientes e pedidos.
- **Saída:** Tabelas Delta em `data/bronze/`.

#### `20_silver_transform.py`
- **Entrada:** Tabelas Delta em `data/bronze/`.
- **Processamento:** Lê cada tabela Bronze com `spark.read.format("delta").load()`. Aplica transformações conforme seção 6.2. Grava como Delta em `data/silver/`.
- **Saída:** Tabelas Delta em `data/silver/`.

#### `30_gold_model.py`
- **Entrada:** Tabelas Delta em `data/silver/`.
- **Processamento:**
  1. `dim_clientes`: seleciona `cliente_id AS id_cliente`, `nome`, `cidade`, `estado`, `regiao` de `silver_clientes`.
  2. `dim_produtos`: extrai número do SKU (`regexp_extract(sku, r'\d+')`) como `id_produto`, seleciona `nome_produto`, `categoria`, `preco_venda` de `silver_produtos`.
  3. `dim_calendario`: gera sequência de datas entre `min(data_pedido)` e `max(data_pedido)`, extrai `dia`, `mes`, `nome_mes`, `mes_num`, `trimestre`, `ano`.
  4. `dim_vendedores`: cria DataFrame a partir de lista hard-coded com 15 vendedores.
  5. `fact_vendas`: faz JOIN de `silver_pedidos` com as dimensões para mapear chaves naturais para surrogate keys, seleciona colunas da fato.
- **Saída:** 5 tabelas Delta em `data/gold/`.

#### `40_quality_checks.py`
- **Entrada:** Tabelas Delta em `data/gold/`.
- **Processamento:** Executa bateria de asserts usando PySpark. Cada verificação falha com `raise Exception` se a condição não for satisfeita.
- **Saída:** Relatório de checks no console. Exit code 0 se todos aprovados.

---

## 8. Configuração do Spark

### 8.1 SparkSession

```python
from pyspark.sql import SparkSession

def create_spark_session(app_name="BI_Ecommerce"):
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.databricks.delta.retentionDurationCheck.enabled", "false")
        .getOrCreate()
    )
```

### 8.2 Parâmetros Explicados

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| `master` | `local[*]` | Execução local utilizando todos os núcleos disponíveis da CPU |
| `spark.sql.extensions` | `DeltaSparkSessionExtension` | Habilita comandos SQL do Delta Lake (`VACUUM`, `OPTIMIZE`, `DESCRIBE HISTORY`) |
| `spark.sql.catalog.spark_catalog` | `DeltaCatalog` | Configura o catálogo padrão para usar Delta Lake como formato nativo |
| `spark.sql.adaptive.enabled` | `true` | Habilita Adaptive Query Execution (AQE) para otimização dinâmica de plano de execução |
| `spark.sql.adaptive.coalescePartitions.enabled` | `true` | Permite coalescência automática de partições pós-shuffle |
| `spark.sql.sources.partitionOverwriteMode` | `dynamic` | Sobrescreve apenas partições afetadas em escritas com `mode("overwrite")` |
| `spark.databricks.delta.retentionDurationCheck.enabled` | `false` | Desabilita verificação de retenção para permitir `VACUUM` com qualquer intervalo (ambiente de desenvolvimento) |

---

## 9. Transformações por Camada

### 9.1 Camada Bronze — Ingestão

**Objetivo:** Ingerir dados brutos sem transformações, preservando fidelidade.

Operações:
1. Leitura de CSV com schema explícito (`StructType`) para garantir tipos corretos desde a ingestão.
2. Escrita em formato Delta com `mode("overwrite")`.
3. Particionamento por `regiao` para clientes e pedidos.

**Exemplo de schema explícito:**
```python
schema_clientes = StructType([
    StructField("cliente_id", IntegerType(), False),
    StructField("nome", StringType(), False),
    StructField("email", StringType(), False),
    StructField("telefone", StringType(), False),
    StructField("cidade", StringType(), False),
    StructField("estado", StringType(), False),
    StructField("regiao", StringType(), False),
    StructField("data_cadastro", DateType(), False),
])
```

### 9.2 Camada Silver — Limpeza e Enriquecimento

**Objetivo:** Produzir dados limpos, consistentes e enriquecidos.

Operações por tabela:

**silver_clientes:**
- `F.initcap(F.col("nome"))` — padronização de nome
- `F.initcap(F.col("cidade"))` — padronização de cidade
- `F.upper(F.col("estado"))` — padronização de estado
- `F.lower(F.col("email"))` — normalização de e-mail
- `.dropDuplicates(["cliente_id"])` — remoção de duplicatas
- Verificação: `cliente_id IS NOT NULL`

**silver_produtos:**
- `F.initcap(F.col("categoria"))`, `F.initcap(F.col("subcategoria"))` — padronização
- Filtro: `F.col("preco_venda") > 0` e `F.col("preco_custo") > 0`
- Enriquecimento: `margem = preco_venda - preco_custo`
- Enriquecimento: `margem_pct = round((preco_venda - preco_custo) / preco_venda * 100, 2)`
- `.dropDuplicates(["sku"])` — garantia de unicidade

**silver_pedidos:**
- JOIN: `bronze_pedidos.join(silver_produtos, "sku", "left")` para obter `preco_venda`
- Enriquecimento: `total_pedido = (quantidade * preco_venda) + valor_frete`
- Limpeza: Title Case em `municipio` e `regiao`, UPPER em `estado`
- Filtro: remoção de pedidos onde JOIN falhou (produto inexistente)
- Verificação: `quantidade > 0`, `total_pedido > 0`

### 9.3 Camada Gold — Modelagem Dimensional

**Objetivo:** Criar Star Schema otimizado para consultas analíticas.

**dim_clientes:**
```python
dim_clientes = silver_clientes.select(
    F.col("cliente_id").alias("id_cliente"),
    F.col("nome"),
    F.col("cidade"),
    F.col("estado"),
    F.col("regiao")
)
```

**dim_produtos:**
```python
dim_produtos = silver_produtos.select(
    F.regexp_extract(F.col("sku"), r"(\d+)", 1).cast("int").alias("id_produto"),
    F.col("nome_produto"),
    F.col("categoria"),
    F.col("preco_venda")
)
```

**dim_calendario:**
```python
min_date, max_date = silver_pedidos.agg(
    F.min("data_pedido"), F.max("data_pedido")
).first()

dim_calendario = spark.sql(f"""
    SELECT explode(sequence(to_date('{min_date}'), to_date('{max_date}'), interval 1 day)) AS data
""").select(
    F.col("data"),
    F.dayofmonth("data").alias("dia"),
    F.date_format("data", "MMMM").alias("mes"),
    F.date_format("data", "MMM").alias("nome_mes"),
    F.month("data").alias("mes_num"),
    F.quarter("data").alias("trimestre"),
    F.year("data").alias("ano")
)
```

**dim_vendedores:**
```python
vendedores_data = [
    (1, "Carlos Mendes", "Sudeste"),
    (2, "Ana Beatriz", "Sudeste"),
    # ... (15 vendedores)
]
dim_vendedores = spark.createDataFrame(vendedores_data, ["id_vendedor", "nome", "regiao"])
```

**fact_vendas:**
```python
fact_vendas = silver_pedidos.alias("p") \
    .join(dim_clientes.alias("c"), F.col("p.cliente_id") == F.col("c.id_cliente"), "inner") \
    .join(dim_produtos.alias("pr"), F.col("p.sku") == F.concat(F.lit("SKU-"), F.lpad(F.col("pr.id_produto"), 3, "0")), "inner") \
    .select(
        F.col("p.pedido_id"),
        F.col("c.id_cliente"),
        F.col("pr.id_produto"),
        F.col("p.data_pedido"),
        F.col("p.id_vendedor"),
        F.col("p.quantidade"),
        F.col("p.valor_frete"),
        F.col("p.total_pedido"),
        F.col("p.municipio"),
        F.col("p.estado"),
        F.col("p.regiao")
    )
```

---

## 10. Verificações de Qualidade

O script `40_quality_checks.py` implementa uma bateria abrangente de verificações automatizadas. A filosofia adotada é _fail fast_: qualquer verificação que falhe interrompe a execução com uma mensagem descritiva do problema encontrado.

### 10.1 Categorias de Verificação

| Categoria | Descrição | Exemplos |
|-----------|-----------|----------|
| Contagem de registros | Garante que nenhuma transformação perdeu ou duplicou registros indevidamente | `dim_clientes.count() <= 1500` |
| Unicidade de chaves | Garante que chaves primárias são únicas | `COUNT(id_cliente) = COUNT(DISTINCT id_cliente)` |
| Integridade referencial | Garante que toda FK na fato tem correspondente na dimensão | LEFT ANTI JOIN fact × dim = 0 |
| Domínios válidos | Garante que valores estão dentro de intervalos esperados | `preco_venda > 0`, `estado IN (SP, RJ, ...)` |
| Não nulidade | Garante que colunas obrigatórias não têm nulos | `cliente_id IS NOT NULL` |
| Métricas calculadas | Verifica consistência de valores calculados | `total_pedido = (quantidade × preco_venda) + valor_frete` |
| Datas válidas | Garante que datas estão no intervalo esperado | `data_pedido >= '2024-01-01'` |

### 10.2 Lista de Checks Implementados

1. `check_row_count(table, expected_min, expected_max)` — contagem dentro do range
2. `check_unique(table, column)` — unicidade de coluna
3. `check_referential_integrity(fact, fact_col, dim, dim_col)` — sem órfãos
4. `check_not_null(table, column)` — ausência de nulos
5. `check_positive(table, column)` — valores positivos
6. `check_domain(table, column, valid_values)` — valores em lista permitida
7. `check_date_range(table, column, min_date, max_date)` — datas no range
8. `check_kpi_faturamento(fact_table)` — SUM(total_pedido) > 0
9. `check_kpi_pedidos(fact_table)` — COUNT(DISTINCT pedido_id) > 0
10. `check_kpi_vendedores(dim_vendedores)` — total = 15

---

## 11. Modelo Semântico (Power BI)

### 11.1 Relacionamentos

| Tabela (From) | Coluna | Tabela (To) | Coluna | Cardinalidade | Cross-filter |
|---------------|--------|-------------|--------|---------------|-------------|
| dim_clientes | id_cliente | fact_vendas | id_cliente | 1:N | Single |
| dim_produtos | id_produto | fact_vendas | id_produto | 1:N | Single |
| dim_calendario | data | fact_vendas | data_pedido | 1:N | Single |
| dim_vendedores | id_vendedor | fact_vendas | id_vendedor | 1:N | Single |

Todos os relacionamentos são configurados como _single-direction cross-filter_ partindo das dimensões para a fato.

### 11.2 Medidas DAX

Principais medidas definidas no arquivo `powerbi/dax_measures.txt`:

```dax
Faturamento = SUM(fact_vendas[total_pedido])

Total Pedidos = DISTINCTCOUNT(fact_vendas[pedido_id])

Ticket Médio = DIVIDE([Faturamento], [Total Pedidos], 0)

Total Vendedores = DISTINCTCOUNT(fact_vendas[id_vendedor])

Volume de Itens = SUM(fact_vendas[quantidade])

Faturamento Ano Anterior = CALCULATE([Faturamento], SAMEPERIODLASTYEAR(dim_calendario[data]))

Crescimento % = DIVIDE([Faturamento] - [Faturamento Ano Anterior], [Faturamento Ano Anterior], 0)
```

---

## 12. Requisitos de Ambiente

### 12.1 Hardware Recomendado

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 4 núcleos | 8+ núcleos |
| RAM | 8 GB | 16 GB |
| Disco | 2 GB livres | 10 GB SSD |
| SO | Windows 10/11 64-bit | Windows 11 64-bit |

### 12.2 Software Necessário

| Software | Versão | Observação |
|----------|--------|------------|
| Java JDK | 8 ou 11 | Obrigatório para PySpark. `JAVA_HOME` configurado. |
| Python | 3.10 ou superior | Recomendado 3.11. |
| Power BI Desktop | Mais recente (2.x) | Para visualização. |
| Git | Qualquer | Opcional, para versionamento. |

### 12.3 Pacotes Python (`requirements.txt`)

```
pyspark>=3.4.0,<4.0.0
delta-spark>=3.0.0
faker>=22.0.0
pandas>=2.0.0
```

### 12.4 Variáveis de Ambiente

| Variável | Valor (exemplo) |
|----------|-----------------|
| `JAVA_HOME` | `C:\Program Files\Java\jdk-11` |
| `HADOOP_HOME` | (opcional; PySpark local não exige para I/O básico) |
| `PYTHONPATH` | (definido automaticamente pelo venv) |

---

## 13. Limitações e Premissas

### 13.1 Premissas do Projeto

1. **Dados sintéticos:** Todos os dados são gerados artificialmente. Distribuições, correlações e sazonalidades são simplificadas e controladas programaticamente. Não refletem comportamento real de consumidores.
2. **Granularidade simplificada:** Cada pedido contém exatamente 1 produto. Não há suporte a múltiplos itens por pedido nesta versão.
3. **Vendedores fixos:** Os 15 vendedores são estáticos e não variam ao longo do tempo.
4. **Sem SCD Tipo 2:** Dimensões utilizam SCD Tipo 1 — alterações em atributos sobrescrevem valores anteriores. Não há versionamento histórico de mudanças dimensionais.
5. **Execução local:** O pipeline executa em single-node (modo `local[*]`). Particionamento por região existe, mas não há distribuição real entre nós.
6. **Janela temporal fixa:** Dados cobrem aproximadamente janeiro de 2024 a dezembro de 2025, definidos na geração.
7. **Frete simplificado:** O valor do frete é gerado aleatoriamente sem correlação real com distância geográfica, peso ou dimensões do produto.

### 13.2 Limitações Conhecidas

1. **Ausência de dados reais:** Métricas e insights são ilustrativos, não representam performance real de mercado.
2. **Sem pipeline incremental:** A cada execução, todas as tabelas são sobrescritas (`mode("overwrite")`). Não há suporte a _upsert_ ou captura de mudanças incrementais (CDC).
3. **Sem catálogo de metadados:** Não há integração com Hive Metastore, AWS Glue ou Unity Catalog. Metadados residem apenas nos diretórios Delta.
4. **Monitoramento ausente:** Não há integração com ferramentas de observabilidade (Grafana, Datadog, Spark UI persistente).
5. **Performance limitada:** Com 8.000 pedidos, o volume é pequeno. Em escala de milhões, otimizações adicionais seriam necessárias (Z-ordering, particionamento por data, compactação).
6. **Segurança:** Não há criptografia, mascaramento de dados sensíveis ou controle de acesso (RBAC). Dados de clientes (nome, e-mail, telefone) estão em texto plano.

### 13.3 Extensões Futuras Possíveis

1. Incrementar volume para milhões de registros e testar performance.
2. Implementar SCD Tipo 2 para dimensões que mudam ao longo do tempo.
3. Adicionar tabela fato de múltiplos itens por pedido (fact_vendas com granularidade item).
4. Pipeline incremental com _change data capture_ via Delta Lake `MERGE`.
5. Integração com Hive Metastore para catálogo centralizado.
6. Implementar _data masking_ para colunas sensíveis (LGPD).
7. Orquestração com Apache Airflow ou Dagster.
8. Deploy em cluster Spark (Databricks, EMR, HDInsight).
9. Testes de regressão automatizados com pytest e Delta Lake _time travel_.
10. Dashboard em tempo real com Spark Structured Streaming.

---

## 14. Referências

1. **Databricks — Medallion Architecture.** Disponível em: https://www.databricks.com/glossary/medallion-architecture
2. **Delta Lake Documentation.** Disponível em: https://docs.delta.io/latest/index.html
3. **Apache Spark Documentation.** Disponível em: https://spark.apache.org/docs/latest/
4. **PySpark API Reference.** Disponível em: https://spark.apache.org/docs/latest/api/python/
5. **Microsoft Power BI — Guia de Modelagem.** Disponível em: https://learn.microsoft.com/pt-br/power-bi/guidance/
6. **Kimball, Ralph; Ross, Margy.** _The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling._ 3ª ed. Wiley, 2013.
7. **Reis, Joe; Housley, Matt.** _Fundamentals of Data Engineering._ O'Reilly Media, 2022.
8. **Faker Documentation.** Disponível em: https://faker.readthedocs.io/
9. **Python venv Documentation.** Disponível em: https://docs.python.org/3/library/venv.html

---

*Documento gerado para o projeto BI E-Commerce — versão 1.0. Junho de 2026.*
