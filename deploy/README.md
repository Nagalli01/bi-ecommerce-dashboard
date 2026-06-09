---
title: Nexus Dashboard
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Nexus Dashboard

Dashboard profissional de BI para analise de vendas de e-commerce.

## Dataset Simulado

- 1.500 clientes · 250 produtos · 8.000 pedidos · R$ 179,6 Mi em faturamento
- Arquitetura Medallion: Bronze -> Silver -> Gold -> Star Schema
- 5 tabelas em SQLite, pipeline ETL completo

## 4 Paginas

| Pagina | Conteudo |
|--------|----------|
| **Visao Executiva** | KPIs (Fat. / Pedidos / Ticket / Vendedores), Fat. por Estado + Regiao, Top 10 Municipios, Ranking Vendedores, Evolucao Mensal com crescimento MoM |
| **Vendedores** | Melhor Vendedor, Ranking completo com medalhas (🥇🥈🥉), Participacao % (Donut), Barras Empilhadas por regiao |
| **Produtos** | Categorias / Preco Medio / Produtos Vendidos, Fat. por Categoria, Top 10 Produtos, Detalhamento |
| **Geografica** | Fat. por Estado, Fat. por Regiao, Top 15 Municipios |

## Funcionalidades

- Tema dark profissional com paleta de cores por tipo de grafico
- Header com KPIs flutuantes e range de datas
- Filtros na sidebar: ano, regiao, estado, categoria
- Loading states e tratamento de dados vazios
- Metricas de crescimento mensal (MoM)
- Graficos interativos (Plotly)

## Tech Stack

Python · Streamlit · Plotly · Pandas · SQLite · Docker
