# Guia de Implementação — BI E-Commerce

Este documento fornece instruções detalhadas, passo a passo, para configurar o ambiente e executar o pipeline de dados do projeto BI E-Commerce, do zero à visualização no Power BI.

---

## 1. Pré-requisitos

### 1.1 Sistema Operacional

- Windows 10 ou Windows 11 (64-bit).
- O projeto pode ser adaptado para macOS ou Linux, mas este guia foca no ambiente Windows.

### 1.2 Java Development Kit (JDK)

O Apache Spark requer Java. Recomenda-se JDK 8 ou JDK 11.

**Verificação:**
```bash
java -version
```

**Saída esperada (exemplo):**
```
openjdk version "11.0.22" 2024-01-16 LTS
OpenJDK Runtime Environment (build 11.0.22+9)
OpenJDK 64-Bit Server VM (build 11.0.22+9, mixed mode)
```

**Instalação (caso não tenha):**
1. Acesse https://adoptium.net/ e faça o download do instalador do Temurin JDK 11 (Windows x64).
2. Execute o instalador e siga as instruções.
3. Configure a variável de ambiente `JAVA_HOME`:
   - Abra "Editar as variáveis de ambiente do sistema" no Windows.
   - Crie uma variável de sistema chamada `JAVA_HOME` apontando para o diretório de instalação. Exemplo: `C:\Program Files\Eclipse Adoptium\jdk-11.0.22.6-hotspot\`.
   - Adicione `%JAVA_HOME%\bin` à variável `Path`.
4. Reinicie o terminal e teste com `java -version`.

### 1.3 Python 3.10+

**Verificação:**
```bash
python --version
```

**Saída esperada:** `Python 3.10.x` ou `Python 3.11.x` ou `Python 3.12.x`.

**Instalação (caso não tenha):**
1. Acesse https://www.python.org/downloads/ e faça o download do instalador para Windows (64-bit).
2. Durante a instalação, marque a opção **"Add Python to PATH"**.
3. Conclua a instalação e reinicie o terminal.

### 1.4 Power BI Desktop

Necessário apenas para a etapa de visualização (opcional para execução do pipeline).

**Instalação:**
1. Acesse https://www.microsoft.com/pt-br/power-platform/products/power-bi/desktop.
2. Faça o download e execute o instalador.
3. Siga as instruções de instalação padrão.

### 1.5 Git (Opcional)

Para versionamento do código. Pode ser baixado em https://git-scm.com/.

---

## 2. Instalação do Projeto

### 2.1 Obter o Código-Fonte

**Opção A — Extrair de arquivo compactado:**
Extraia o conteúdo do projeto para `C:\dev\projetoInt\bi_ecommerce\`.

**Opção B — Clonar repositório Git (se disponível):**
```bash
git clone <url-do-repositorio> C:\dev\projetoInt\bi_ecommerce
```

### 2.2 Criar Ambiente Virtual Python

Abra o PowerShell como administrador e execute:

```powershell
Set-Location -LiteralPath "C:\dev\projetoInt\bi_ecommerce"
python -m venv venv
```

### 2.3 Ativar o Ambiente Virtual

No PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Se aparecer um erro de política de execução, execute primeiro:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

E então tente ativar novamente. Você saberá que o ambiente está ativo quando o prompt mostrar `(venv)` no início.

### 2.4 Instalar Dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

**Conteúdo esperado do `requirements.txt`:**
```
pyspark>=3.4.0,<4.0.0
delta-spark>=3.0.0
faker>=22.0.0
pandas>=2.0.0
```

**Tempo estimado:** 2 a 5 minutos, dependendo da velocidade da conexão. Os pacotes principais (pyspark) têm cerca de 300 MB.

---

## 3. Verificação do Ambiente

Antes de executar o pipeline, confirme que todos os componentes estão funcionando.

### 3.1 Verificar Java

```bash
java -version
```

Se o comando não for reconhecido, revise a instalação do JDK e a variável `JAVA_HOME`.

### 3.2 Verificar Python

```bash
python --version
```

### 3.3 Verificar PySpark

```bash
python -c "import pyspark; print('PySpark', pyspark.__version__)"
```

**Saída esperada:** `PySpark 3.4.x` ou `PySpark 3.5.x`.

### 3.4 Verificar Delta Lake

```bash
python -c "from delta import configure_spark_with_delta_pip; print('Delta Lake OK')"
```

**Saída esperada:** `Delta Lake OK`.

### 3.5 Verificar Faker

```bash
python -c "import faker; print('Faker', faker.__version__)"
```

**Saída esperada:** `Faker 22.x.x` ou superior.

---

## 4. Execução do Pipeline

### 4.1 Estrutura Antes da Execução

Inicialmente, apenas o diretório `src/` e `docs/` contêm arquivos. Execute o pipeline na ordem correta.

### 4.2 Opção A — Script Orquestrador (Recomendado)

Este comando executa todo o pipeline de uma vez:

```bash
python src/run_pipeline.py
```

O orquestrador executa cada script na sequência e interrompe se algum falhar.

**Tempo estimado de execução completa:** 3 a 8 minutos, dependendo do hardware.

**Saída esperada no console:**
```
============================================================
BI E-COMMERCE - PIPELINE DE DADOS
============================================================

