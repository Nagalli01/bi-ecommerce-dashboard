---
title: BI E-Commerce Dashboard
emoji: 🛒
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# BI E-Commerce Dashboard

Dashboard interativo de analise de vendas de e-commerce.

## Dataset

- 1500 clientes, 250 produtos, 8000 pedidos
- Faturamento: R$ 179,6M
- 5 tabelas em Star Schema (SQLite)

## Paginas

1. **Visao Executiva** — KPIs, faturamento por estado, ranking vendedores, evolucao mensal
2. **Vendedores** — performance individual, participacao, ranking completo
3. **Produtos & Categorias** — faturamento por categoria, top produtos, detalhamento

## Tech Stack

- Python + Streamlit + Plotly
- SQLite (portatil, sem banco externo)
- Dark theme (#1B1B1B / #4A90D9)
