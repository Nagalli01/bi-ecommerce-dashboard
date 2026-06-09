# Roteiro de Apresentação — Sprint 2 · BI E-Commerce

**Duração total:** ~10 minutos
**Equipe:** 4 integrantes
**Formato:** Apresentação oral em grupo, tom de conversa, sem leitura de slides
**Contexto:** Sprint 2 — Transformar o projeto em um processo completo e repetível

---

## Pessoa 1 (≈ 2min30s) — Abertura + Pipeline (Engenharia de Dados)

"Boa tarde, professor. Nós vamos apresentar a Sprint 2 do BI E-Commerce, seguindo o fluxo: primeiro a pipeline de dados, depois a transformação e modelagem, e por fim o relatório.

Na Sprint 2, o objetivo foi transformar o projeto em um processo completo e repetível — sair de notebooks isolados e passar a ter uma esteira organizada. Nós criamos um orquestrador em Python, o `run_pipeline.py`, que encadeia seis etapas em sequência: geração dos dados, validação de schema, ingestão na Bronze, transformação na Silver, modelagem na Gold com Star Schema, e verificações de qualidade. Se qualquer etapa falhar, o pipeline para imediatamente.

Essa pipeline implementa a arquitetura Medallion, padrão de indústria para lakehouses. São três camadas: Bronze com os dados brutos preservados como chegaram, Silver com limpeza e padronização, e Gold com o modelo dimensional pronto para consumo analítico. A pipeline é reexecutável: tratamos escrita de tabelas para evitar falhas do tipo 'arquivo já existe' e validamos schema na entrada. Basta rodar um comando e o ambiente se reconstrói.

Pra dar noção de volume: são 1.500 clientes, 250 produtos e 8.000 pedidos cobrindo 10 estados, 5 regiões e 15 vendedores. O pipeline inteiro roda em segundos.

Agora eu passo pra próxima pessoa, que vai explicar a transformação e modelagem."

---

## Pessoa 2 (≈ 2min30s) — Transformação (Silver) + Modelagem (Gold)

"Continuando, eu vou falar da transformação e modelagem, o coração técnico da Sprint 2.

Na Silver, aplicamos regras de padronização e qualidade. Nomes e cidades em Title Case — 'joão da silva' vira 'João Da Silva'. Estados em caixa alta, e-mails em minúsculas. Removemos produtos com preço inválido e deduplicamos registros. A transformação principal foi o enriquecimento dos pedidos: os dados brutos não têm o valor total. Fizemos JOIN com a tabela de produtos e calculamos `total_pedido` como quantidade vezes preço de venda mais frete. Isso transforma um registro incompleto numa medida financeira pronta pra análise.

Na Gold, modelamos um Star Schema — o Esquema Estrela — com quatro dimensões e uma tabela fato. dim_clientes responde 'quem comprou', dim_produtos 'o que foi comprado', dim_calendario — gerada programaticamente com 731 dias e hierarquias de mês, trimestre e ano — responde 'quando', e dim_vendedores mapeia os 15 vendedores com nome e região, 'quem vendeu'. A fact_vendas concentra as medidas com chaves estrangeiras pra cada dimensão.

Incluímos também vendedor, região e município como atributos degenerados na fato, permitindo responder perguntas como: qual região vende mais, ranking de vendedores, top municípios.

E tudo isso é validado por quality checks automatizados: conferimos contagens, nulos, integridade referencial com LEFT ANTI JOINs e métricas de negócio. Resultado: zero nulos, 100% de integridade, faturamento de R$ 179,6 milhões, 8.000 pedidos e ticket médio de R$ 22.447.

Passo agora pra próxima pessoa mostrar o relatório."

---

## Pessoa 3 (≈ 2min30s) — Power BI + Dashboard

"Agora a parte de visualização, onde o valor fica claro pra quem toma decisão.

Entregamos duas frentes: um relatório no Power BI Desktop consumindo o modelo Gold via MySQL com medidas DAX, e um dashboard web em Streamlit publicado online. Ambos seguem estética profissional: fundo escuro, indicadores claros, leitura rápida.

No topo, KPIs em cards: faturamento total, total de pedidos, ticket médio e total de vendedores. São medidas DAX, então respondem a qualquer filtro automaticamente.