[1/6] Gerando dados sintéticos...
  OK - Dados gerados com sucesso.

[2/6] Validando arquivos de entrada...
  OK - Validações aprovadas.

[3/6] Executando ingestão Bronze...
  OK - Camada Bronze criada.

[4/6] Executando transformação Silver...
  OK - Camada Silver criada.

[5/6] Executando modelagem Gold...
  OK - Star Schema criado.

[6/6] Executando verificações de qualidade...
  OK - Todas as verificações passaram.

============================================================
PIPELINE CONCLUÍDO COM SUCESSO
============================================================
```

### 4.3 Opção B — Execução Passo a Passo

Caso prefira executar cada etapa individualmente (útil para depuração):

```bash
python src/00_generate_data.py
```

**Saída esperada:** `[OK] 1500 clientes, 250 produtos, 8000 pedidos gerados em data/source/`

```bash
python src/01_validate_inputs.py
```

**Saída esperada:** `[OK] Validação concluída. 0 erros encontrados.`

```bash
python src/10_bronze_ingestion.py
```

**Saída esperada:** `[OK] Bronze: 3 tabelas Delta criadas em data/bronze/`

```bash
python src/20_silver_transform.py
```

**Saída esperada:** `[OK] Silver: 3 tabelas Delta criadas em data/silver/`

```bash
python src/30_gold_model.py
```

**Saída esperada:** `[OK] Gold: 5 tabelas Delta criadas em data/gold/`

```bash
python src/40_quality_checks.py
```

**Saída esperada:** `[OK] 10/10 verificações de qualidade aprovadas.`

---

## 5. Execução dos Notebooks (Opcional)

Os Jupyter Notebooks oferecem uma interface interativa para exploração dos dados.

### 5.1 Instalar Jupyter

```bash
pip install jupyter
```

### 5.2 Iniciar o Servidor

```bash
jupyter notebook
```

O navegador abrirá automaticamente. Navegue até a pasta `notebooks/` e abra os arquivos `.ipynb`. Execute as células sequencialmente.

**Notebooks disponíveis:**
- `00_exploracao_dados.ipynb` — visualização rápida dos dados gerados com pandas e gráficos.
- `01_validacao_quality.ipynb` — execução interativa das verificações de qualidade.
- `02_insights_preliminares.ipynb` — consultas analíticas com Spark SQL.

---

## 6. Conexão com Power BI

### 6.1 Abrir Power BI Desktop

Inicie o Power BI Desktop. Na tela inicial, selecione **"Obter Dados"**.

### 6.2 Importar as Tabelas

Para cada tabela da camada Gold, siga este procedimento:

1. **Obter Dados → Mais... → Pasta** (ou "Folder").
2. Clique em **Conectar**.
3. Navegue até o diretório da tabela. Exemplo: `C:\dev\projetoInt\bi_ecommerce\data\gold\dim_clientes\`.
4. Clique em **OK**.
5. Na janela de visualização, clique em **Combinar e Transformar Dados** (ou "Combine & Transform Data").
6. O Power Query será aberto. Verifique se todas as colunas e tipos estão corretos.
7. Clique em **Fechar e Aplicar**.

Repita o processo para cada uma das 5 tabelas:

| Tabela no Power BI | Caminho da pasta |
|--------------------|------------------|
| dim_clientes | `data/gold/dim_clientes/` |
| dim_produtos | `data/gold/dim_produtos/` |
| dim_calendario | `data/gold/dim_calendario/` |
| dim_vendedores | `data/gold/dim_vendedores/` |
| fact_vendas | `data/gold/fact_vendas/` |

**Alternativa mais rápida:** Todas as tabelas estão no mesmo diretório pai `data/gold/`. Você pode usar **Obter Dados → Pasta** no diretório `data/gold/` e selecionar todas as subpastas de uma vez, usando a opção de combinação do Power Query.

### 6.3 Configurar Relacionamentos

Após importar todas as tabelas, o Power BI pode detectar automaticamente alguns relacionamentos. Verifique e ajuste conforme necessário na aba **Modelo** (ícone de diagrama à esquerda):

| De (Dimensão) | Coluna | Para (Fato) | Coluna | Cardinalidade | Direção do Filtro |
|---------------|--------|-------------|--------|---------------|-------------------|
| dim_clientes | id_cliente | fact_vendas | id_cliente | Um para Muitos (1:N) | Única |
| dim_produtos | id_produto | fact_vendas | id_produto | Um para Muitos (1:N) | Única |
| dim_calendario | data | fact_vendas | data_pedido | Um para Muitos (1:N) | Única |
| dim_vendedores | id_vendedor | fact_vendas | id_vendedor | Um para Muitos (1:N) | Única |

**Como criar um relacionamento:**
1. Arraste a coluna da tabela dimensão para a coluna correspondente na tabela fato.
2. Na janela que se abre, confirme a cardinalidade e a direção do filtro.
3. Clique em **OK**.

**Importante:** A direção do filtro deve ser **Única** (Single), partindo da dimensão para a fato. Isso garante o comportamento esperado de filtragem.

### 6.4 Importar Medidas DAX

Abra o arquivo `powerbi/dax_measures.txt`. Para cada medida listada:

1. No Power BI, selecione a tabela `fact_vendas` (ou crie uma tabela de medidas separada).
2. Clique com o botão direito → **Nova Medida**.
3. Cole a fórmula DAX correspondente.
4. Pressione Enter para confirmar.

**Medidas essenciais a serem criadas:**

```dax
Faturamento = SUM(fact_vendas[total_pedido])

