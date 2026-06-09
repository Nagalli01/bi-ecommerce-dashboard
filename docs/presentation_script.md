# Roteiro de Apresentação — Projeto BI E-Commerce

**Duração total:** 15 minutos
**Equipe:** 4 integrantes
**Formato:** Apresentação acadêmica oral com slides de apoio

---

## Slide 1 — Capa
**Tempo:** 30 segundos
**Quem fala:** Integrante 1

### Conteúdo do slide:
- Título: "BI E-Commerce — Solução de Business Intelligence com Arquitetura Medallion"
- Subtítulo: "PySpark + Delta Lake + Power BI"
- Nomes dos 4 integrantes
- Instituição / Curso / Data

### O que dizer:

> Boa tarde a todos. Meu nome é [Nome do Integrante 1] e junto com meus colegas [Nome 2], [Nome 3] e [Nome 4], apresentamos hoje o projeto BI E-Commerce. Trata-se de uma solução completa de Business Intelligence para uma empresa de comércio eletrônico de eletrônicos, implementada com arquitetura Medallion utilizando PySpark e Delta Lake, com consumo final em Power BI. Ao longo dos próximos quinze minutos, vamos mostrar desde a geração dos dados até os insights de negócio que o dashboard entrega.

**Pontos-chave:** Apresentar-se brevemente. Contextualizar a apresentação inteira. Não gastar mais que 30 segundos.

---

## Slide 2 — Visão Geral da Arquitetura
**Tempo:** 1 minuto
**Quem fala:** Integrante 1

### Conteúdo do slide:
- Diagrama da arquitetura Medallion em três camadas:
  - Bronze (dados brutos, Delta Lake, particionado por região)
  - Silver (dados limpos, padronizados e enriquecidos)
  - Gold (Star Schema com 4 dimensões e 1 fato)
- Setas indicando o fluxo: CSV → Bronze → Silver → Gold → Power BI

### O que dizer:

> Nosso projeto segue a arquitetura Medallion, um padrão da indústria para organização de dados em lakehouses. A ideia é simples: os dados evoluem em três camadas progressivas. A camada Bronze armazena os dados brutos exatamente como eles chegam — no nosso caso, três arquivos CSV com clientes, produtos e pedidos. Não mexemos em nada aqui; é a nossa camada de segurança. Na Silver, aplicamos toda a inteligência de qualidade: limpamos nomes, padronizamos siglas de estado, removemos duplicatas e fazemos o enriquecimento principal, que é calcular o valor total de cada pedido cruzando com a tabela de produtos. Finalmente, na camada Gold, modelamos um Star Schema — um esquema estrela com quatro dimensões, que vocês vão ver em detalhes daqui a pouco, e uma tabela fato central de vendas. Tudo isso é implementado em PySpark com armazenamento Delta Lake, o que nos dá transações ACID e versionamento dos dados. O Power BI consome diretamente os arquivos da camada Gold.

**Pontos-chave:** Explicar que Bronze é raw, Silver é limpo, Gold é modelado. Mencionar Delta Lake.

---

## Slide 3 — Pipeline de Execução
**Tempo:** 1 minuto
**Quem fala:** Integrante 1

### Conteúdo do slide:
- Fluxograma sequencial:
  1. `00_generate_data.py` — gera CSVs sintéticos
  2. `01_validate_inputs.py` — validação inicial
  3. `10_bronze_ingestion.py` — ingestão Bronze
  4. `20_silver_transform.py` — limpeza e enriquecimento Silver
  5. `30_gold_model.py` — modelagem Star Schema Gold
  6. `40_quality_checks.py` — verificações finais

### O que dizer:

> O pipeline é composto por seis scripts Python executados sequencialmente. Primeiro, geramos dados sintéticos: mil e quinhentos clientes, duzentos e cinquenta produtos e oito mil pedidos, cobrindo dez estados brasileiros e as cinco regiões. Essa geração usa a biblioteca Faker com localidade brasileira para produzir dados verossímeis. Depois validamos as entradas: conferimos se as contagens batem, se as chaves estrangeiras são válidas e se não há preços negativos. Na sequência, ingerimos os dados na Bronze usando schemas explícitos no Spark, o que garante que os tipos já estejam corretos desde o primeiro contato. O script da Silver aplica as transformações de qualidade, e o da Gold constrói o modelo dimensional. Por último, uma bateria de verificações de qualidade confere integridade referencial — ou seja, se toda venda aponta para um cliente, produto, data e vendedor que realmente existem. Todo o pipeline pode ser executado com um único comando: `python src/run_pipeline.py`.

**Pontos-chave:** Enfatizar a sequência e a dependência entre scripts. Mencionar o comando único.

---

## Slide 4 — Tecnologias e Justificativas
**Tempo:** 1 minuto
**Quem fala:** Integrante 1

### Conteúdo do slide:
- Ícones/logos das tecnologias: Python, PySpark, Delta Lake, Power BI
- Box com justificativas curtas

### O que dizer:

> Escolhemos PySpark como engine de processamento porque, mesmo rodando localmente, a arquitetura é idêntica à que se usa em clusters de produção com terabytes de dados. O Delta Lake adiciona confiabilidade: cada escrita é atômica, é possível viajar no tempo para versões anteriores dos dados, e o schema é validado automaticamente — ninguém corrompe uma tabela por engano. Python foi a linguagem natural pela produtividade e pela integração nativa com Spark. E o Power BI, além de ser a ferramenta de visualização mais adotada no mercado brasileiro, possui conector nativo a arquivos Parquet, que é o formato interno do Delta Lake. Ou seja, conseguimos conectar diretamente nas pastas da camada Gold sem nenhum driver adicional. Isso fecha o ciclo completo: da geração de dados ao dashboard, tudo com ferramentas maduras e de mercado.

**Pontos-chave:** Justificar cada tecnologia em uma frase. Conectar com o mercado real.

---

## Slide 5 — Geração de Dados e Fontes
**Tempo:** 1 minuto e 20 segundos
**Quem fala:** Integrante 2

### Conteúdo do slide:
- Tabela resumo das fontes:
  - clientes: 1.500 registros, 8 colunas
  - produtos: 250 registros, 7 colunas, 8 categorias
  - pedidos: 8.000 registros, 10 colunas
- Mapa mental com as 10 siglas de estado cobertos

### O que dizer:

> Boa tarde. Eu sou o [Nome do Integrante 2] e vou conduzir vocês pelas camadas Bronze e Silver. Antes de chegar lá, é importante entender de onde os dados vêm. Nosso projeto simula uma empresa real de e-commerce de eletrônicos que atua nacionalmente. Geramos três fontes de dados. A tabela de clientes tem mil e quinhentos registros com dados cadastrais completos: nome, e-mail, telefone, cidade, estado, região e data de cadastro. A tabela de produtos tem duzentos e cinquenta itens distribuídos em oito categorias — Smartphones, Notebooks, Acessórios, Áudio, Tablets, Monitores, Periféricos e Armazenamento — com preço de venda, preço de custo e estoque. E a tabela de pedidos, a principal, contém oito mil transações. Cada pedido vincula um cliente a um produto, em uma data, por meio de um vendedor, para entrega em um município. Os estados cobertos — São Paulo, Rio de Janeiro, Minas Gerais, Rio Grande do Sul, Paraná, Bahia, Pernambuco, Ceará, Amazonas e Distrito Federal — representam bem a distribuição nacional. É importante destacar que são dados sintéticos, mas gerados com distribuições que simulam razoavelmente a realidade de mercado.

**Pontos-chave:** Contextualizar o domínio de negócio. Não entrar em detalhes técnicos ainda.

---

## Slide 6 — Camada Bronze (Ingestão)
**Tempo:** 1 minuto e 20 segundos
**Quem fala:** Integrante 2

### Conteúdo do slide:
- Tabela mostrando "Antes" (CSV) e "Depois" (Delta com particionamento)
- Destaque: `schema enforcement` e `partitionBy("regiao")`
- Exemplo de linha de CSV e como fica armazenada

