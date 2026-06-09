# Documentação Funcional — BI E-Commerce (Solução de Business Intelligence)

## 1. Introdução

O projeto **BI E-Commerce** foi concebido para atender às necessidades analíticas de uma empresa fictícia do setor de comércio eletrônico de eletrônicos. A empresa opera nacionalmente, comercializando produtos de tecnologia como smartphones, notebooks, tablets, acessórios, equipamentos de áudio, monitores, periféricos e dispositivos de armazenamento, por meio de uma equipe de 15 vendedores distribuídos pelas cinco regiões do Brasil.

Atualmente, a empresa dispõe de dados transacionais armazenados em planilhas e sistemas departamentais desconectados. Extrair informações gerenciais desses dados exige esforço manual, está sujeito a erros e não oferece agilidade para a tomada de decisão. Os gestores enfrentam dificuldades para responder perguntas fundamentais como: _Qual foi o faturamento do último trimestre?_, _Quais vendedores tiveram melhor desempenho?_, _Que regiões apresentam maior ticket médio?_ ou _Quais categorias de produto geram mais receita?_

A solução de Business Intelligence proposta neste projeto endereça esses desafios ao implementar um pipeline de dados completo, desde a ingestão de dados brutos até a disponibilização de um dashboard interativo no Power BI, permitindo que decisões estratégicas sejam baseadas em dados confiáveis, consistentes e atualizados.

---

## 2. Objetivos de Negócio

A implementação desta solução de BI visa instrumentalizar os seguintes processos decisórios:

1. **Acompanhamento de performance financeira:** Visualizar o faturamento total da empresa, com capacidade de detalhamento por período (dia, mês, trimestre, ano), região, estado, categoria de produto e vendedor. Identificar tendências de crescimento ou retração ao longo do tempo.

2. **Gestão da força de vendas:** Avaliar o desempenho individual de cada um dos 15 vendedores, com métricas comparativas que permitam identificar _top performers_, calcular comissões com base em resultados, e direcionar ações de capacitação para vendedores com desempenho abaixo da média.

3. **Inteligência geográfica de mercado:** Compreender a distribuição das vendas pelo território nacional, identificando regiões e estados de maior e menor penetração, subsidiando decisões de expansão comercial e alocação de investimentos de marketing regionalizados.

4. **Gestão de portfólio de produtos:** Analisar a contribuição de cada categoria e produto para o faturamento, identificando itens de alto giro, produtos com baixa performance, e subsidiando decisões de sortimento, precificação e campanhas promocionais.

5. **Análise de ticket médio:** Monitorar o valor médio gasto por pedido, correlacionando com variáveis como região, categoria de produto e vendedor, para identificar oportunidades de _upsell_ e _cross-sell_.

---

## 3. Fontes de Dados

A solução trabalha com três fontes de dados sintéticos, modeladas para representar sistemas transacionais típicos de uma operação de e-commerce brasileira.

### 3.1 Base de Clientes

A tabela de clientes representa o cadastro de consumidores da plataforma. Cada cliente é identificado unicamente e possui informações de contato e localização. Do ponto de vista de negócio, esta tabela responde à pergunta _"quem comprou?"_. A localização geográfica (cidade, estado, região) permite segmentar análises por perfil regional do consumidor, enquanto a data de cadastro possibilita análises de fidelização e _cohort analysis_ (clientes antigos vs. novos).

**Volume:** 1.500 clientes cadastrados, distribuídos pelas cinco regiões brasileiras.

### 3.2 Base de Produtos

A tabela de produtos representa o catálogo de eletrônicos disponível para venda. Contém 250 itens organizados em 8 categorias e respectivas subcategorias, com informações de preço de venda (quanto o cliente paga), preço de custo (quanto a empresa paga ao fornecedor) e estoque disponível. Do ponto de vista de negócio, responde à pergunta _"o que foi vendido?"_. As informações de margem (preço de venda menos custo) são fundamentais para análises de rentabilidade por produto e categoria.

**Volume:** 250 produtos ativos no catálogo.

### 3.3 Base de Pedidos

A tabela de pedidos é a principal fonte transacional, registrando cada venda realizada. Cada registro vincula um cliente (quem comprou) a um produto (o que comprou), em uma data específica (quando comprou), por meio de um vendedor (quem vendeu), para entrega em um município (onde será entregue). As medidas transacionais incluem a quantidade de itens e o valor do frete cobrado. O valor total do pedido é calculado via enriquecimento na camada Silver (quantidade × preço do produto + frete) e representa a receita gerada por aquela transação.

