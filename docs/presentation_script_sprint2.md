# Roteiro de Apresentação — Sprint 2 · BI E-Commerce

**Duração total:** ~15 minutos
**Equipe:** 4 integrantes
**Formato:** Apresentação oral em grupo, tom de conversa, sem leitura de slides
**Contexto:** Sprint 2 — Transformar o projeto em um processo completo e repetível

---

## Pessoa 1 (≈ 3min30s) — Abertura + Pipeline (Engenharia de Dados)

"Boa tarde, professor. Nós vamos apresentar a Sprint 2 do nosso Projeto Integrador — BI E-Commerce, seguindo o fluxo que está representado na imagem: primeiro a pipeline de dados, depois a transformação e modelagem, e por fim o relatório no Power BI e o dashboard web.

Na Sprint 2, o nosso objetivo foi transformar o projeto em um processo completo e repetível, ou seja, sair de um cenário de tarefas manuais e notebooks isolados e passar a ter uma esteira organizada, com execução automatizada e resultados consistentes.

A primeira parte é a pipeline, que é a 'linha de montagem' do projeto. Ela define a ordem correta de execução e garante que tudo rode sempre do mesmo jeito. Nós criamos um orquestrador em Python — o `run_pipeline.py` — que encadeia seis etapas em sequência: primeiro a geração de dados sintéticos, depois a validação das entradas, em seguida a ingestão na camada Bronze, depois transformação para Silver, depois modelagem para Gold com Star Schema, e por fim as verificações de qualidade. Cada etapa depende da anterior, e se qualquer uma falhar, o pipeline para imediatamente com uma mensagem de erro clara.

Essa pipeline implementa a arquitetura Medallion, que é um padrão da indústria para organização de dados em lakehouses. São três camadas progressivas: Bronze para os dados brutos exatamente como chegaram, Silver para limpeza e padronização, e Gold para o modelo dimensional pronto para consumo analítico. Com isso, quando alguém executar a pipeline, o projeto se reconstrói de ponta a ponta.

Um ponto importante é que essa pipeline foi preparada para ser reexecutável. Em projetos reais, a execução precisa ser segura, então nós ajustamos a forma de escrita das tabelas para evitar falhas do tipo 'arquivo já existe' e também tratamos validação de schema logo na entrada. O resultado é que o projeto não depende de passos manuais para funcionar: basta executar `python src/run_pipeline.py` e o ambiente fica consistente novamente.

Para dar uma dimensão do volume: nossa base tem 1.500 clientes, 250 produtos em 8 categorias de eletrônicos e 8.000 pedidos, cobrindo 10 estados brasileiros e as 5 regiões, com 15 vendedores. O pipeline inteiro roda em poucos segundos e gera todas as camadas e o relatório de qualidade automaticamente.

Agora eu vou passar para a próxima pessoa, que vai explicar como nós tratamos os dados na parte de transformação, que é onde garantimos qualidade e criamos uma base confiável para o BI."

---

## Pessoa 2 (≈ 4min) — Transformação (Silver) + Modelagem (Gold)

"Continuando, eu vou falar sobre a parte de transformação e modelagem, que foi o coração técnico da Sprint 2.

Na camada Silver, nós pegamos os dados que vieram da Bronze e aplicamos regras de padronização e qualidade. Isso inclui ajustar tipos de dados, garantir consistência nos campos principais e preparar as tabelas para análise. A ideia aqui é que a Silver seja a camada onde os dados deixam de ser 'brutos' e passam a ser confiáveis: é onde se reduz sujeira, se organiza o formato e se evita inconsistências.

Na prática, o que fizemos: padronizamos nomes de clientes e cidades para Title Case — ou seja, 'joão da silva' vira 'João Da Silva'. Siglas de estado foram convertidas para caixa alta, para garantir que 'sp' e 'SP' sejam tratados como o mesmo estado nos agrupamentos. E-mails foram normalizados para minúsculas. Também removemos produtos com preço zero ou negativo e deduplicamos registros.

Mas a transformação mais importante foi o enriquecimento dos pedidos. Os dados brutos não têm o valor total da venda — eles só informam a quantidade e o frete. Nós fizemos um JOIN com a tabela de produtos para obter o preço unitário e calculamos o `total_pedido` como quantidade vezes preço de venda mais o frete. Isso transforma um registro transacional incompleto em uma medida financeira pronta para análise. Também calculamos a margem bruta dos produtos, que é o preço de venda menos o preço de custo, para análises de rentabilidade.