Total Pedidos = DISTINCTCOUNT(fact_vendas[pedido_id])

Ticket Médio = DIVIDE([Faturamento], [Total Pedidos], 0)

Total Vendedores = DISTINCTCOUNT(fact_vendas[id_vendedor])

Volume de Itens = SUM(fact_vendas[quantidade])
```

### 6.5 Marcar Tabelas de Dimensão

Para que o Power BI otimize as consultas:

1. Na aba **Modelo**, selecione cada tabela de dimensão.
2. No painel de propriedades, marque a opção **"Tabela de Dimensão"** (ou configure "Is Dimension Table").
3. Para `fact_vendas`, marque **"Tabela de Fatos"**.

### 6.6 Ocultar Colunas Desnecessárias

Oculte as chaves estrangeiras na tabela fato para evitar confusão no painel de campos:
- Em `fact_vendas`, clique com o botão direito em `id_cliente`, `id_produto`, `data_pedido`, `id_vendedor` e selecione **"Ocultar"**.

---

## 7. Dashboard Setup

### 7.1 Tema e Cores

1. Na aba **Exibição**, selecione o tema escuro ou configure manualmente:
   - Plano de fundo da página: `#262626` (cinza escuro)
   - Plano de fundo dos visuais: `#333333` (cinza médio)
   - Cor da fonte: `#FFFFFF` (branco)
   - Cor de destaque para KPIs: `#4CAF50` (verde) ou `#FF9800` (laranja)

2. Ajuste o tamanho da página para **16:9** (padrão para apresentações).

### 7.2 Construir Visuais da Página 1 (Visão Executiva)

**Cards de KPI:**
- Insira 4 cartões (visual "Cartão").
- Configure cada um com uma medida: Faturamento, Total Pedidos, Ticket Médio, Total Vendedores.
- Formate como moeda (R$) para valores monetários.

**Gráfico de Barras — Categorias:**
- Eixo: `dim_produtos[categoria]`
- Valores: `[Faturamento]`
- Ordenação: decrescente por faturamento

**Gráfico de Área — Evolução Temporal:**
- Eixo: `dim_calendario[data]` (configure hierarquia: Ano → Trimestre → Mês → Dia)
- Valores: `[Faturamento]`

**Top 5 Produtos (Tabela):**
- Colunas: `dim_produtos[nome_produto]`, `dim_produtos[categoria]`, `[Faturamento]`
- Filtro de Top N: 5 maiores por faturamento

**Gráfico de Rosca — Regiões:**
- Legenda: `fact_vendas[regiao]`
- Valores: `[Faturamento]`

### 7.3 Construir Visuais da Página 2 (Vendedores)