**Volume:** 8.000 pedidos ao longo de aproximadamente 24 meses de operação.

---

## 4. Regras de Negócio Aplicadas

As regras de negócio foram implementadas como transformações na camada Silver do pipeline Medallion. Cada regra reflete uma necessidade real de qualidade de dados em ambientes corporativos.

### 4.1 Padronização de Dados Cadastrais (Clientes)

**Problema de negócio:** Dados cadastrais frequentemente apresentam inconsistências de formatação, como nomes digitados em minúsculas ou caixa alta, estados em formatos variados ("sp", "SP", "Sp"), e e-mails com capitalização irregular. Essas inconsistências comprometem a qualidade de relatórios, agrupamentos e comunicações com clientes.

**Regra aplicada:**
- **Nomes de clientes:** Convertidos para Title Case (primeira letra de cada palavra em maiúscula, demais em minúscula). Exemplo: `"ana beatriz silva"` → `"Ana Beatriz Silva"`. No Power BI, isso garante que nomes sejam exibidos de forma profissional e padronizada.
- **Cidades:** Convertidas para Title Case. Exemplo: `"são paulo"` → `"São Paulo"`.
- **Siglas de estado:** Convertidas para caixa alta (UPPER). Exemplo: `"sp"` → `"SP"`. Garante que agrupamentos e filtros por estado funcionem corretamente independentemente da formatação original.
- **E-mails:** Convertidos para minúsculas (lowercase). Exemplo: `"Ana.Silva@Email.com"` → `"ana.silva@email.com"`. Segue convenção padrão da internet e evita duplicatas por diferença de capitalização.

### 4.2 Validação de Dados de Produto

**Problema de negócio:** Produtos com preço de venda zerado ou negativo distorcem análises de faturamento e ticket médio. SKUs duplicados causam ambiguidade na identificação de produtos. Preço de custo zerado inviabiliza o cálculo de margem e rentabilidade.

**Regra aplicada:**
- **Preço de venda válido:** Apenas produtos com `preco_venda > 0` são mantidos. Produtos com preço zero ou negativo são removidos do pipeline.
- **Preço de custo válido:** Apenas produtos com `preco_custo > 0` são mantidos.
- **Estoque não negativo:** Apenas produtos com `estoque >= 0` são mantidos.
- **SKU único:** A unicidade do SKU é garantida via deduplicação. Em caso de duplicatas, a primeira ocorrência é mantida.
- **Margem calculada:** A margem bruta (`preco_venda - preco_custo`) e o percentual de margem (`margem / preco_venda × 100`) são calculados para análises de rentabilidade.

### 4.3 Enriquecimento de Pedidos

**Problema de negócio:** Os dados transacionais brutos não contêm o valor total do pedido, apenas a quantidade e o valor do frete. O preço unitário do produto reside na tabela de produtos. Para análises financeiras, é necessário consolidar essas informações em um único valor monetário por pedido.

**Regra aplicada:**
- **Cálculo do total do pedido:** `total_pedido = (quantidade × preco_venda) + valor_frete`. O preço de venda é obtido via JOIN com a tabela de produtos Silver.
- **Validação do total:** Apenas pedidos com `total_pedido > 0` são mantidos.
- **Integridade do JOIN:** Pedidos cujo SKU não encontra correspondência na tabela de produtos são removidos (pedidos órfãos).

### 4.4 Classificação Regional

**Problema de negócio:** A empresa precisa analisar desempenho por região geográfica (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) para decisões estratégicas regionais. A classificação regional deve ser consistente com a divisão oficial do IBGE.

**Regra aplicada:**
- A coluna `regiao` é padronizada em Title Case em todas as tabelas.
- Estados são mapeados para regiões conforme a divisão oficial brasileira:
  - **Norte:** AM
  - **Nordeste:** BA, PE, CE
  - **Centro-Oeste:** DF
  - **Sudeste:** SP, RJ, MG
  - **Sul:** RS, PR

### 4.5 Validação de Datas

**Problema de negócio:** Datas inválidas ou em formato incorreto quebram séries temporais e gráficos de evolução.

**Regra aplicada:**
- Conversão explícita da coluna `data_pedido` e `data_cadastro` para o tipo `DATE`.
- Verificação de que as datas estão dentro do intervalo esperado (2024-01-01 a 2025-12-31).