Depois disso, passamos para a camada Gold, que é a camada de consumo analítico. Nela nós criamos um modelo dimensional seguindo o conceito de Star Schema — o Esquema Estrela. Em vez de o relatório ficar fazendo múltiplos JOINs complexos diretamente em tabelas operacionais, nós estruturamos quatro dimensões e uma tabela fato central.

As dimensões são: dim_clientes, que responde 'quem comprou'; dim_produtos, respondendo 'o que foi comprado'; dim_calendario, que nós geramos programaticamente com 731 dias, incluindo hierarquias de dia, mês, trimestre e ano, respondendo 'quando'; e dim_vendedores, mapeando os 15 vendedores com nome e região, respondendo 'quem vendeu'. A tabela fato — fact_vendas — concentra todas as medidas: quantidade, valor do frete e total do pedido, com chaves estrangeiras apontando para cada dimensão.

Além da modelagem, nós também fizemos um enriquecimento analítico. Como o dataset original não tinha algumas dimensões necessárias para a análise que queríamos apresentar, nós incluímos o conceito de vendedor, região e município na própria tabela fato como atributos degenerados. Isso permite que o projeto responda perguntas de negócio como: qual região vende mais, quais são os municípios com maior faturamento, e como está o ranking dos vendedores. Esse enriquecimento foi incorporado na Gold para que o Power BI e o dashboard já consumam os dados prontos.

E nada disso seria confiável sem verificações de qualidade. Nosso script de quality checks confere seis categorias: contagem de registros em cada camada, análise de nulos em todas as colunas críticas, integridade referencial — usando LEFT ANTI JOINs para garantir que nenhuma venda aponte para um cliente, produto, vendedor ou data que não existe —, validação de datas, métricas de negócio e análise de distribuição. O resultado: zero nulos em colunas críticas, 100% de integridade referencial, faturamento total de R$ 179,6 milhões, 8.000 pedidos e ticket médio de R$ 22.447.

Com isso, ao final dessa etapa, nós temos tabelas finais bem definidas e prontas para o painel. Agora eu passo para a próxima pessoa, que vai mostrar como isso virou um relatório executivo e um dashboard interativo."

---

## Pessoa 3 (≈ 4min) — Power BI + Dashboard (relatório executivo)

"Agora eu vou falar da parte de visualização, que é onde o valor fica mais claro para quem vai tomar decisão.

Nós entregamos duas frentes de visualização. A primeira é um relatório no Power BI Desktop, consumindo o modelo Gold diretamente via MySQL, com medidas DAX e visuais Python. A segunda é um dashboard web interativo feito em Streamlit com Plotly, que está publicado online e pode ser acessado de qualquer navegador.

A ideia do nosso relatório foi seguir uma estética profissional: fundo escuro, leitura rápida e indicadores bem claros. Como o visual de mapa nativo do Power BI tem limitações no ambiente acadêmico, nós utilizamos Python visuals com matplotlib e geopandas para gerar mapas coropléticos com os dados reais de faturamento por estado. Isso mantém o insight geográfico e ainda melhora a precisão visual.

No topo do relatório, nós colocamos os principais indicadores — os KPIs em formato de cards. Faturamento total, total de pedidos, ticket médio e a contagem de vendedores. Esses KPIs são medidas DAX, então eles respondem a filtros e cortes automaticamente. Se eu filtrar por uma região, todos os cards se atualizam.

Na parte central do relatório, nós estruturamos as análises principais. Temos o mapa de faturamento por estado, que mostra a concentração de vendas no território nacional. Ao lado, mostramos faturamento por região — e os dados mostram que Sudeste lidera com R$ 55 milhões, seguido de perto pelo Nordeste com R$ 53,8 milhões. Também construímos um ranking dos vendedores, que foi possível graças ao enriquecimento feito na Gold — nossa top vendedora é Juliana Alves, com R$ 12,7 milhões. Além disso, incluímos um Top 10 de municípios para evidenciar onde há maior concentração de vendas.

O dashboard em Streamlit complementa essa análise com 4 páginas: Visão Executiva, Vendedores, Produtos & Categorias, e Análise Geográfica. Ele tem filtros interativos por ano, região, estado e categoria, cross-filtering entre gráficos e está publicado no Hugging Face Spaces, então qualquer pessoa com o link pode acessar. É um dashboard vivo, que funciona em tempo real.

E para fechar a leitura de negócio, nós incluímos a evolução temporal do faturamento por mês, permitindo identificar tendência e sazonalidade. Os dados cobrem dois anos — 2023 e 2024 — então já é possível ver padrões como picos no final do ano, consistentes com Black Friday e Natal. O ponto importante é que tudo isso está alimentado por uma pipeline e um modelo Gold automatizado: o relatório não é algo manual, ele é o resultado final de um processo de engenharia de dados.