### O que dizer:

> A camada Bronze é o primeiro contato do Spark com os dados. Lemos cada CSV definindo um schema explícito — isso é importante porque obriga o Spark a interpretar corretamente cada coluna: inteiros ficam como inteiros, decimais como decimais, datas como datas. Nada de "tudo string". Gravamos o resultado em formato Delta Lake, que internamente usa Parquet colunar, mas adiciona metadados transacionais. Para as tabelas de clientes e pedidos, aplicamos particionamento por região. Isso significa que, fisicamente em disco, os dados são organizados em subpastas: uma para Sudeste, outra para Nordeste, e assim por diante. Quando uma consulta filtra por uma região específica, o Spark lê apenas a partição relevante, ignorando as demais — é o que chamamos de _partition pruning_. Na Bronze, os dados estão exatamente como chegaram. Não aplicamos nenhuma transformação. A ideia é preservar a fonte original intacta. Se amanhã descobrirmos um problema na lógica de limpeza, podemos sempre voltar à Bronze e reprocessar do zero.

**Pontos-chave:** Schema explícito. Particionamento. Imutabilidade da Bronze.

---

## Slide 7 — Camada Silver (Limpeza e Enriquecimento)
**Tempo:** 1 minuto e 20 segundos
**Quem fala:** Integrante 2

### Conteúdo do slide:
- Exemplos de "Antes e Depois":
  - `"joão da silva"` → `"João Da Silva"` (Title Case)
  - `"sp"` → `"SP"` (UPPER)
  - Pedido sem total → Pedido com `total_pedido = quantidade × preco_venda + frete`
- Checklist de validações aplicadas

### O que dizer:

> A Silver é onde a mágica acontece. Pegamos os dados da Bronze e aplicamos cinco tipos de transformação. Primeiro, a padronização: nomes de clientes e cidades são convertidos para Title Case usando a função nativa do Spark `initcap`. Siglas de estado vão para caixa alta, e e-mails para minúsculas. Isso é fundamental porque, sem padronização, um mesmo cliente poderia aparecer como "ana silva" em um pedido e "ANA SILVA" em outro, quebrando agrupamentos. Segundo, a validação de domínio: removemos produtos com preço zero ou negativo e pedidos com quantidade inválida. Terceiro, a deduplicação: garantimos que cada cliente_id, cada SKU e cada pedido_id apareçam uma única vez. Quarto, e talvez o mais importante, o enriquecimento: os pedidos não têm o valor total na origem. Fazemos um JOIN com a tabela de produtos para obter o preço unitário e calculamos `total_pedido` como quantidade vezes preço de venda mais o frete. Isso transforma um registro transacional incompleto em uma medida financeira pronta para análise. Por último, também enriquecemos a tabela de produtos com a margem bruta e o percentual de margem, que depois podem ser usados para análises de rentabilidade.

**Pontos-chave:** Mostrar exemplos concretos de antes/depois. Enfatizar o cálculo do total_pedido.

---

## Slide 8 — Modelagem Star Schema
**Tempo:** 1 minuto e 20 segundos
**Quem fala:** Integrante 3

### Conteúdo do slide:
- Diagrama do Star Schema:
  - Centro: `fact_vendas` (pedido_id, id_cliente FK, id_produto FK, data_pedido FK, id_vendedor FK, quantidade, valor_frete, total_pedido, municipio, estado, regiao)
  - 4 dimensões ao redor com linhas conectando

### O que dizer:

> Olá, sou o [Nome do Integrante 3] e vou apresentar a camada Gold e o modelo dimensional. O coração da nossa solução de BI é o Star Schema — o esquema estrela — que modelamos na camada Gold. É o padrão mais consagrado para data warehouses e ferramentas de BI. A ideia é simples: uma tabela fato central com todas as medidas quantitativas do negócio — valores, quantidades, fretes — cercada por dimensões que respondem às perguntas clássicas de análise. Quem comprou? O que foi comprado? Quando? Quem vendeu? A tabela fato de vendas tem granularidade de um pedido por linha. Cada linha contém chaves estrangeiras que apontam para as quatro dimensões, mais as medidas: quantidade, valor do frete e total do pedido. Também mantivemos na fato colunas como município, estado e região — são o que chamamos de atributos degenerados — porque são úteis para filtros rápidos sem precisar passar por uma dimensão geográfica separada. O importante é que o Star Schema é otimizado para consultas: as dimensões são desnormalizadas, ou seja, cada dimensão já contém todos os atributos necessários, sem precisar de mais JOINs. O Power BI adora esse modelo.