### 4.6 Controle de Duplicatas

**Problema de negócio:** Registros duplicados inflam métricas de contagem e faturamento, levando a decisões baseadas em informações incorretas.

**Regra aplicada:**
- `cliente_id` deduplicado na tabela de clientes.
- `sku` deduplicado na tabela de produtos.
- `pedido_id` deduplicado na tabela de pedidos.

---

## 5. Dimensões de Análise

O modelo dimensional Star Schema foi projetado para responder às perguntas de negócio por meio de quatro dimensões de análise. Cada dimensão representa um eixo analítico independente.

### 5.1 Dimensão Cliente (dim_clientes) — "Quem comprou?"

Permite analisar as vendas sob a ótica do consumidor. Questões respondidas:
- Quais clientes geraram maior faturamento?
- Qual o perfil geográfico dos clientes que mais compram?
- Como o ticket médio varia entre diferentes cidades e regiões?
- Quais regiões concentram a maior base de clientes?

**Atributos disponíveis:** nome do cliente, cidade, estado, região.

### 5.2 Dimensão Produto (dim_produtos) — "O que foi vendido?"

Permite analisar as vendas sob a ótica do portfólio de produtos. Questões respondidas:
- Quais categorias de produto geram mais receita?
- Qual o preço médio de venda por categoria?
- Existem categorias com alto volume de pedidos mas baixo ticket médio?
- Quais produtos individuais são _best-sellers_?

**Atributos disponíveis:** nome do produto, categoria, preço de venda.

**Categorias (8):** Smartphones, Notebooks, Acessórios, Áudio, Tablets, Monitores, Periféricos, Armazenamento.

### 5.3 Dimensão Calendário (dim_calendario) — "Quando foi vendido?"

Permite analisar as vendas em perspectiva temporal com múltiplos níveis de granularidade. Questões respondidas:
- Qual o faturamento por mês e por trimestre?
- Há sazonalidade nas vendas (ex.: picos em novembro/dezembro)?
- Qual a evolução do ticket médio ao longo do tempo?
- Como o desempenho atual se compara ao mesmo período do ano anterior?

**Atributos disponíveis:** data, dia do mês, nome do mês por extenso, nome do mês abreviado, número do mês, trimestre, ano.

**Hierarquia temporal:** Ano → Trimestre → Mês → Dia.

### 5.4 Dimensão Vendedor (dim_vendedores) — "Quem vendeu?"

Permite analisar as vendas sob a ótica da força de vendas. Questões respondidas:
- Quem são os 3 melhores vendedores por faturamento?
- Qual o ticket médio praticado por cada vendedor?
- Existem vendedores com performance abaixo da média em alguma região?
- Qual a participação percentual de cada vendedor no faturamento total?

**Atributos disponíveis:** nome do vendedor, região de atuação.

**Total de vendedores:** 15, distribuídos pelas 5 regiões.

---

## 6. Métricas e KPIs

As métricas e indicadores-chave de desempenho (KPIs) são calculados via medidas DAX no Power BI e representam os principais números que a gestão da empresa precisa acompanhar.

### 6.1 Faturamento

**Definição:** Soma do valor total de todos os pedidos em um determinado período.

**Fórmula DAX:**
```dax
Faturamento = SUM(fact_vendas[total_pedido])
```

**Fórmula SQL equivalente:** `SELECT SUM(total_pedido) FROM fact_vendas`

**Interpretação de negócio:** Representa a receita bruta total da empresa, incluindo o valor dos produtos vendidos e o frete cobrado. É o principal indicador financeiro e a métrica de topo do dashboard. Permite avaliar se a empresa está crescendo, estagnada ou em declínio. Deve ser sempre analisado em conjunto com o Total de Pedidos para contextualizar se o aumento de faturamento decorre de mais vendas ou de vendas de maior valor.

**Unidade:** R$ (reais)

### 6.2 Total de Pedidos

**Definição:** Contagem distinta de pedidos realizados em um determinado período. Cada pedido é identificado unicamente por `pedido_id`.

**Fórmula DAX:**
```dax
Total Pedidos = DISTINCTCOUNT(fact_vendas[pedido_id])
```

**Fórmula SQL equivalente:** `SELECT COUNT(DISTINCT pedido_id) FROM fact_vendas`