Agora eu passo para a última pessoa para encerrar a Sprint 2 com as entregas e como isso fecha o projeto para apresentação."

---

## Pessoa 4 (≈ 3min30s) — Encerramento: entregas, valor e demonstração curta

"Para encerrar, eu vou resumir as entregas da Sprint 2 e o valor do que foi construído.

Ao final desta sprint, a gente tem um projeto completo e apresentável, porque ele está estruturado como um fluxo real de engenharia de dados. Primeiro, existe uma pipeline orquestrada em Python que organiza a execução de seis etapas com tratamento de erros e medição de tempo. Segundo, existem camadas bem definidas seguindo a arquitetura Medallion: Bronze para ingestão, Silver para tratamento e qualidade, e Gold para modelagem analítica com Star Schema. Terceiro, existe um relatório executivo no Power BI e um dashboard web em Streamlit consumindo o modelo Gold, mostrando KPIs e análises de ranking por estado, região, município e vendedores. Quarto, as verificações de qualidade são automatizadas e garantem 100% de integridade referencial e zero nulos em colunas críticas.

O que diferencia o nosso trabalho é que nós não entregamos apenas um painel ou um notebook: nós entregamos um processo. Se amanhã os dados forem recarregados ou a base crescer, a pipeline pode rodar novamente com um único comando e o relatório continua consistente. Isso representa um padrão mais próximo de um cenário profissional de engenharia de dados.

Se o professor quiser uma demonstração rápida, nós conseguimos rodar a pipeline — `python src/run_pipeline.py` — e mostrar no terminal as seis etapas sendo executadas em sequência, com os tempos de cada uma e o relatório de qualidade sendo gerado automaticamente. Em seguida, podemos abrir o dashboard no Streamlit para ver os indicadores, rankings e gráficos interativos. Isso prova que o fluxo está funcionando de ponta a ponta.

Resumindo os números do projeto: 1.500 clientes, 250 produtos, 8.000 pedidos, 15 vendedores, 10 estados, 5 regiões, 8 categorias de eletrônicos, faturamento de R$ 179,6 milhões, ticket médio de R$ 22.447 e pipeline que roda em poucos segundos. O dashboard está publicado em [huggingface.co/spaces/Nagalli-01-bi-ecommerce-dashboard](https://Nagalli-01-bi-ecommerce-dashboard.hf.space) e o código está disponível no GitHub.

Com isso, a Sprint 2 fica concluída com pipeline montada, transformação e modelagem implementadas, verificações de qualidade automatizadas e relatório em funcionamento. Obrigado."

---

## Resumo da Divisão

| Pessoa | Tempo | Conteúdo |
|--------|-------|----------|
| Pessoa 1 | ≈ 3min30s | Abertura + Pipeline (orquestrador, Medallion, reexecutabilidade) |
| Pessoa 2 | ≈ 4min | Transformação Silver (limpeza, enriquecimento) + Modelagem Gold (Star Schema, quality checks) |
| Pessoa 3 | ≈ 4min | Power BI + Streamlit (KPIs, rankings, mapa, evolução temporal) |
| Pessoa 4 | ≈ 3min30s | Encerramento (entregas, valor do processo, demonstração, números-chave) |

---

## Dicas de Apresentação

- **Tom de conversa, não de leitura.** O roteiro acima é um guia; adaptem a linguagem para soar natural.
- **Ensaiem as transições.** Cada passagem deve ser fluida: "Agora eu passo para..." ou "Com vocês, [Nome] para mostrar...".
- **Olhem para a plateia, não para os slides.** Os slides são apoio visual.
- **Cuidado com o tempo.** Se estiverem atrasando, cortem exemplos secundários, nunca os conceitos principais.
- **Preparem-se para perguntas típicas:**
  - "Por que Medallion e não um modelo relacional direto?" → Responder com separação de responsabilidades, reprocessamento seguro e padrão de indústria.
  - "Como escalariam isso para milhões de registros?" → Responder com migração para PySpark/Delta Lake em cluster, particionamento por data.
  - "Como lidariam com dados reais e LGPD?" → Responder com data masking, criptografia e colunas de consentimento.
  - "Por que Streamlit e Power BI juntos?" → Responder que Power BI atende o público de negócio com modelagem semântica, e Streamlit permite deploy web rápido e acessível.
  - "Como garantir a qualidade se os dados mudam todo dia?" → Responder com quality checks automatizados no pipeline e validação de schema na ingestão.

---

*Documento gerado para o projeto BI E-Commerce — Sprint 2. Junho de 2026.*
