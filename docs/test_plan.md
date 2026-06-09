# Plano de Testes — BI E-Commerce

## 1. Objetivo dos Testes

O plano de testes do projeto BI E-Commerce tem como objetivo garantir que todas as etapas do pipeline de dados produzam resultados corretos, consistentes e confiáveis. Os testes verificam:

- **Integridade dos dados gerados:** se os CSVs sintéticos possuem o volume, schema e restrições esperados.
- **Corretude das transformações:** se as regras de limpeza, padronização e enriquecimento produzem os resultados esperados.
- **Consistência entre camadas:** se a quantidade de registros evolui corretamente entre Bronze, Silver e Gold.
- **Integridade referencial:** se todas as chaves estrangeiras na tabela fato possuem correspondentes válidos nas dimensões.
- **Precisão das métricas:** se os KPIs calculados (faturamento, total de pedidos, ticket médio, total de vendedores) estão corretos.
- **Qualidade dos dados:** se não há valores nulos inesperados, duplicatas, preços inválidos ou datas fora de intervalo.

---

## 2. Escopo

### 2.1 O que é testado

- Geração de dados sintéticos (volume, schema).
- Validação de entradas (00_generate_data.py, 01_validate_inputs.py).
- Ingestão na camada Bronze (10_bronze_ingestion.py).
- Transformações na camada Silver (20_silver_transform.py):
  - Padronização de strings (Title Case, UPPER, lowercase).
  - Validação de preços (> 0), estoque (>= 0), datas (tipo DATE).
  - Deduplicação (cliente_id, SKU, pedido_id).
  - Enriquecimento (total_pedido, margem, margem_pct).
- Modelagem na camada Gold (30_gold_model.py):
  - Criação das 4 dimensões e 1 fato.
  - Geração da dimensão calendário.
  - Mapeamento de chaves naturais para surrogate keys.
- Verificações de qualidade (40_quality_checks.py):
  - Contagens de registros.
  - Unicidade de chaves.
  - Integridade referencial (4 LEFT ANTI JOINs).
  - Domínios e nulos.
  - Métricas de KPI.
- Consistência das métricas de negócio (faturamento, pedidos, ticket médio).

### 2.2 O que NÃO é testado

- Performance e escalabilidade (projeto acadêmico, volume pequeno).
- Segurança de dados (não há criptografia ou RBAC implementados).
- Integração com sistemas externos (tudo é local).
- Recuperação de falhas (não há mecanismo de retry ou checkpoint).
- Qualidade visual do dashboard (Power BI é validado manualmente).
- Usabilidade da interface do dashboard.
- Compatibilidade com diferentes versões de navegadores.
- Tempo de execução máximo (SLA).
- Dados reais (os dados são sintéticos).

---

## 3. Estratégia de Teste

A estratégia combina duas abordagens:

### 3.1 Testes Automatizados

Executados pelo script `40_quality_checks.py` ao final do pipeline. Implementam verificações programáticas usando PySpark DataFrames. Cada verificação é uma função que levanta uma exceção (`raise Exception`) se a condição não for satisfeita, interrompendo o pipeline com uma mensagem descritiva.

**Tecnologia:** PySpark (DataFrame API).

**Cobertura:** 10 verificações automatizadas cobrindo contagem, unicidade, integridade referencial, domínios, nulos e métricas.

### 3.2 Testes Manuais

Executados pelo desenvolvedor/avaliador em momentos específicos:

1. Após a geração de dados: inspeção visual dos CSVs para verificar realismo e distribuição.
2. Após a camada Gold: consultas exploratórias com Spark SQL para validar resultados.
3. No Power BI: validação visual dos gráficos e medidas, conferência de cross-filtering e drill-through.

**Ferramentas:** Leitura de CSV em editor de texto ou Excel, Spark shell, Power BI Desktop.

---

## 4. Casos de Teste por Camada

### 4.1 Testes da Camada Bronze

A camada Bronze deve conter os dados brutos fiéis às fontes. Testes focam em volume, schema e tipos.