**Interpretação de negócio:** Representa o volume de transações da empresa. É uma métrica de atividade comercial. Um aumento no Total de Pedidos sem aumento proporcional no Faturamento pode indicar que os clientes estão comprando produtos mais baratos ou em menor quantidade. Inversamente, Faturamento crescendo mais rápido que o Total de Pedidos sugere aumento no ticket médio.

**Unidade:** número inteiro (contagem)

### 6.3 Ticket Médio

**Definição:** Valor médio gasto por pedido. Calculado como a razão entre o faturamento total e o número total de pedidos.

**Fórmula DAX:**
```dax
Ticket Médio = DIVIDE([Faturamento], [Total Pedidos], 0)
```

**Fórmula SQL equivalente:** `SELECT SUM(total_pedido) / COUNT(DISTINCT pedido_id) FROM fact_vendas`

**Interpretação de negócio:** Indica o valor médio que cada cliente gasta em uma compra. É uma métrica de eficiência comercial e potencial de receita. Um ticket médio elevado pode indicar sucesso em estratégias de _upsell_ (venda de produtos mais caros) ou _cross-sell_ (venda de produtos complementares). Segmentar o ticket médio por região, categoria de produto ou vendedor revela oportunidades de melhoria direcionadas. Por exemplo, se uma região tem ticket médio consistentemente inferior às demais, pode-se investigar se o mix de produtos ofertados é adequado ou se há oportunidade para campanhas promocionais de produtos premium.

**Unidade:** R$ (reais)

### 6.4 Total de Vendedores

**Definição:** Contagem distinta de vendedores ativos. Neste projeto, o valor é fixo em 15 vendedores, mas a métrica é incluída como verificação de integridade.

**Fórmula DAX:**
```dax
Total Vendedores = DISTINCTCOUNT(fact_vendas[id_vendedor])
```

**Interpretação de negócio:** Confirma que todos os 15 vendedores estão representados nos dados. Em um ambiente real, esta métrica poderia ser segmentada para identificar vendedores inativos ou sem vendas em determinado período.

### 6.5 Métricas Complementares

Além dos KPI principais, o dashboard oferece métricas derivadas que enriquecem a análise:

- **Volume de Itens:** `SUM(fact_vendas[quantidade])` — quantidade total de unidades vendidas. Complementa o Total de Pedidos distinguindo pedidos de 1 item de pedidos com múltiplas unidades.
- **Faturamento por Categoria:** `SUM(fact_vendas[total_pedido])` filtrado por categoria de produto.
- **Faturamento por Região:** `SUM(fact_vendas[total_pedido])` filtrado por região geográfica.
- **Ranking de Vendedores:** Ordenação decrescente de vendedores por faturamento.
- **Participação % do Vendedor:** `DIVIDE([Faturamento do Vendedor], [Faturamento Total], 0) * 100`.
- **Variação Mensal (MoM):** `([Faturamento Mês Atual] - [Faturamento Mês Anterior]) / [Faturamento Mês Anterior]`.
- **Variação Anual (YoY):** `([Faturamento Ano Atual] - [Faturamento Ano Anterior]) / [Faturamento Ano Anterior]`.

---

## 7. Visuais do Dashboard

O dashboard Power BI é composto por três páginas temáticas, cada uma atendendo a um perfil de usuário e conjunto de perguntas de negócio.

### 7.1 Página 1 — Visão Executiva

**Objetivo:** Fornecer uma visão consolidada e imediata da saúde do negócio. Destinada a diretores e alta gestão.

**Visuais:**

1. **Cards de KPI (topo da página):** Quatro cartões exibindo os valores principais:
   - **Faturamento Total** — valor monetário formatado em R$, com destaque visual (fonte grande, cor de destaque).
   - **Total de Pedidos** — valor inteiro, formatado com separador de milhar.
   - **Ticket Médio** — valor monetário, com indicador de tendência se disponível.
   - **Total de Vendedores** — valor inteiro (15).

2. **Gráfico de Barras — Faturamento por Categoria (centro-esquerda):** Barras horizontais ou verticais mostrando o faturamento para cada uma das 8 categorias de produto. Permite identificar rapidamente quais categorias são as principais geradoras de receita. Eixo X: categoria; Eixo Y: faturamento.

3. **Gráfico de Área — Faturamento ao Longo do Tempo (centro-direita):** Gráfico de área mostrando a evolução mensal do faturamento ao longo dos meses cobertos pelos dados. O preenchimento de área facilita a visualização de tendências e sazonalidades. Eixo X: mês/ano; Eixo Y: faturamento.

