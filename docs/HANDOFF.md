# HANDOFF — BI E-Commerce (Guia de Referência Rápida)

Este documento é o ponto de partida para qualquer pessoa que precise entender ou operar o projeto rapidamente. Leia isso primeiro.

---

## 1. Como Rodar (3 Comandos)

Abra o PowerShell no diretório raiz do projeto e execute:

```bash
# 1. Instalar dependências (apenas na primeira vez)
pip install -r requirements.txt

# 2. Gerar dados sintéticos
python src/00_generate_data.py

# 3. Executar pipeline completo
python src/run_pipeline.py
```

**Tempo estimado:** 5 a 10 minutos (dependendo do hardware).

**Pré-requisitos:** Java JDK 8/11 instalado com `JAVA_HOME` configurado, Python 3.10+.

**O que esperar no console:** O pipeline exibe o progresso de cada etapa e, ao final, confirma que todas as verificações de qualidade passaram.

---

## 2. O que foi Feito

### Pipeline de Dados (6 scripts Python)

| Ordem | Script | Função |
|-------|--------|--------|
| 1 | `00_generate_data.py` | Gera 1.500 clientes, 250 produtos e 8.000 pedidos sintéticos em CSV |
| 2 | `01_validate_inputs.py` | Valida consistência dos CSVs (contagens, schemas, chaves) |
| 3 | `10_bronze_ingestion.py` | Ingestão bruta como tabelas Delta em `data/bronze/` |
| 4 | `20_silver_transform.py` | Limpeza, padronização e enriquecimento em `data/silver/` |
| 5 | `30_gold_model.py` | Modelagem Star Schema (4 dims + 1 fato) em `data/gold/` |
| 6 | `40_quality_checks.py` | 10 verificações automatizadas de qualidade |

### Arquitetura Medallion

```
CSV (source) → Bronze (raw Delta) → Silver (clean Delta) → Gold (Star Schema Delta) → Power BI
```

### Tecnologias

- **PySpark 3.x** — engine de processamento
- **Delta Lake 3.x** — armazenamento transacional com ACID
- **Python 3.10+** — linguagem de script
- **Power BI Desktop** — visualização e dashboard
- **Faker** — geração de dados sintéticos brasileiros

### Artefatos Entregues

- 3 arquivos CSV (source)
- 3 tabelas Delta Bronze (particionadas por região)
- 3 tabelas Delta Silver (limpas e enriquecidas)
- 5 tabelas Delta Gold (Star Schema)
- 1 dashboard Power BI com 3 páginas
- 7 documentos de documentação completa

---

## 3. Estrutura de Diretórios