**Ranking de Vendedores (Tabela):**
- Colunas: `dim_vendedores[nome]`, `dim_vendedores[regiao]`, `[Faturamento]`, `[Total Pedidos]`, `[Ticket Médio]`
- Ordenação: decrescente por `[Faturamento]`

**Barras Horizontais — Vendedores:**
- Eixo: `dim_vendedores[nome]`
- Valores: `[Faturamento]`

**Participação Percentual:**
- Criar medida DAX adicional:
  ```dax
  Participação % = DIVIDE([Faturamento], CALCULATE([Faturamento], ALL(dim_vendedores)), 0) * 100
  ```

### 7.4 Construir Visuais da Página 3 (Geográfica)

**Mapa:**
- Localização: `fact_vendas[estado]` (configurar como campo de estado/UF)
- Tamanho da bolha ou intensidade de cor: `[Faturamento]`

**Top 10 Municípios:**
- Eixo: `fact_vendas[municipio]`
- Valores: `[Faturamento]`
- Filtro de Top N: 10

**Matriz Região × Categoria:**
- Linhas: `fact_vendas[regiao]`
- Colunas: `dim_produtos[categoria]`
- Valores: `[Faturamento]`

### 7.5 Adicionar Slicers (Filtros)

Insira segmentações de dados (_slicers_) para os seguintes campos (podem ser sincronizados entre páginas):
- `dim_calendario[ano]`
- `dim_calendario[nome_mes]`
- `fact_vendas[regiao]`
- `fact_vendas[estado]`
- `dim_produtos[categoria]`
- `dim_vendedores[nome]`

---

## 8. Solução de Problemas

### 8.1 "java" não é reconhecido como comando

**Causa:** Java não está instalado ou `JAVA_HOME` não está configurado.

**Solução:**
1. Instale o JDK (ver seção 1.2).
2. Configure `JAVA_HOME` e adicione `%JAVA_HOME%\bin` ao `Path`.
3. Reinicie o terminal e teste com `java -version`.

### 8.2 "delta-spark" module not found

**Causa:** O pacote `delta-spark` não foi instalado ou a versão é incompatível com o PySpark.

**Solução:**
```bash
pip uninstall delta-spark -y
pip install delta-spark==3.1.0
```

Confirme que a versão do `delta-spark` é compatível com a versão do PySpark:
- PySpark 3.4.x → delta-spark 3.0.x ou 3.1.x
- PySpark 3.5.x → delta-spark 3.1.x ou 3.2.x

### 8.3 Erro "winutils.exe not found"

**Causa:** O Spark em modo Windows procura um binário Hadoop auxiliar.

**Solução para este projeto:** No modo local (`local[*]`), o PySpark consegue ler e escrever arquivos Delta sem o `winutils.exe` para operações básicas de I/O. Este aviso pode ser ignorado. Caso o erro seja bloqueante:

1. Baixe `winutils.exe` de https://github.com/steveloughran/winutils
2. Coloque em `C:\hadoop\bin\`
3. Configure `HADOOP_HOME=C:\hadoop`

### 8.4 "Python not found" ou import errors

**Causa:** Ambiente virtual não está ativado ou pacotes não instalados.

**Solução:**
```powershell
Set-Location -LiteralPath "C:\dev\projetoInt\bi_ecommerce"
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 8.5 "No module named 'pyspark'"

**Causa:** PySpark não foi instalado ou ambiente virtual não está ativo.

**Solução:** Confirme que o prompt mostra `(venv)`. Execute `pip list | Select-String pyspark`. Se não aparecer, execute `pip install pyspark`.

### 8.6 Delta Lake version mismatch

**Solução:** Verifique a compatibilidade:
```bash
python -c "import pyspark; print(pyspark.__version__)"
python -c "import delta; print(delta.__version__)"
```

Se houver incompatibilidade, desinstale e reinstale com versões compatíveis.

### 8.7 Erro de política de execução no PowerShell

**Erro:** `... cannot be loaded because running scripts is disabled on this system.`

**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8.8 SparkSession não inicia

**Causa:** Conflito de versão Java ou variável de ambiente incorreta.

**Solução:**
1. Confirme `java -version` retorna algo.
2. Confirme `$env:JAVA_HOME` aponta para um diretório válido.
3. Teste: `python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.master('local[1]').appName('test').getOrCreate(); print(spark.version); spark.stop()"`

### 8.9 Power BI não reconhece arquivos Delta/Parquet

**Causa:** Power BI precisa acessar os arquivos Parquet dentro das pastas Delta.