| ID | Cenário | Pré-condição | Passos | Resultado Esperado | Tipo |
|----|---------|-------------|--------|--------------------|------|
| TC-BR-01 | Contagem bronze_clientes | Dados gerados | `spark.read.format("delta").load("data/bronze/bronze_clientes").count()` | 1.500 registros | Automatizado |
| TC-BR-02 | Contagem bronze_produtos | Dados gerados | `spark.read.format("delta").load("data/bronze/bronze_produtos").count()` | 250 registros | Automatizado |
| TC-BR-03 | Contagem bronze_pedidos | Dados gerados | `spark.read.format("delta").load("data/bronze/bronze_pedidos").count()` | 8.000 registros | Automatizado |
| TC-BR-04 | Schema bronze_clientes | Dados gerados | `df.printSchema()` e comparar com schema esperado (8 colunas) | 8 colunas com nomes e tipos corretos | Automatizado |
| TC-BR-05 | Schema bronze_produtos | Dados gerados | `df.printSchema()` e comparar com schema esperado (7 colunas) | 7 colunas com nomes e tipos corretos | Automatizado |
| TC-BR-06 | Schema bronze_pedidos | Dados gerados | `df.printSchema()` e comparar com schema esperado (10 colunas) | 10 colunas com nomes e tipos corretos | Automatizado |
| TC-BR-07 | Tipo cliente_id | Dados gerados | `df.schema["cliente_id"].dataType` | `IntegerType` | Automatizado |
| TC-BR-08 | Tipo data_pedido | Dados gerados | `df.schema["data_pedido"].dataType` | `DateType` | Automatizado |
| TC-BR-09 | Tipo preco_venda | Dados gerados | `df.schema["preco_venda"].dataType` | `DecimalType(10,2)` | Automatizado |
| TC-BR-10 | Particionamento clientes | Dados gerados | Listar subpastas em `bronze_clientes/` | 5 partições (uma por região) | Automatizado |
| TC-BR-11 | Particionamento pedidos | Dados gerados | Listar subpastas em `bronze_pedidos/` | 5 partições (uma por região) | Automatizado |
| TC-BR-12 | Unicidade cliente_id (Bronze) | Dados gerados | `df.select("cliente_id").distinct().count() == df.count()` | True (sem duplicatas) | Automatizado |
| TC-BR-13 | Unicidade sku (Bronze) | Dados gerados | `df.select("sku").distinct().count() == df.count()` | True (sem duplicatas) | Automatizado |
| TC-BR-14 | Unicidade pedido_id (Bronze) | Dados gerados | `df.select("pedido_id").distinct().count() == df.count()` | True (sem duplicatas) | Automatizado |
| TC-BR-15 | Cliente_id NOT NULL | Dados gerados | `df.filter(F.col("cliente_id").isNull()).count()` | 0 nulos | Automatizado |

### 4.2 Testes da Camada Silver

A camada Silver aplica transformações de qualidade. Testes focam em padronização, validação e enriquecimento.