**Pontos-chave:** Explicar o porquê do Star Schema. Dizer o que cada dimensão representa.

---

## Slide 9 — As Quatro Dimensões
**Tempo:** 1 minuto e 20 segundos
**Quem fala:** Integrante 3

### Conteúdo do slide:
- Quadro com 4 boxes, um para cada dimensão:
  - dim_clientes (id_cliente, nome, cidade, estado, região) — "Quem?"
  - dim_produtos (id_produto, nome, categoria, preço) — "O quê?"
  - dim_calendario (data, dia, mês, trimestre, ano) — "Quando?"
  - dim_vendedores (id_vendedor, nome, região) — "Quem vendeu?"

### O que dizer:

> Vamos detalhar cada dimensão. A dimensão de clientes responde "quem comprou?". Extraímos da tabela silver apenas os atributos descritivos: identificador, nome, cidade, estado e região. Não precisamos de e-mail ou telefone aqui, porque eles não são analíticos — são dados operacionais. A dimensão de produtos responde "o que foi vendido?". Pegamos o identificador do produto — que extraímos do número do SKU —, o nome, a categoria e o preço de venda. As oito categorias permitem agrupar vendas em níveis de análise estratégicos. A dimensão calendário é especial: ela é gerada programaticamente. Pegamos a menor e a maior data dos pedidos e criamos uma linha para cada dia nesse intervalo. Cada linha tem o dia do mês, o nome do mês por extenso e abreviado, o número do mês, o trimestre e o ano. Isso permite hierarquias temporais no Power BI: você pode navegar de ano para trimestre, para mês, para dia. E a dimensão de vendedores lista os quinze vendedores com nome e região de atuação. No total, temos um modelo enxuto, com apenas quatro dimensões, mas que cobre praticamente todas as perguntas de negócio relevantes para uma operação de e-commerce.

**Pontos-chave:** Ser didático. Mostrar a relação pergunta-dimensão.

---

## Slide 10 — Verificações de Qualidade
**Tempo:** 1 minuto e 20 segundos
**Quem fala:** Integrante 3

### Conteúdo do slide:
- Lista de verificações executadas com ícones de check:
  - Contagem de registros em cada camada
  - Unicidade de chaves primárias
  - Integridade referencial (4 LEFT ANTI JOINs)
  - Domínios válidos (preços > 0, estados válidos)
  - Ausência de nulos em colunas críticas
  - Métricas consolidadas (faturamento, pedidos, ticket médio)

### O que dizer:

> Nenhum pipeline de dados está completo sem verificações de qualidade. Implementamos dez verificações automatizadas no script de quality checks. A primeira categoria é contagem: conferimos se a Bronze tem mil e quinhentos clientes, duzentos e cinquenta produtos e oito mil pedidos, e se as camadas seguintes não perdem registros indevidamente. Depois, unicidade de chaves: nenhuma chave primária pode estar duplicada. A verificação mais importante é a de integridade referencial. Fazemos quatro LEFT ANTI JOINs — uma técnica que retorna apenas os registros da fato que não encontram correspondente na dimensão. Se qualquer um desses JOINs retornar alguma linha, significa que temos vendas órfãs — por exemplo, um pedido apontando para um vendedor que não existe. Isso pararia o pipeline com uma mensagem de erro clara. Também validamos domínios: nenhum preço pode ser negativo ou zero, nenhum estado pode ser diferente da lista de dez estados esperados. Por fim, recalculamos as métricas principais — faturamento total, número de pedidos distintos, ticket médio e total de vendedores — e conferimos se batem com os valores esperados. Essa bateria de verificações garante que o que chega ao Power BI é confiável.