**Solução:** Ao usar "Obter Dados → Pasta", navegue até o diretório da tabela Delta (ex.: `data/gold/dim_clientes/`). O Power BI lerá os arquivos `.parquet` dentro dessa pasta. Não aponte para o diretório `_delta_log/`.

### 8.10 Memória insuficiente (OutOfMemoryError)

**Causa:** O Spark pode consumir mais memória do que o disponível.

**Solução:** No script de configuração (`spark_config.py`), limite a memória do driver:
```python
.config("spark.driver.memory", "2g")
```

Para este projeto, com apenas 8.000 registros, o consumo de memória é baixo e este erro é improvável.

---

## 9. Estrutura de Pastas Após Execução

Após executar o pipeline completo, a estrutura de diretórios será:

```
C:\dev\projetoInt\bi_ecommerce\
│
├── data/
│   ├── source/
│   │   ├── clientes.csv          (~150 KB)
│   │   ├── produtos.csv          (~25 KB)
│   │   └── pedidos.csv           (~800 KB)
│   │
│   ├── bronze/
│   │   ├── bronze_clientes/      (Delta, ~150 KB)
│   │   │   ├── regiao=Nordeste/
│   │   │   ├── regiao=Norte/
│   │   │   ├── regiao=Sudeste/
│   │   │   ├── regiao=Sul/
│   │   │   ├── regiao=Centro-Oeste/
│   │   │   └── _delta_log/
│   │   ├── bronze_produtos/      (Delta, ~25 KB)
│   │   └── bronze_pedidos/       (Delta, ~800 KB)
│   │       ├── regiao=Nordeste/
│   │       ├── regiao=.../
│   │       └── _delta_log/
│   │
│   ├── silver/
│   │   ├── silver_clientes/      (Delta, ~150 KB)
│   │   ├── silver_produtos/      (Delta, ~30 KB)
│   │   └── silver_pedidos/       (Delta, ~1 MB)
│   │
│   └── gold/
│       ├── dim_clientes/         (Delta, ~100 KB)
│       ├── dim_produtos/         (Delta, ~20 KB)
│       ├── dim_calendario/       (Delta, ~50 KB)
│       ├── dim_vendedores/       (Delta, ~1 KB)
│       └── fact_vendas/          (Delta, ~900 KB)
│
├── src/
│   ├── 00_generate_data.py
│   ├── 01_validate_inputs.py
│   ├── 10_bronze_ingestion.py
│   ├── 20_silver_transform.py
│   ├── 30_gold_model.py
│   ├── 40_quality_checks.py
│   ├── run_pipeline.py
│   └── spark_config.py
│
├── notebooks/
│   ├── 00_exploracao_dados.ipynb
│   ├── 01_validacao_quality.ipynb
│   └── 02_insights_preliminares.ipynb
│
├── powerbi/
│   ├── bi_ecommerce.pbix
│   ├── dax_measures.txt
│   └── dashboard_spec.txt
│
├── docs/
│   ├── data_dictionary.md
│   ├── technical_documentation.md
│   ├── functional_documentation.md
│   ├── presentation_script.md
│   ├── implementation_guide.md
│   ├── test_plan.md
│   └── HANDOFF.md
│
├── tests/
│   └── test_pipeline.py
│
├── venv/                         (ambiente virtual Python)
├── requirements.txt
├── README.md
└── .gitignore
```

### 9.1 Verificação Rápida

Para confirmar que os dados foram gerados corretamente, liste o conteúdo de `data/gold/`:

```bash
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

Para verificar o conteúdo de cada tabela rapidamente, use o Spark shell:

```bash
python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.master('local[*]').config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension').config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog').getOrCreate(); df = spark.read.format('delta').load('data/gold/fact_vendas'); df.printSchema(); df.show(5, False); spark.stop()"
```

---

## 10. Limpeza e Reexecução

Para limpar todos os dados gerados e reexecutar do zero:

```bash
Remove-Item -Recurse -Force -LiteralPath "data\source"
Remove-Item -Recurse -Force -LiteralPath "data\bronze"
Remove-Item -Recurse -Force -LiteralPath "data\silver"
Remove-Item -Recurse -Force -LiteralPath "data\gold"
python src/run_pipeline.py
```

Alternativamente, o próprio pipeline usa `mode("overwrite")`, então reexecutar o `run_pipeline.py` já sobrescreve os dados existentes. A limpeza manual só é necessária se houver corrupção nos arquivos Delta ou mudança de schema.

---

*Documento gerado para o projeto BI E-Commerce — versão 1.0. Junho de 2026.*