| ID | Cenário | Pré-condição | Passos | Resultado Esperado | Tipo |
|----|---------|-------------|--------|--------------------|------|
| TC-SV-01 | Remoção de duplicatas clientes | Bronze tem dados | `silver_clientes.select("cliente_id").distinct().count()` vs `silver_clientes.count()` | Igual (clientes únicos) | Automatizado |
| TC-SV-02 | Remoção de duplicatas produtos | Bronze tem dados | `silver_produtos.select("sku").distinct().count()` vs `silver_produtos.count()` | Igual (SKUs únicos) | Automatizado |
| TC-SV-03 | Remoção de duplicatas pedidos | Bronze tem dados | `silver_pedidos.select("pedido_id").distinct().count()` vs `silver_pedidos.count()` | Igual (pedidos únicos) | Automatizado |
| TC-SV-04 | Padronização nome (Title Case) | Nomes em vários formatos no CSV | Verificar que toda string em "nome" tem primeira letra maiúscula | `"João Silva"` (não `"joão silva"` ou `"JOÃO SILVA"`) | Automatizado |
| TC-SV-05 | Padronização estado (UPPER) | Estados em vários formatos | Verificar `F.col("estado") == F.upper(F.col("estado"))` para todas as linhas | True (todos em caixa alta) | Automatizado |
| TC-SV-06 | Padronização email (lowercase) | E-mails com capitalização mista | Verificar `F.col("email") == F.lower(F.col("email"))` | True (todos em minúsculas) | Automatizado |
| TC-SV-07 | Preços de venda válidos | Produtos com preço negativo/zero nos dados | `silver_produtos.filter(F.col("preco_venda") <= 0).count()` | 0 (todos positivos) | Automatizado |
| TC-SV-08 | Preços de custo válidos | Produtos com custo negativo/zero | `silver_produtos.filter(F.col("preco_custo") <= 0).count()` | 0 (todos positivos) | Automatizado |
| TC-SV-09 | Estoque não negativo | Produtos com estoque negativo | `silver_produtos.filter(F.col("estoque") < 0).count()` | 0 (todos >= 0) | Automatizado |
| TC-SV-10 | Quantidade positiva nos pedidos | Pedidos com quantidade zero/negativa | `silver_pedidos.filter(F.col("quantidade") <= 0).count()` | 0 (todos > 0) | Automatizado |
| TC-SV-11 | Cálculo do total_pedido | Silver pedidos criado com produtos | `total_pedido == round(quantidade * preco_venda + valor_frete, 2)` | True para todas as linhas | Automatizado |
| TC-SV-12 | total_pedido > 0 | Silver pedidos criado | `silver_pedidos.filter(F.col("total_pedido") <= 0).count()` | 0 | Automatizado |
| TC-SV-13 | Cálculo da margem | Silver produtos criado | `margem == preco_venda - preco_custo` | True para todas as linhas | Automatizado |
| TC-SV-14 | Cálculo margem_pct | Silver produtos criado | `margem_pct == round((preco_venda - preco_custo) / preco_venda * 100, 2)` | True para todas as linhas | Automatizado |
| TC-SV-15 | Tipo data_pedido DATE | Bronze ingerido | `silver_pedidos.schema["data_pedido"].dataType` | `DateType` | Automatizado |
| TC-SV-16 | Cliente_id NOT NULL (Silver) | Dados com possíveis nulos | `silver_clientes.filter(F.col("cliente_id").isNull()).count()` | 0 | Automatizado |
| TC-SV-17 | SKU NOT NULL (Silver) | Dados com possíveis nulos | `silver_produtos.filter(F.col("sku").isNull()).count()` | 0 | Automatizado |
| TC-SV-18 | Pedido_id NOT NULL (Silver) | Dados com possíveis nulos | `silver_pedidos.filter(F.col("pedido_id").isNull()).count()` | 0 | Automatizado |
| TC-SV-19 | Sem pedidos órfãos de produto | SKU inválido nos pedidos | JOIN silver_pedidos com silver_produtos deve retornar todas as linhas | 0 pedidos sem produto correspondente | Automatizado |
| TC-SV-20 | Intervalo de datas | Silver pedidos criado | Min e max data_pedido | Entre 2024-01-01 e 2025-12-31 | Automatizado |

### 4.3 Testes da Camada Gold

A camada Gold implementa o Star Schema. Testes focam em dimensionalidade, chaves substitutas e integridade referencial.