4. **Tabela — Top 5 Produtos (rodapé esquerdo):** Tabela ranqueando os 5 produtos com maior faturamento, exibindo nome do produto, categoria e faturamento.

5. **Gráfico de Rosca — Faturamento por Região (rodapé direito):** Gráfico de rosca (donut) mostrando a participação percentual de cada região no faturamento total.

**Interações:** Todos os visuais são interativos. Ao selecionar uma categoria no gráfico de barras, os demais visuais são filtrados automaticamente (cross-filtering).

### 7.2 Página 2 — Análise de Vendedores

**Objetivo:** Fornecer análise detalhada do desempenho da força de vendas. Destinada a gerentes comerciais.

**Visuais:**

1. **Tabela — Ranking de Vendedores (centro):** Tabela completa com os 15 vendedores, ordenada por faturamento (decrescente). Colunas: posição no ranking, nome do vendedor, região, faturamento, total de pedidos, ticket médio, participação percentual.

2. **Gráfico de Barras — Faturamento por Vendedor (topo):** Gráfico de barras horizontais com um vendedor por barra, ordenado por faturamento. Visualização intuitiva de _top performers_ e distribuição de performance.

3. **Gráfico de Barras Empilhadas — Vendedores por Região (esquerda):** Mostra a contribuição de cada vendedor para o faturamento de sua região. Permite comparar vendedores dentro da mesma região.

4. **Indicador (Gauge) — Ticket Médio por Vendedor (direita):** _Multi-row card_ ou tabela resumida comparando ticket médio entre os vendedores. Destaca vendedores com ticket médio acima e abaixo da média geral.

**Segmentação de dados:** Filtros por região, período (ano/mês) e categoria de produto afetam todos os visuais desta página.

### 7.3 Página 3 — Análise Geográfica

**Objetivo:** Fornecer visão territorial das vendas. Destinada a diretores regionais e equipe de expansão.

**Visuais:**

1. **Mapa Coroplético — Faturamento por Estado (centro):** Mapa do Brasil com estados coloridos por intensidade de faturamento. Estados com maior faturamento aparecem em tons mais escuros, facilitando a identificação de concentração geográfica. (Nota: disponível no Power BI com o visual de mapa padrão, utilizando os 10 estados cobertos.)

2. **Gráfico de Barras — Top 10 Municípios (esquerda):** Ranking dos 10 municípios com maior faturamento. Revela concentração urbana das vendas.

3. **Gráfico de Barras — Faturamento por Estado (direita):** Barras horizontais para cada um dos 10 estados cobertos (SP, RJ, MG, RS, PR, BA, PE, CE, AM, DF).

4. **Tabela Cruzada — Região × Categoria (rodapé):** Matriz mostrando a intersecção de faturamento entre as 5 regiões e as 8 categorias de produto. Revela preferências regionais por tipo de produto.

5. **Segmentação — Seletor de Região (topo):** Filtro _slicer_ permitindo selecionar uma ou mais regiões para análise focada.

---

## 8. Filtros e Segmentações

O dashboard oferece as seguintes segmentações (filtros interativos) disponíveis em todas as páginas:

| Segmentação | Tipo | Descrição |
|-------------|------|-----------|
| Período (Ano) | Slicer — lista | Permite filtrar por ano (2024, 2025) |
| Período (Mês) | Slicer — lista | Permite filtrar por mês específico |
| Período (Trimestre) | Slicer — lista | Permite filtrar por trimestre (1 a 4) |
| Região | Slicer — lista | Permite selecionar uma ou mais regiões |
| Estado | Slicer — lista | Permite selecionar um ou mais estados |
| Categoria | Slicer — lista | Permite selecionar uma ou mais categorias de produto |
| Vendedor | Slicer — lista | Permite selecionar um ou mais vendedores |

**Filtros de página:** A página de Vendedores mantém um filtro de região persistente. A página Geográfica mantém um filtro de região persistente.

**Interações entre páginas:** Dril-through configurado para navegar da página de Visão Executiva (clicando em uma categoria) para uma página de detalhamento de produtos (se implementado).

---

## 9. Público-Alvo

### 9.1 Alta Gestão (CEO, CFO, Diretoria)

**Necessidade:** Visão consolidada de alto nível. KPIs de faturamento, crescimento e participação regional. Atualização periódica (mensal/trimestral).