```
bi_ecommerce/
│
├── data/
│   ├── source/                   # CSVs sintéticos (entrada)
│   │   ├── clientes.csv          #    1.500 registros
│   │   ├── produtos.csv          #      250 registros
│   │   └── pedidos.csv           #    8.000 registros
│   ├── bronze/                   # Delta — dados brutos
│   │   ├── bronze_clientes/
│   │   ├── bronze_produtos/
│   │   └── bronze_pedidos/
│   ├── silver/                   # Delta — dados limpos
│   │   ├── silver_clientes/
│   │   ├── silver_produtos/
│   │   └── silver_pedidos/
│   └── gold/                     # Delta — Star Schema
│       ├── dim_clientes/
│       ├── dim_produtos/
│       ├── dim_calendario/
│       ├── dim_vendedores/
│       └── fact_vendas/
│
├── src/                          # Código-fonte do pipeline
│   ├── 00_generate_data.py
│   ├── 01_validate_inputs.py
│   ├── 10_bronze_ingestion.py
│   ├── 20_silver_transform.py
│   ├── 30_gold_model.py
│   ├── 40_quality_checks.py
│   ├── run_pipeline.py           # Orquestrador (master)
│   └── spark_config.py           # Configuração Spark + Delta
│
├── powerbi/                      # Recursos do dashboard
│   ├── bi_ecommerce.pbix
│   ├── dax_measures.txt
│   └── dashboard_spec.txt
│
├── docs/                         # Documentação
│   ├── data_dictionary.md
│   ├── technical_documentation.md
│   ├── functional_documentation.md
│   ├── presentation_script.md
│   ├── implementation_guide.md
│   ├── test_plan.md
│   └── HANDOFF.md                # ← Você está aqui
│
├── notebooks/                    # Jupyter Notebooks
├── tests/                        # Testes
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 4. Schema Final (Gold — Star Schema)

### dim_clientes (até 1.500 linhas)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id_cliente | INT | PK — chave substituta |
| nome | STRING | Nome em Title Case |
| cidade | STRING | Município |
| estado | STRING | Sigla UF (UPPER) |
| regiao | STRING | Região geográfica |

### dim_produtos (até 250 linhas)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id_produto | INT | PK — extraído do número do SKU |
| nome_produto | STRING | Nome do produto |
| categoria | STRING | Categoria (8 valores) |
| preco_venda | DECIMAL | Preço unitário em R$ |

### dim_calendario (até ~730 linhas)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| data | DATE | PK — data completa |
| dia | INT | Dia do mês (1-31) |
| mes | STRING | Nome do mês por extenso |
| nome_mes | STRING | Mês abreviado (3 letras) |
| mes_num | INT | Número do mês (1-12) |
| trimestre | INT | Trimestre (1-4) |
| ano | INT | Ano (4 dígitos) |

### dim_vendedores (15 linhas fixas)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id_vendedor | INT | PK — 1 a 15 |
| nome | STRING | Nome completo |
| regiao | STRING | Região de atuação |

### fact_vendas (até 8.000 linhas)

| Coluna | Tipo | Descrição | FK |
|--------|------|-----------|----|
| pedido_id | INT | Chave degenerada | — |
| id_cliente | INT | FK → dim_clientes | dim_clientes |
| id_produto | INT | FK → dim_produtos | dim_produtos |
| data_pedido | DATE | FK → dim_calendario | dim_calendario |
| id_vendedor | INT | FK → dim_vendedores | dim_vendedores |
| quantidade | INT | Quantidade de itens | — |
| valor_frete | DECIMAL | Frete em R$ | — |
| total_pedido | DECIMAL | = qtd × preço + frete | — |
| municipio | STRING | Município de entrega | — |
| estado | STRING | UF de entrega (UPPER) | — |
| regiao | STRING | Região de entrega | — |

### Relacionamentos no Power BI

```
dim_clientes    (1) ──── (N) fact_vendas (N) ──── (1) dim_produtos
dim_calendario  (1) ──── (N) fact_vendas (N) ──── (1) dim_vendedores
```

Todas as cardinalidades: 1:N com direção de filtro única (dimensão → fato).

---

## 5. Como Conectar no Power BI

1. Abra o Power BI Desktop.
2. **Obter Dados → Pasta**.
3. Navegue até `C:\dev\projetoInt\bi_ecommerce\data\gold\`.
4. Selecione a subpasta de cada tabela (ex.: `dim_clientes/`) → **Combinar e Transformar**.
5. Repita para as 5 tabelas: `dim_clientes`, `dim_produtos`, `dim_calendario`, `dim_vendedores`, `fact_vendas`.
6. Configure os relacionamentos na aba **Modelo** (arrastar coluna FK para PK).
7. Crie as medidas DAX a partir de `powerbi/dax_measures.txt`.
8. Construa os visuais conforme `powerbi/dashboard_spec.txt`.

**Arquivo .pbix pronto:** Se disponível, abra `powerbi/bi_ecommerce.pbix` e atualize a fonte de dados apontando para `data/gold/`.

---

## 6. Validação Rápida

Para verificar se tudo está funcionando após a execução do pipeline:

### 6.1 Conferir diretórios Gold

```powershell
Get-ChildItem -LiteralPath "data\gold" -Directory | Select-Object Name
```

**Saída esperada:**
```
dim_clientes
dim_produtos
dim_calendario
dim_vendedores
fact_vendas
```

### 6.2 Conferir contagens com Spark

```bash
python -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .master('local[*]') \
    .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension') \
    .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog') \
    .getOrCreate()

for t in ['dim_clientes','dim_produtos','dim_calendario','dim_vendedores','fact_vendas']:
    c = spark.read.format('delta').load(f'data/gold/{t}').count()
    print(f'{t}: {c} registros')