| ID | Cenário | Pré-condição | Passos | Resultado Esperado | Tipo |
|----|---------|-------------|--------|--------------------|------|
| TC-GD-01 | dim_clientes criada | Silver pronto | `spark.read.format("delta").load("data/gold/dim_clientes").count()` | ≤ 1.500 | Automatizado |
| TC-GD-02 | dim_produtos criada | Silver pronto | `spark.read.format("delta").load("data/gold/dim_produtos").count()` | ≤ 250 | Automatizado |
| TC-GD-03 | dim_calendario criada | Silver pronto | Verificar contagem de datas | Range cobre min(data_pedido) a max(data_pedido) | Automatizado |
| TC-GD-04 | dim_vendedores criada | N/A (dados fixos) | `spark.read.format("delta").load("data/gold/dim_vendedores").count()` | 15 | Automatizado |
| TC-GD-05 | fact_vendas criada | Silver pronto + dimensões | `spark.read.format("delta").load("data/gold/fact_vendas").count()` | ≤ 8.000 | Automatizado |
| TC-GD-06 | Unicidade id_cliente | dim_clientes criada | `COUNT(id_cliente) == COUNT(DISTINCT id_cliente)` | True | Automatizado |
| TC-GD-07 | Unicidade id_produto | dim_produtos criada | `COUNT(id_produto) == COUNT(DISTINCT id_produto)` | True | Automatizado |
| TC-GD-08 | Unicidade data (dim_calendario) | dim_calendario criada | `COUNT(data) == COUNT(DISTINCT data)` | True | Automatizado |
| TC-GD-09 | Unicidade id_vendedor | dim_vendedores criada | `COUNT(id_vendedor) == COUNT(DISTINCT id_vendedor)` | True | Automatizado |
| TC-GD-10 | Integridade referencial cliente | fact + dim_clientes criados | LEFT ANTI JOIN: `fact_vendas.join(dim_clientes, "id_cliente", "left_anti")` | 0 linhas (sem órfãos) | Automatizado |
| TC-GD-11 | Integridade referencial produto | fact + dim_produtos criados | LEFT ANTI JOIN: `fact_vendas.join(dim_produtos, "id_produto", "left_anti")` | 0 linhas (sem órfãos) | Automatizado |
| TC-GD-12 | Integridade referencial data | fact + dim_calendario criados | LEFT ANTI JOIN: `fact_vendas.join(dim_calendario, F.col("data_pedido") == F.col("data"), "left_anti")` | 0 linhas (sem órfãos) | Automatizado |
| TC-GD-13 | Integridade referencial vendedor | fact + dim_vendedores criados | LEFT ANTI JOIN: `fact_vendas.join(dim_vendedores, "id_vendedor", "left_anti")` | 0 linhas (sem órfãos) | Automatizado |
| TC-GD-14 | Schema dim_clientes | dim_clientes criada | Verificar colunas: id_cliente, nome, cidade, estado, regiao | 5 colunas, tipos corretos | Automatizado |
| TC-GD-15 | Schema dim_produtos | dim_produtos criada | Verificar colunas: id_produto, nome_produto, categoria, preco_venda | 4 colunas, tipos corretos | Automatizado |
| TC-GD-16 | Schema dim_calendario | dim_calendario criada | Verificar colunas: data, dia, mes, nome_mes, mes_num, trimestre, ano | 7 colunas, tipos corretos | Automatizado |
| TC-GD-17 | Schema dim_vendedores | dim_vendedores criada | Verificar colunas: id_vendedor, nome, regiao | 3 colunas, tipos corretos | Automatizado |
| TC-GD-18 | Schema fact_vendas | fact_vendas criada | Verificar 11 colunas: pedido_id, id_cliente, id_produto, data_pedido, id_vendedor, quantidade, valor_frete, total_pedido, municipio, estado, regiao | 11 colunas, tipos corretos | Automatizado |
| TC-GD-19 | Nomes de vendedores corretos | dim_vendedores criada | Verificar que os 15 nomes batem com a lista esperada | Carlos Mendes, Ana Beatriz, ... | Automatizado |
| TC-GD-20 | Regiões de vendedores corretas | dim_vendedores criada | Verificar distribuição regional dos 15 vendedores | 5 Sudeste, 3 Sul, 3 Nordeste, 3 Centro-Oeste, 1 Norte? ou conforme distribuição definida | Automatizado |

### 4.4 Testes de Métricas (KPIs)

As métricas de negócio devem ser consistentes com os dados subjacentes.

| ID | Cenário | Cálculo | Resultado Esperado | Tipo |
|----|---------|---------|--------------------|------|
| TC-MT-01 | Faturamento total | `SELECT SUM(total_pedido) FROM fact_vendas` | > 0 (valor depende dos dados gerados) | Automatizado |
| TC-MT-02 | Total de pedidos | `SELECT COUNT(DISTINCT pedido_id) FROM fact_vendas` | ≤ 8.000, consistente com Silver | Automatizado |
| TC-MT-03 | Ticket médio | `faturamento / total_pedidos` | > 0, aproximadamente = AVG(total_pedido) | Automatizado |
| TC-MT-04 | Total de vendedores | `SELECT COUNT(DISTINCT id_vendedor) FROM fact_vendas` | ≤ 15 (todos os 15 devem aparecer) | Automatizado |
| TC-MT-05 | Volume de itens | `SELECT SUM(quantidade) FROM fact_vendas` | ≥ total de pedidos (cada pedido tem pelo menos 1 item) | Automatizado |
| TC-MT-06 | Faturamento por região | `SELECT regiao, SUM(total_pedido) FROM fact_vendas GROUP BY regiao` | Todas as 5 regiões com valor > 0 | Automatizado |
| TC-MT-07 | Pedidos por categoria | `SELECT c.categoria, COUNT(DISTINCT f.pedido_id) FROM fact_vendas f JOIN dim_produtos p ON f.id_produto = p.id_produto GROUP BY p.categoria` | Todas as 8 categorias com valor > 0 | Automatizado |
| TC-MT-08 | Consistência total_pedido | `SUM(total_pedido) na fact_vendas` vs `SUM(quantidade * preco_venda + valor_frete) na silver_pedidos` | Valores iguais (com margem de arredondamento) | Automatizado |
| TC-MT-09 | Ticket médio por região | Para cada região: `SUM(total_pedido) / COUNT(DISTINCT pedido_id)` | > 0 para cada região | Manual (Power BI) |
| TC-MT-10 | Ranking de vendedores | Ordenar vendedores por faturamento decrescente | Lista de 15 vendedores com valores decrescentes | Manual (Power BI) |