**Pontos-chave:** Enfatizar integridade referencial. Mostrar que qualidade é prioridade.

---

## Slide 11 — Visão Geral do Dashboard
**Tempo:** 1 minuto
**Quem fala:** Integrante 4

### Conteúdo do slide:
- Screenshots em miniatura das 3 páginas do dashboard
- Fluxo de navegação entre elas

### O que dizer:

> Boa tarde, sou o [Nome do Integrante 4] e é comigo que vocês vão ver para onde tudo isso converge. O resultado final do nosso projeto é um dashboard interativo no Power BI Desktop, composto por três páginas, cada uma com um propósito específico e um público-alvo distinto. A primeira página, Visão Executiva, traz os quatro KPI principais em cards no topo — faturamento, total de pedidos, ticket médio e total de vendedores — e gráficos que mostram faturamento por categoria, evolução temporal e distribuição geográfica. É a página que um diretor abriria numa reunião de segunda-feira de manhã. A segunda página é focada em vendedores: um ranking completo de performance, com comparações de ticket médio e participação percentual de cada vendedor no faturamento. É a página do gerente comercial. A terceira página faz a análise geográfica: mapa do Brasil com intensidade de vendas por estado, ranking de municípios e um cruzamento de região por categoria de produto que revela preferências regionais de consumo. As três páginas são interligadas por filtros e é possível navegar de uma para outra com drill-through.

**Pontos-chave:** Apresentar as 3 páginas. Associar cada página a um público.

---

## Slide 12 — KPIs e Principais Insights
**Tempo:** 1 minuto
**Quem fala:** Integrante 4

### Conteúdo do slide:
- Cards ampliados dos 4 KPIs com valores (ilustrativos)
- Bullet points de insights de negócio descobertos

### O que dizer:

> Vamos aos números e ao que eles nos contam. Os quatro KPIs centrais são: faturamento total, que é a soma de todos os totais de pedidos; total de pedidos, que é a contagem distinta de identificadores de pedido; ticket médio, que é a divisão do faturamento pelo número de pedidos — ou seja, quanto em média cada cliente gasta por compra; e total de vendedores, fixo em quinze. Mas KPI sem contexto é só número. O valor do dashboard está nos insights que ele permite extrair. Por exemplo: ao cruzar faturamento por categoria, identificamos quais categorias são as "vacas leiteiras" do negócio e quais têm participação marginal, subsidiando decisões de sortimento. Ao analisar o ranking de vendedores, conseguimos ver não só quem vende mais, mas quem vende melhor — porque faturamento alto com ticket médio baixo pode indicar que o vendedor está empurrando volume de produtos baratos, enquanto um ticket médio elevado sugere habilidade em vender produtos premium. A análise geográfica revela concentração de vendas: tipicamente, Sudeste domina o faturamento, mas regiões como Nordeste podem apresentar ticket médio surpreendentemente alto em categorias específicas. E a evolução temporal expõe sazonalidades — picos em novembro e dezembro, por exemplo, consistentes com Black Friday e Natal. Esses padrões permitem planejar estoque, campanhas e metas com antecedência.

**Pontos-chave:** Explicar cada KPI. Dar exemplos concretos de insights.

---

## Slide 13 — Navegação e Funcionalidades do Dashboard
**Tempo:** 1 minuto
**Quem fala:** Integrante 4

### Conteúdo do slide:
- Screenshots ou mockups mostrando:
  - Slicers (filtros de período, região, categoria)
  - Cross-filtering (selecionar uma barra e ver os outros visuais atualizarem)
  - Drill-through

### O que dizer:

> O dashboard não é estático — ele é totalmente interativo. Temos slicers, que são os filtros visuais, em todas as páginas: você pode selecionar um ano específico, um trimestre, uma região, uma categoria ou um vendedor, e todos os gráficos se atualizam instantaneamente. A mágica do Power BI está no cross-filtering: se eu clicar na barra de Smartphones no gráfico de categorias, automaticamente o gráfico de evolução temporal passa a mostrar apenas o faturamento de Smartphones ao longo do tempo, o mapa muda para mostrar só os estados onde Smartphones foram vendidos, e o ranking de vendedores se reordena considerando apenas vendas dessa categoria. Tudo isso acontece em frações de segundo, porque as medidas são calculadas em memória pelo motor DAX. Outro recurso importante é o drill-through: da página de Visão Executiva, ao clicar com o botão direito em uma região, é possível navegar para a página Geográfica já filtrada para aquela região específica. Isso torna a exploração dos dados muito fluida. E como os dados estão em Delta Lake, se o pipeline for re-executado com dados novos, basta atualizar a conexão no Power BI que tudo se atualiza. É uma solução viva.

**Pontos-chave:** Enfatizar interatividade. Mostrar o valor do cross-filtering.

---

## Slide 14 — Conclusão
**Tempo:** 30 segundos
**Quem fala:** Integrante 1

### Conteúdo do slide:
- Resumo em 4 bullet points:
  - Arquitetura Medallion completa (Bronze → Silver → Gold)
  - Pipeline ETL automatizado e reprodutível
  - Star Schema otimizado para análises multidimensionais
  - Dashboard interativo com insights acionáveis
- "Obrigado" / "Perguntas?"

### O que dizer:

> Recapitulando: entregamos uma solução de BI de ponta a ponta. Começamos com dados sintéticos que simulam uma operação real de e-commerce brasileiro. Implementamos a arquitetura Medallion em três camadas usando PySpark e Delta Lake, com qualidade de dados garantida por verificações automatizadas. Modelamos um Star Schema profissional, pronto para consumo analítico. E coroamos tudo com um dashboard interativo no Power BI que transforma dados brutos em decisões de negócio. O projeto demonstra que, mesmo com ferramentas acessíveis e execução local, é possível implementar um pipeline de dados com padrões de indústria. É uma fundação sólida que poderia ser escalada para ambientes de produção em nuvem com volumes muito maiores. Obrigado pela atenção. Ficamos à disposição para perguntas.

**Pontos-chave:** Ser conciso. Agradecer. Abrir para perguntas.

---

## Notas para os Integrantes

### Dicas de Apresentação

- **Ensaiem as transições entre integrantes.** Cada passagem deve ser fluida: "Agora, o [Nome] vai detalhar a camada Silver" ou "Com vocês, [Nome] para mostrar o dashboard".
- **Cuidado com o tempo.** 15 minutos passam rápido. Se estiverem atrasando, cortem exemplos secundários, nunca os conceitos principais.
- **Olhem para a plateia, não para os slides.** Os slides são apoio visual, não teleprompter.
- **Tom de conversa, não de leitura.** O roteiro acima é um guia; adaptem a linguagem para soar natural.
- **Preparem-se para perguntas típicas:**
  - "Por que Delta Lake e não Parquet puro?" → Responder com ACID e versionamento.
  - "Como escalariam isso para milhões de registros?" → Responder com particionamento por data, Z-ordering, execução em cluster.
  - "Como lidariam com dados reais e LGPD?" → Responder com data masking e criptografia.
  - "Por que Power BI e não Tableau ou outra ferramenta?" → Responder com mercado brasileiro e conector Parquet nativo.
  - "Como garantir a qualidade se os dados mudam todo dia?" → Responder com quality checks automatizados e Delta Lake schema enforcement.

### Divisão de Conteúdo por Integrante

| Integrante | Slides | Conteúdo |
|------------|--------|----------|
| Integrante 1 | 1, 2, 3, 4, 14 | Abertura, arquitetura, pipeline, tecnologias, conclusão |
| Integrante 2 | 5, 6, 7 | Fontes de dados, Bronze, Silver |
| Integrante 3 | 8, 9, 10 | Star Schema, dimensões, qualidade |
| Integrante 4 | 11, 12, 13 | Dashboard, KPIs, insights |

---

*Documento gerado para o projeto BI E-Commerce — versão 1.0. Junho de 2026.*
