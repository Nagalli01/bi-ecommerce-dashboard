# Dicionário de Dados — BI E-Commerce (Medallion Architecture)

Projeto acadêmico de Business Intelligence para empresa fictícia de comércio eletrônico de eletrônicos. Este documento descreve detalhadamente todas as tabelas e colunas das camadas Bronze, Silver e Gold (Star Schema), incluindo tipos de dados, descrições de negócio, exemplos ilustrativos e restrições aplicadas.

---

## Camada Bronze

A camada Bronze armazena os dados brutos exatamente como foram gerados, sem nenhuma transformação. Atua como _data lake_ de ingestão, preservando a fidelidade dos dados originais. Tabelas no formato Delta Lake, particionadas por `regiao` (clientes e pedidos) ou sem particionamento (produtos).

### bronze_clientes

Origem: `source/clientes.csv` (1500 registros sintéticos). Contém dados cadastrais dos clientes.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| cliente_id | INT | Identificador único do cliente, sequencial | `1`, `523`, `1500` | PK, NOT NULL |
| nome | STRING | Nome completo do cliente | `"Ana Silva"`, `"João Souza"` | NOT NULL |
| email | STRING | Endereço de e-mail do cliente | `"ana.silva@email.com"` | NOT NULL, formato email |
| telefone | STRING | Número de telefone com DDD, formato (XX) XXXXX-XXXX | `"(11) 98765-4321"` | NOT NULL |
| cidade | STRING | Município de residência | `"São Paulo"`, `"Campinas"` | NOT NULL |
| estado | STRING | Sigla da unidade federativa | `"SP"`, `"RJ"`, `"MG"` | NOT NULL, 2 caracteres |
| regiao | STRING | Região geográfica do Brasil | `"Sudeste"`, `"Nordeste"` | NOT NULL |
| data_cadastro | DATE | Data em que o cliente se cadastrou na plataforma | `"2024-03-15"` | NOT NULL |