---

## 5. Ambiente de Teste

### 5.1 Hardware

| Componente | Especificação Mínima |
|------------|---------------------|
| CPU | Intel Core i5 ou equivalente, 4 núcleos |
| RAM | 8 GB |
| Disco | SSD com 5 GB livres |
| SO | Windows 10/11 64-bit |

### 5.2 Software

| Software | Versão |
|----------|--------|
| Java JDK | 8 ou 11 |
| Python | 3.10 ou superior |
| PySpark | 3.4.x ou 3.5.x |
| Delta Lake | 3.0.x ou 3.1.x |
| Faker | 22.x ou superior |
| Pandas | 2.0.x ou superior |
| Jupyter | (opcional) 6.x |
| Power BI Desktop | última versão estável |

### 5.3 Configurações do Spark

- Master: `local[*]`
- Driver memory: padrão (ou 2g)
- Shuffle partitions: padrão (200)
- Extensões Delta: habilitadas

### 5.4 Dados de Teste

Os dados de teste são os próprios dados sintéticos gerados pelo script `00_generate_data.py`. Como a geração é determinística (ou pseudo-aleatória com seed fixa), os resultados são reprodutíveis em cada execução.

**Recomendação para reprodutibilidade:** Configurar uma seed fixa no Faker (`Faker.seed(42)`) e no random do Python (`random.seed(42)`) no script de geração para que os resultados sejam idênticos a cada execução.

---

## 6. Critérios de Aceite

### 6.1 Critérios de Sucesso para Testes Automatizados

Um teste automatizado é considerado **aprovado** quando:
- A condição booleana avaliada retorna `True`.
- Nenhuma exceção é lançada.
- O valor medido está dentro do intervalo esperado (para contagens com tolerância).

Um teste automatizado é considerado **reprovado** quando:
- A condição avaliada retorna `False`.
- Uma exceção é lançada com mensagem descritiva.
- O valor medido está fora do intervalo esperado.

### 6.2 Critérios de Sucesso para Testes Manuais

Um teste manual é considerado **aprovado** quando:
- A inspeção visual confirma o resultado esperado.
- O dashboard Power BI exibe os valores corretos.
- As interações (cross-filtering, slicers, drill-through) funcionam conforme esperado.

### 6.3 Critérios de Aceite Gerais do Projeto

Para que o projeto seja considerado **aprovado** na bateria de testes:

1. **100% dos testes automatizados devem passar** (10 verificações no `40_quality_checks.py`).
2. **0 registros órfãos** — integridade referencial perfeita.
3. **Contagens consistentes** entre camadas (Silver ≤ Bronze, Gold ≤ Silver).
4. **Métricas positivas e coerentes** — faturamento > 0, ticket médio > 0.
5. **Dashboard funcional** — todos os visuais carregam sem erros, medidas calculam corretamente.
6. **15 vendedores distintos** aparecem tanto na dimensão quanto nos fatos.

### 6.4 Critérios de Rejeição

O projeto é considerado **reprovado** se:
- Qualquer verificação automatizada falhar.
- Houver registros órfãos (integridade referencial quebrada).
- Faturamento ou ticket médio zerado ou negativo.
- Menos de 15 vendedores na dimensão ou fato.
- Dashboard não carregar ou exibir erros de relacionamento.

---