spark.stop()
"
```

**Saída esperada (aproximada):**
```
dim_clientes: 1500 registros
dim_produtos: 250 registros
dim_calendario: ~730 registros
dim_vendedores: 15 registros
fact_vendas: 8000 registros
```

### 6.3 Conferir integridade referencial

```bash
python src/40_quality_checks.py
```

**Saída esperada:** `[OK] 10/10 verificações de qualidade aprovadas.`

---

## 7. KPIs Principais

| KPI | Definição | Fórmula DAX |
|-----|-----------|-------------|
| Faturamento | Receita total bruta | `SUM(fact_vendas[total_pedido])` |
| Total Pedidos | Número de pedidos distintos | `DISTINCTCOUNT(fact_vendas[pedido_id])` |
| Ticket Médio | Valor médio por pedido | `DIVIDE([Faturamento], [Total Pedidos], 0)` |
| Total Vendedores | Vendedores ativos | `DISTINCTCOUNT(fact_vendas[id_vendedor])` |

---

## 8. Estados e Regiões Cobertos

| Estado | Região |
|--------|--------|
| SP | Sudeste |
| RJ | Sudeste |
| MG | Sudeste |
| RS | Sul |
| PR | Sul |
| BA | Nordeste |
| PE | Nordeste |
| CE | Nordeste |
| AM | Norte |
| DF | Centro-Oeste |

---

## 9. Categorias de Produto

1. Smartphones
2. Notebooks
3. Acessórios
4. Áudio
5. Tablets
6. Monitores
7. Periféricos
8. Armazenamento

---

## 10. Vendedores (15)

| ID | Nome | Região |
|----|------|--------|
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

---

## 11. Dashboard — Páginas

| Página | Público | Conteúdo |
|--------|---------|----------|
| P1: Visão Executiva | Alta gestão | Cards KPI, faturamento por categoria, evolução temporal, top 5 produtos, rosca por região |
| P2: Vendedores | Gerência comercial | Ranking completo, barras, ticket médio, participação % |
| P3: Geográfica | Diretores regionais | Mapa, top 10 municípios, matriz região × categoria, barras por estado |

---

## 12. Documentação — Índice Rápido

| Documento | Conteúdo | Quando consultar |
|-----------|----------|-----------------|
| `HANDOFF.md` | Referência rápida (este arquivo) | Primeiro contato com o projeto |
| `data_dictionary.md` | Todas as colunas de todas as tabelas | Dúvidas sobre tipos, nomes de colunas, restrições |
| `technical_documentation.md` | Arquitetura, tecnologias, pipeline | Entendimento técnico aprofundado |
| `functional_documentation.md` | Regras de negócio, KPIs, dashboard | Entendimento do domínio de negócio |
| `presentation_script.md` | Roteiro de apresentação de 15 min | Preparação para apresentação acadêmica |
| `implementation_guide.md` | Passo a passo de instalação e execução | Setup do ambiente, solução de problemas |
| `test_plan.md` | Casos de teste e critérios de aceite | Execução e validação de testes |

---

## 13. Status do Projeto

| Item | Status |
|------|--------|
| Geração de dados sintéticos | ✅ Concluído |
| Validação de entradas | ✅ Concluído |
| Pipeline Bronze (ingestão) | ✅ Concluído |
| Pipeline Silver (transformação) | ✅ Concluído |
| Pipeline Gold (modelagem) | ✅ Concluído |
| Verificações de qualidade | ✅ Concluído |
| Dashboard Power BI | ✅ Concluído (3 páginas) |
| Documentação (7 arquivos) | ✅ Concluído |
| Noteboooks Jupyter | ✅ Concluído |
| Testes automatizados | ✅ Concluído |

---

## 14. Solução de Problemas Rápidos

| Erro | Solução |
|------|---------|
| `'java' is not recognized` | Instalar JDK 8 ou 11, configurar `JAVA_HOME` e `Path` |
| `No module named 'pyspark'` | Ativar venv (`.venv\Scripts\Activate.ps1`) e `pip install -r requirements.txt` |
| `No module named 'delta'` | `pip install delta-spark` |
| `winutils.exe not found` | No modo `local[*]`, este aviso pode ser ignorado para I/O básico |
| `OutOfMemoryError` | Reduzir `spark.driver.memory` para `1g` em `spark_config.py` |
| Power BI não lê Delta | Apontar "Obter Dados → Pasta" para o diretório da tabela, não para `_delta_log/` |
| Script de ativação bloqueado | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Versão incompatível delta-spark | Ver compatibilidade: PySpark 3.4 → delta-spark 3.0/3.1; PySpark 3.5 → delta-spark 3.1/3.2 |

---

*Documento gerado para o projeto BI E-Commerce — versão 1.0. Junho de 2026.*