**Particionamento:** `regiao` (5 partições: Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

**Total de registros:** 1.500

---

### bronze_produtos

Origem: `source/produtos.csv` (250 registros sintéticos). Catálogo de produtos eletrônicos.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| sku | STRING | Código SKU (Stock Keeping Unit) do produto | `"SKU-001"`, `"SKU-250"` | PK, NOT NULL, padrão SKU-NNN |
| nome_produto | STRING | Nome descritivo do produto | `"Smartphone Galaxy S24"` | NOT NULL |
| categoria | STRING | Categoria principal do produto | `"Smartphones"` | NOT NULL |
| subcategoria | STRING | Subcategoria do produto | `"Premium"`, `"Intermediário"` | NOT NULL |
| preco_venda | DECIMAL(10,2) | Preço unitário de venda em reais (R$) | `4999.99`, `129.90` | NOT NULL, > 0 |
| preco_custo | DECIMAL(10,2) | Preço de custo unitário em reais (R$) | `3200.00`, `85.50` | NOT NULL, > 0 |
| estoque | INT | Quantidade disponível em estoque | `150`, `42`, `0` | NOT NULL, >= 0 |

**Particionamento:** sem particionamento (tabela de pequeno volume)

**Total de registros:** 250

**Categorias:** Smartphones, Notebooks, Acessórios, Áudio, Tablets, Monitores, Periféricos, Armazenamento

---

### bronze_pedidos

Origem: `source/pedidos.csv` (8.000 registros sintéticos). Registro de vendas realizadas.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| pedido_id | INT | Identificador único do pedido | `1`, `5000`, `8000` | PK, NOT NULL |
| cliente_id | INT | Chave estrangeira para o cliente que realizou a compra | `342`, `1500` | FK → clientes.cliente_id, NOT NULL |
| sku | STRING | Chave estrangeira para o produto adquirido | `"SKU-042"`, `"SKU-250"` | FK → produtos.sku, NOT NULL |
| data_pedido | DATE | Data em que o pedido foi realizado | `"2025-01-10"` | NOT NULL |
| quantidade | INT | Quantidade de itens comprados no pedido | `1`, `3`, `10` | NOT NULL, > 0 |
| valor_frete | DECIMAL(10,2) | Valor do frete cobrado em reais (R$) | `0.00`, `25.90`, `49.99` | NOT NULL, >= 0 |
| municipio | STRING | Município de entrega do pedido | `"São Paulo"`, `"Salvador"` | NOT NULL |
| estado | STRING | Sigla da UF de entrega | `"SP"`, `"BA"`, `"AM"` | NOT NULL, 2 caracteres |
| regiao | STRING | Região geográfica de entrega | `"Sudeste"`, `"Nordeste"` | NOT NULL |
| id_vendedor | INT | Identificador do vendedor responsável pela venda | `1`, `8`, `15` | FK → vendedores, NOT NULL |

**Particionamento:** `regiao` (5 partições)

**Total de registros:** 8.000

**Estados brasileiros cobertos:** SP, RJ, MG, RS, PR, BA, PE, CE, AM, DF

---

## Camada Silver

A camada Silver contém dados limpos, padronizados, validados e enriquecidos. Transformações incluem: remoção de duplicatas, padronização de strings (Title Case para nomes, UPPER para siglas), validação de preços positivos, enriquecimento com valor total do pedido via JOIN com produtos, e tipagem consistente.

### silver_clientes

Origem: `bronze_clientes` com limpeza e padronização.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| cliente_id | INT | Identificador único do cliente | `1`, `523`, `1500` | PK, NOT NULL |
| nome | STRING | Nome padronizado em Title Case (primeira letra de cada palavra maiúscula) | `"Ana Silva"` (antes: `"ana silva"`) | NOT NULL |
| email | STRING | E-mail normalizado em minúsculas | `"ana.silva@email.com"` | NOT NULL |
| telefone | STRING | Telefone mantido no formato original | `"(11) 98765-4321"` | NOT NULL |
| cidade | STRING | Município padronizado em Title Case | `"São Paulo"` | NOT NULL |
| estado | STRING | Sigla da UF padronizada em caixa alta (UPPER) | `"SP"`, `"RJ"` | NOT NULL, 2 caracteres |
| regiao | STRING | Região padronizada em Title Case | `"Sudeste"` | NOT NULL |
| data_cadastro | DATE | Data de cadastro, tipo DATE validado | `2024-03-15` | NOT NULL |

**Transformações aplicadas:**
- Remoção de duplicatas (DISTINCT por `cliente_id` ou `dropDuplicates`)
- `nome`, `cidade`, `regiao`: conversão para Title Case via `initcap()`
- `estado`: conversão para UPPER via `upper()`
- `email`: conversão para lowercase via `lower()`
- Validação de `data_cadastro` como tipo DATE
- Verificação de ausência de nulos em `cliente_id`

**Particionamento:** mantido por `regiao`

**Total de registros:** ≤ 1.500 (1.500 se nenhum duplicado removido)

---

### silver_produtos

Origem: `bronze_produtos` com limpeza e validação.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| sku | STRING | Código SKU padronizado | `"SKU-001"` | PK, NOT NULL |
| nome_produto | STRING | Nome do produto em Title Case | `"Smartphone Galaxy S24"` | NOT NULL |
| categoria | STRING | Categoria em Title Case | `"Smartphones"`, `"Notebooks"` | NOT NULL |
| subcategoria | STRING | Subcategoria em Title Case | `"Premium"` | NOT NULL |
| preco_venda | DECIMAL(10,2) | Preço de venda validado (deve ser > 0) | `4999.99` | NOT NULL, > 0 |
| preco_custo | DECIMAL(10,2) | Preço de custo validado (deve ser > 0) | `3200.00` | NOT NULL, > 0 |
| estoque | INT | Estoque validado (>= 0) | `150` | NOT NULL, >= 0 |
| margem | DECIMAL(10,2) | Margem bruta calculada: preco_venda - preco_custo | `1799.99` | Calculado, >= 0 |
| margem_pct | DECIMAL(5,2) | Percentual de margem: (margem / preco_venda) × 100 | `36.00` | Calculado |

**Transformações aplicadas:**
- `nome_produto`, `categoria`, `subcategoria`: Title Case
- SKU deduplicado: `COUNT(DISTINCT sku) = COUNT(sku)`
- Validação: `preco_venda > 0`, `preco_custo > 0`, `estoque >= 0`
- Enriquecimento: cálculo de `margem = preco_venda - preco_custo`
- Enriquecimento: cálculo de `margem_pct = ROUND((preco_venda - preco_custo) / preco_venda * 100, 2)`
- Remoção de produtos com dados inválidos (preços zero ou negativos)

**Particionamento:** sem particionamento

**Total de registros:** ≤ 250

---

### silver_pedidos

Origem: `bronze_pedidos` com limpeza, validação e enriquecimento via JOIN com `silver_produtos`.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| pedido_id | INT | Identificador único do pedido | `1`, `5000`, `8000` | PK, NOT NULL |
| cliente_id | INT | Chave estrangeira para cliente | `342`, `1500` | FK, NOT NULL |
| sku | STRING | Chave estrangeira para produto | `"SKU-042"` | FK, NOT NULL |
| data_pedido | DATE | Data do pedido, tipo DATE validado | `2025-01-10` | NOT NULL |
| quantidade | INT | Quantidade comprada (validada > 0) | `1`, `3`, `10` | NOT NULL, > 0 |
| preco_venda | DECIMAL(10,2) | Preço unitário de venda (obtido do JOIN com produtos) | `4999.99` | FK, NOT NULL, > 0 |
| valor_frete | DECIMAL(10,2) | Valor do frete cobrado (validado >= 0) | `25.90` | NOT NULL, >= 0 |
| total_pedido | DECIMAL(10,2) | Valor total do pedido: (quantidade × preco_venda) + valor_frete | `5025.89` | Calculado, NOT NULL, > 0 |
| municipio | STRING | Município de entrega em Title Case | `"São Paulo"` | NOT NULL |
| estado | STRING | Sigla da UF em caixa alta | `"SP"` | NOT NULL, 2 caracteres |
| regiao | STRING | Região em Title Case | `"Sudeste"` | NOT NULL |
| id_vendedor | INT | Identificador do vendedor | `8` | FK, NOT NULL |

**Transformações aplicadas:**
- JOIN `bronze_pedidos` com `silver_produtos` via `sku` para obter `preco_venda`
- `total_pedido = (quantidade × preco_venda) + valor_frete`
- Validação: `quantidade > 0`, `valor_frete >= 0`, `total_pedido > 0`
- Limpeza de strings: `municipio` e `regiao` em Title Case, `estado` em UPPER
- Conversão de `data_pedido` para tipo DATE
- Remoção de pedidos órfãos (cliente ou produto inexistente após validação)
- Remoção de duplicatas por `pedido_id`

**Particionamento:** mantido por `regiao`

**Total de registros:** ≤ 8.000

---

## Camada Gold (Star Schema)

A camada Gold implementa o modelo dimensional Star Schema (Esquema Estrela), otimizado para consultas analíticas no Power BI. Contém 4 dimensões descritivas e 1 fato central. Todas as tabelas em formato Delta Lake.

---

### dim_clientes

Dimensão de clientes. Contém atributos descritivos para análise de perfil do consumidor.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| id_cliente | INT | Chave substituta (surrogate key) da dimensão cliente | `1`, `500`, `1500` | PK, NOT NULL |
| nome | STRING | Nome do cliente em Title Case | `"Ana Silva"` | NOT NULL |
| cidade | STRING | Município de residência | `"São Paulo"` | NOT NULL |
| estado | STRING | Sigla da UF (UPPER) | `"SP"` | NOT NULL, 2 caracteres |
| regiao | STRING | Região geográfica | `"Sudeste"` | NOT NULL |

**Origem:** `silver_clientes` com seleção apenas das colunas dimensionais.

**Total de registros:** ≤ 1.500

**SCD Type:** Type 1 (sobrescreve alterações — dados históricos não mantidos nesta versão)

---

### dim_produtos

Dimensão de produtos. Contém atributos descritivos do catálogo de eletrônicos.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| id_produto | INT | Chave substituta da dimensão produto (derivada do SKU) | `1`, `100`, `250` | PK, NOT NULL |
| nome_produto | STRING | Nome do produto em Title Case | `"Smartphone Galaxy S24"` | NOT NULL |
| categoria | STRING | Categoria do produto | `"Smartphones"`, `"Notebooks"` | NOT NULL |
| preco_venda | DECIMAL(10,2) | Preço unitário de venda em R$ | `4999.99` | NOT NULL, > 0 |

**Origem:** `silver_produtos` com seleção de colunas dimensionais e geração de `id_produto` a partir do SKU (ex.: `SKU-042` → `id_produto = 42`).

**Total de registros:** ≤ 250

**Categorias (8):** Smartphones, Notebooks, Acessórios, Áudio, Tablets, Monitores, Periféricos, Armazenamento

---

### dim_calendario

Dimensão de calendário. Gerada programaticamente para cobrir todas as datas presentes nos pedidos, mais margem para filtros. Cada linha representa um dia.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| data | DATE | Data completa no formato AAAA-MM-DD (chave da dimensão) | `2025-01-15` | PK, NOT NULL |
| dia | INT | Dia do mês (1 a 31) | `15` | NOT NULL, 1-31 |
| mes | STRING | Nome do mês por extenso em português, Title Case | `"Janeiro"`, `"Dezembro"` | NOT NULL |
| nome_mes | STRING | Nome do mês abreviado (3 letras) em português | `"Jan"`, `"Fev"`, `"Dez"` | NOT NULL |
| mes_num | INT | Número do mês (1 a 12) | `1`, `6`, `12` | NOT NULL, 1-12 |
| trimestre | INT | Trimestre do ano (1 a 4) | `1` (Jan-Mar), `3` (Jul-Set) | NOT NULL, 1-4 |
| ano | INT | Ano com 4 dígitos | `2025`, `2026` | NOT NULL |

**Origem:** Gerada via `pyspark.sql.functions.sequence()` a partir de `min(data_pedido)` e `max(data_pedido)` com intervalo de 1 dia.

**Exemplo de range:** `2024-01-01` a `2025-12-31` (ajustado dinamicamente conforme os dados)

**Total de registros:** variável (~365 a 730 dias dependendo do range dos pedidos)

---

### dim_vendedores

Dimensão de vendedores. Criada artificialmente com 15 vendedores pré-definidos.

| Coluna | Tipo | Descrição | Exemplo | Restrições |
|--------|------|-----------|---------|------------|
| id_vendedor | INT | Chave substituta da dimensão vendedor (1 a 15) | `1`, `8`, `15` | PK, NOT NULL, 1-15 |
| nome | STRING | Nome completo do vendedor | `"Carlos Mendes"` | NOT NULL |
| regiao | STRING | Região de atuação principal do vendedor | `"Sudeste"` | NOT NULL |

**Vendedores cadastrados (15):**

| id_vendedor | nome | regiao |
|-------------|------|--------|
| 1 | Carlos Mendes | Sudeste |
| 2 | Ana Beatriz | Sudeste |
| 3 | Roberto Nunes | Sudeste |
| 4 | Fernanda Lima | Sul |
| 5 | Paulo César | Sul |
| 6 | Juliana Alves | Nordeste |
| 7 | Ricardo Souza | Nordeste |
| 8 | Mariana Costa | Nordeste |
| 9 | Lucas Pereira | Centro-Oeste |
| 10 | Camila Rocha | Centro-Oeste |
| 11 | Eduardo Santos | Norte |
| 12 | Patrícia Gomes | Norte |
| 13 | Felipe Oliveira | Sudeste |
| 14 | Tatiane Martins | Sul |
| 15 | Gustavo Barbosa | Centro-Oeste |

**Origem:** Dados hard-coded na camada Gold, persistidos como tabela Delta.

**Total de registros:** 15 (fixo)

---

### fact_vendas

Tabela fato central do Star Schema. Cada linha representa um pedido individual. Contém chaves estrangeiras para todas as dimensões, medidas quantitativas e atributos descritivos degenerados.

| Coluna | Tipo | Descrição | Exemplo | FK | Restrições |
|--------|------|-----------|---------|----|------------|
| pedido_id | INT | Chave degenerada (degenerate dimension) — identificador do pedido | `5000` | — | NOT NULL |
| id_cliente | INT | Chave estrangeira para `dim_clientes.id_cliente` | `342` | dim_clientes | FK, NOT NULL |
| id_produto | INT | Chave estrangeira para `dim_produtos.id_produto` | `42` | dim_produtos | FK, NOT NULL |
| data_pedido | DATE | Chave estrangeira para `dim_calendario.data` | `2025-01-10` | dim_calendario | FK, NOT NULL |
| id_vendedor | INT | Chave estrangeira para `dim_vendedores.id_vendedor` | `8` | dim_vendedores | FK, NOT NULL |
| quantidade | INT | Quantidade de itens no pedido | `1`, `3`, `10` | — | NOT NULL, > 0 |
| valor_frete | DECIMAL(10,2) | Valor do frete em R$ | `25.90` | — | NOT NULL, >= 0 |
| total_pedido | DECIMAL(10,2) | Valor total do pedido = (quantidade × preco_venda) + frete | `5025.89` | — | Medida, NOT NULL, > 0 |
| municipio | STRING | Município de entrega (atributo degenerado geográfico) | `"São Paulo"` | — | NOT NULL |
| estado | STRING | Sigla da UF de entrega | `"SP"` | — | NOT NULL, 2 caracteres |
| regiao | STRING | Região de entrega | `"Sudeste"` | — | NOT NULL |

**Origem:** `silver_pedidos` com mapeamento de chaves naturais para chaves substitutas:
- `cliente_id` (Silver) → `id_cliente` (Gold)
- `sku` (Silver) → `id_produto` (Gold, extraído do número do SKU)
- `data_pedido` → `data` (FK para dim_calendario)
- `id_vendedor` mantido como chave natural (1-15)

**Particionamento:** por `regiao` (5 partições)

**Total de registros:** ≤ 8.000

**Granularidade:** 1 linha = 1 pedido (um pedido contém um produto; não há itens de pedido separados nesta versão)

---

## Relacionamentos do Star Schema

```
                    ┌──────────────────┐
                    │   dim_clientes    │
                    │  (id_cliente PK)  │
                    └────────┬─────────┘
                             │ 1:N
                             │
        ┌──────────────────┐ │ ┌──────────────────┐
        │   dim_produtos   │ │ │ dim_calendario    │
        │ (id_produto PK)  │ │ │   (data PK)       │
        └────────┬─────────┘ │ └────────┬─────────┘
                 │ 1:N        │          │ 1:N
                 │            │          │
        ┌────────┴────────────┴──────────┴─────────┐
        │              fact_vendas                  │
        │  pedido_id (degenerada)                   │
        │  id_cliente (FK)     id_produto (FK)      │
        │  data_pedido (FK)    id_vendedor (FK)     │
        │  quantidade, valor_frete, total_pedido    │
        │  municipio, estado, regiao                │
        └────────┬─────────────────────────────────┘
                 │ N:1
        ┌────────┴─────────┐
        │ dim_vendedores   │
        │(id_vendedor PK)  │
        └──────────────────┘
```

---

## Mapeamento de Tipos entre Camadas

| Fonte (CSV) | Bronze (Delta) | Silver (Delta) | Gold (Delta) | Descrição |
|-------------|----------------|----------------|--------------|-----------|
| `int` | `IntegerType` | `IntegerType` | `IntegerType` | IDs e contagens |
| `str` | `StringType` | `StringType` | `StringType` | Textos e códigos |
| `float` | `DecimalType(10,2)` | `DecimalType(10,2)` | `DecimalType(10,2)` | Valores monetários |
| `date` | `DateType` | `DateType` | `DateType` | Datas |

---

## Volume Estimado por Camada

| Camada | Tabela | Registros | Colunas | Tamanho Estimado |
|--------|--------|-----------|---------|------------------|
| Bronze | clientes | 1.500 | 8 | ~150 KB |
| Bronze | produtos | 250 | 7 | ~25 KB |
| Bronze | pedidos | 8.000 | 10 | ~800 KB |
| Silver | clientes | ≤1.500 | 8 | ~150 KB |
| Silver | produtos | ≤250 | 9 | ~30 KB |
| Silver | pedidos | ≤8.000 | 12 | ~1 MB |
| Gold | dim_clientes | ≤1.500 | 5 | ~100 KB |
| Gold | dim_produtos | ≤250 | 4 | ~20 KB |
| Gold | dim_calendario | ≤730 | 7 | ~50 KB |
| Gold | dim_vendedores | 15 | 3 | ~1 KB |
| Gold | fact_vendas | ≤8.000 | 11 | ~900 KB |

---

## Glossário de Restrições

| Símbolo | Significado |
|---------|-------------|
| PK | Primary Key — chave primária, identifica unicamente cada linha |
| FK | Foreign Key — chave estrangeira, referencia chave primária de outra tabela |
| NOT NULL | Coluna não aceita valores nulos |
| SK | Surrogate Key — chave substituta artificial gerada pelo sistema |
| SCD | Slowly Changing Dimension — estratégia de versionamento dimensional |
| > 0 | Valor estritamente positivo |
| >= 0 | Valor não negativo |

---

*Documento gerado para o projeto BI E-Commerce — arquitetura Medallion com PySpark + Delta Lake.*