**Página principal:** Página 1 — Visão Executiva.

**Perguntas típicas:**
- A empresa está crescendo? A que taxa?
- Qual o faturamento total e como se compara ao período anterior?
- Quais regiões estão performando acima/abaixo do esperado?

### 9.2 Gerência Comercial (Gerente de Vendas, Coordenadores)

**Necessidade:** Acompanhamento de desempenho da equipe de vendas. Comparação entre vendedores. Identificação de _top performers_ e oportunidades de melhoria.

**Página principal:** Página 2 — Análise de Vendedores.

**Perguntas típicas:**
- Quem são os 3 melhores vendedores deste mês?
- Quais vendedores estão abaixo da média e precisam de suporte?
- Como o ticket médio varia entre os vendedores?

### 9.3 Diretores Regionais

**Necessidade:** Análise territorial detalhada. Compreensão do mercado local. Identificação de oportunidades de expansão.

**Página principal:** Página 3 — Análise Geográfica.

**Perguntas típicas:**
- Como está o desempenho da minha região em relação às demais?
- Quais estados/municípios concentram as vendas?
- Quais categorias de produto têm melhor aceitação na minha região?

### 9.4 Equipe de Marketing e Produto

**Necessidade:** Entendimento do mix de produtos e comportamento de consumo por região. Subsídio para campanhas promocionais e definição de sortimento regional.

**Páginas relevantes:** Página 1 (categorias), Página 3 (cruzamento região × categoria).

**Perguntas típicas:**
- Quais categorias deveriam ser promovidas em cada região?
- O portfólio atual atende à demanda de todas as regiões?
- Há oportunidade para campanhas de _upsell_ em categorias com ticket médio baixo?

---

## 10. Glossário

| Termo | Definição |
|-------|-----------|
| **SKU** | Stock Keeping Unit — código único que identifica cada produto no catálogo. |
| **Ticket Médio** | Valor médio gasto pelo cliente por pedido. Calculado como faturamento total dividido pelo número de pedidos. |
| **Faturamento** | Receita bruta total da empresa, somando o valor de todos os pedidos (produtos + frete). |
| **KPI** | Key Performance Indicator — indicador-chave de desempenho, métrica estratégica para avaliação do negócio. |
| **Star Schema** | Modelo dimensional composto por uma tabela fato central cercada por dimensões desnormalizadas. Otimizado para consultas analíticas. |
| **Dimensão** | Tabela com atributos descritivos que qualificam as medições da tabela fato (ex.: cliente, produto, data, vendedor). |
| **Fato** | Tabela central do modelo dimensional que contém as medidas quantitativas do negócio e chaves estrangeiras para as dimensões. |
| **Granularidade** | Nível de detalhe de cada linha em uma tabela. Na fato, a granularidade é de 1 linha por pedido. |
| **Surrogate Key** | Chave substituta artificial (geralmente inteiro sequencial) usada como chave primária na dimensão, desacoplada do identificador de origem. |
| **Degenerate Dimension** | Atributo mantido na tabela fato que não possui dimensão própria, como o número do pedido. |
| **SCD** | Slowly Changing Dimension — estratégia para gerenciar mudanças em atributos dimensionais ao longo do tempo. Tipo 1 sobrescreve; Tipo 2 versiona. |
| **Medallion Architecture** | Arquitetura de camadas progressivas (Bronze → Silver → Gold) para organização de dados em _data lakes_ e _lakehouses_. |
| **Delta Lake** | Camada de armazenamento transacional sobre arquivos Parquet, com suporte a ACID, versionamento e schema enforcement. |
| **Drill-through** | Navegação entre páginas de um dashboard, passando de uma visão agregada para uma visão detalhada. |
| **Cross-filtering** | Funcionalidade do Power BI em que a seleção em um visual automaticamente filtra os demais visuais da página. |
| **Slicer** | Componente visual do Power BI que atua como filtro interativo (segmentação de dados). |
| **MoM** | Month over Month — variação percentual entre um mês e o mês imediatamente anterior. |
| **YoY** | Year over Year — variação percentual entre um período e o mesmo período do ano anterior. |
| **Upsell** | Estratégia de vendas que incentiva o cliente a comprar uma versão mais cara ou premium do produto. |
| **Cross-sell** | Estratégia de vendas que oferece produtos complementares ao item principal da compra. |

---

*Documento gerado para o projeto BI E-Commerce — versão 1.0. Junho de 2026.*