Na parte central, temos análise geográfica: um mapa coroplético de faturamento por estado — implementado com Python visuals no Power BI — e faturamento por região. Os dados mostram Sudeste liderando com R$ 55 milhões, Nordeste logo atrás com R$ 53,8 milhões. Temos ranking de vendedores — top performer é Juliana Alves com R$ 12,7 milhões — e Top 10 de municípios.

O dashboard Streamlit complementa com 4 páginas interativas: Visão Executiva, Vendedores, Produtos & Categorias e Análise Geográfica, com filtros por ano, região, estado e categoria, e cross-filtering entre gráficos. Está publicado no Hugging Face Spaces, acessível por qualquer navegador.

Incluímos também evolução temporal do faturamento por mês ao longo de 2023 e 2024, permitindo identificar sazonalidades como picos de Black Friday e Natal. O ponto central: tudo está alimentado por uma pipeline automatizada — o relatório é o resultado final de um processo de engenharia de dados, não algo manual.

Passo pra última pessoa encerrar."

---

## Pessoa 4 (≈ 2min30s) — Encerramento: entregas e valor

"Para encerrar, vou resumir as entregas e o valor do que foi construído.

Ao final da Sprint 2, temos um projeto completo estruturado como fluxo real de engenharia de dados. Primeiro, uma pipeline orquestrada em Python com seis etapas, tratamento de erros e medição de tempo. Segundo, camadas Medallion bem definidas: Bronze para ingestão, Silver para qualidade, Gold com Star Schema. Terceiro, relatório Power BI e dashboard Streamlit consumindo o modelo Gold. Quarto, quality checks automatizados com 100% de integridade referencial e zero nulos.

O diferencial: não entregamos só um painel, entregamos um processo. Se os dados forem recarregados, a pipeline roda com um comando e o relatório continua consistente — padrão próximo do que se espera em um cenário profissional.

Se quiser uma demonstração rápida, podemos executar `python src/run_pipeline.py` e mostrar as seis etapas rodando no terminal, com o relatório de qualidade sendo gerado. Depois abrimos o dashboard Streamlit pra ver KPIs, rankings e gráficos interativos. O dashboard está em huggingface.co/spaces/Nagalli-01-bi-ecommerce-dashboard e o código no GitHub.

Resumindo: 1.500 clientes, 250 produtos, 8.000 pedidos, 15 vendedores, 5 regiões, R$ 179,6 milhões de faturamento, ticket médio de R$ 22.447. Pipeline, transformação, modelagem e relatório funcionando de ponta a ponta. Obrigado."

---

## Resumo da Divisão

| Pessoa | Tempo | Conteúdo |
|--------|-------|----------|
| Pessoa 1 | ≈ 2min30s | Abertura + Pipeline (orquestrador, Medallion, reexecutabilidade) |
| Pessoa 2 | ≈ 2min30s | Silver (padronização, enriquecimento) + Gold (Star Schema, quality checks) |
| Pessoa 3 | ≈ 2min30s | Power BI + Streamlit (KPIs, rankings, mapa, evolução temporal) |
| Pessoa 4 | ≈ 2min30s | Encerramento (entregas, valor do processo, demonstração, números) |

---

## Dicas de Apresentação

- **Tom de conversa, não de leitura.** O roteiro é um guia; adaptem para soar natural.
- **Ensaiem as transições.** "Agora eu passo para..." ou "Com vocês, [Nome]...".
- **Olhem para a plateia, não para os slides.**
- **Cuidado com o tempo.** Cortem exemplos secundários se atrasar, nunca os conceitos principais.
- **Preparem-se para perguntas:**
  - "Por que Medallion?" → Separação de responsabilidades, reprocessamento seguro, padrão de indústria.
  - "Como escalariam?" → PySpark/Delta Lake em cluster, particionamento por data.
  - "E LGPD com dados reais?" → Data masking, criptografia, colunas de consentimento.
  - "Por que Streamlit e Power BI?" → Power BI pro público de negócio, Streamlit pra deploy web acessível.
  - "Qualidade com dados mutáveis?" → Quality checks automatizados no pipeline e validação de schema.

---

*Documento gerado para o projeto BI E-Commerce — Sprint 2. Junho de 2026.*