## 7. Relatório de Testes

### 7.1 Template de Relatório

Após cada execução do pipeline, preencha o seguinte relatório:

```
================================================================================
                    RELATÓRIO DE TESTES — BI E-COMMERCE
================================================================================

Data da execução: ____/____/________
Executado por: ______________________
Versão do pipeline: 1.0

================================================================================
RESUMO GERAL
================================================================================

Total de verificações automatizadas: 10
Aprovadas: ___
Reprovadas: ___
Taxa de aprovação: ____%

Total de verificações manuais: 5
Aprovadas: ___
Reprovadas: ___

Status geral: [ ] APROVADO  [ ] REPROVADO

================================================================================
RESULTADOS DETALHADOS — VERIFICAÇÕES AUTOMATIZADAS
================================================================================

[ ] TC-BR-01: Contagem bronze_clientes → 1.500 registros ............ (OK / FALHA)
[ ] TC-BR-02: Contagem bronze_produtos → 250 registros .............. (OK / FALHA)
[ ] TC-BR-03: Contagem bronze_pedidos → 8.000 registros ............. (OK / FALHA)
[ ] TC-GD-04: Contagem dim_vendedores → 15 registros ................ (OK / FALHA)
[ ] TC-GD-01: Contagem dim_clientes → <= 1.500 registros ............ (OK / FALHA)
[ ] TC-GD-02: Contagem dim_produtos → <= 250 registros .............. (OK / FALHA)
[ ] TC-GD-05: Contagem fact_vendas → <= 8.000 registros ............. (OK / FALHA)
[ ] TC-GD-10: Integridade referencial cliente ....................... (OK / FALHA)
[ ] TC-GD-11: Integridade referencial produto ....................... (OK / FALHA)
[ ] TC-GD-12: Integridade referencial data .......................... (OK / FALHA)
[ ] TC-GD-13: Integridade referencial vendedor ...................... (OK / FALHA)
[ ] TC-MT-01: Faturamento > 0 ....................................... (OK / FALHA)
[ ] TC-MT-02: Total pedidos > 0 ..................................... (OK / FALHA)
[ ] TC-MT-03: Ticket médio > 0 ...................................... (OK / FALHA)
[ ] TC-MT-04: Total vendedores = 15 ................................. (OK / FALHA)

================================================================================
RESULTADOS DETALHADOS — VERIFICAÇÕES MANUAIS
================================================================================

[ ] Inspeção visual dos CSVs gerados ................................ (OK / FALHA)
[ ] Validação do schema no Power BI .................................. (OK / FALHA)
[ ] Verificação dos relacionamentos no Power BI ...................... (OK / FALHA)
[ ] Cálculo correto das medidas DAX .................................. (OK / FALHA)
[ ] Cross-filtering funcional ........................................ (OK / FALHA)

================================================================================
MÉTRICAS OBTIDAS
================================================================================

Faturamento total:     R$ __________________
Total de pedidos:      __________________
Ticket médio:          R$ __________________
Total de vendedores:   15
Volume de itens:       __________________

Faturamento por região:
  Norte:         R$ __________________
  Nordeste:      R$ __________________
  Centro-Oeste:  R$ __________________
  Sudeste:       R$ __________________
  Sul:           R$ __________________

================================================================================
OBSERVAÇÕES E INCIDENTES
================================================================================

________________________________________________________________________________
________________________________________________________________________________
________________________________________________________________________________

================================================================================
ASSINATURA
================================================================================

Responsável: ___________________________________
Data: ____/____/________

================================================================================
```

### 7.2 Frequência de Testes Recomendada

| Momento | O que testar |
|---------|-------------|
| Após cada alteração no código do pipeline | Execução completa do `run_pipeline.py` + verificação dos checks |
| Após alteração na lógica de geração de dados | Regerar dados + pipeline completo + inspeção manual dos CSVs |
| Após mudança de ambiente (nova máquina, novo SO) | Verificação de ambiente (seção 3 do Guia de Implementação) + pipeline completo |
| Antes de entrega ou apresentação | Pipeline completo + validação manual completa do Power BI |
| Após atualização de versões de bibliotecas | Pipeline completo, com atenção a warnings de depreciação |

---

*Documento gerado para o projeto BI E-Commerce — versão 1.0. Junho de 2026.*
