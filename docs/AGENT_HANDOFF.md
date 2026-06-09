# Nexus Dashboard — Handoff para Agente de Melhoria

---

## 1. Visao Geral

**Projeto:** Dashboard de BI para e-commerce de medio porte (Nexus).
**Objetivo:** Transformar dados transacionais em dashboard executivo orientado a decisao, com aparencia SaaS Enterprise.
**Status atual:** v3.0 — funcional, identidade visual razoavel (7.5/10), mas ainda com sinais de "feito em Streamlit".
**Meta:** 9/10 — produto com nivel profissional que nao pareca template de IA.

---

## 2. Arquivos Relevantes

| Arquivo | Descricao |
|---------|-----------|
| `deploy/app.py` | Dashboard Streamlit principal (~500 linhas). Este e o arquivo a ser melhorado. |
| `deploy/data/*.csv` | 5 CSVs com os dados (fact_vendas 8000 linhas, dim_clientes 1500, dim_produtos 250, dim_calendario 525, dim_vendedores 15) |
| `deploy/Dockerfile` | Docker image para Hugging Face Spaces |
| `deploy/requirements.txt` | Dependencias: streamlit, pandas, plotly |
| `deploy/README.md` | Metadados do Hugging Face Space |
| `src/00_generate_data.py` | Gerador de dados sinteticos (seed 42, 1500 clientes, 250 produtos, 8000 pedidos) |
| `src/run_pipeline.py` | Pipeline Medallion completo (Bronze -> Silver -> Gold -> Star Schema) |
| `docs/DEPLOY_GUIDE.md` | Guia de deploy em HF Spaces / Render / Streamlit Cloud |
| `powerbi/dashboard_completo.md` | Especificacao original do dashboard (Power BI) |

---

## 3. Tech Stack

| Tecnologia | Versao | Uso |
|-----------|--------|-----|
| Python | 3.12 | Linguagem |
| Streamlit | >=1.30 | Framework UI |
| Pandas | >=2.0 | Manipulacao de dados |
| Plotly | >=5.18 | Graficos interativos |
| Docker | — | Container no HF Spaces |
| Hugging Face Spaces | — | Hosting (sdk: docker) |

**Banco:** CSV (nao SQLite, nao MySQL) — os dados sao carregados com `pd.read_csv()`.

---

## 4. Estrutura do `deploy/app.py` (atual)

```
1-15   : Imports + st.set_page_config
16-80  : CSS injection (~65 linhas)
81-90  : Color system constants
91-100 : Data loading (load_csv, load_all)
101-165: Helpers (fmt, fmt_int, delta_badge, chart_config, kpi_card, smart_kpi, section_title, insight_card)
166-175: Data load
176-225: Sidebar (NEXUS logo, MENU radio, FILTROS, PERIODO date inputs, ACOES buttons)
226-250: Filter logic + shared KPIs + previous period deltas + best seller/region + MoM
251-280: TOP KPI BAND (smart_kpi x5: Crescimento, Meta, Melhor Vendedor, Melhor Regiao, Alerta)
281-340: PAGE 1 — Visao Executiva (KPIs+deltas, 3 insights, Fat.Estado+Regiao, Ranking Vendedores, Top/Bottom Municipios, Evolucao)
341-385: PAGE 2 — Vendedores (KPIs, Ranking, Donut, Stacked bars)
386-420: PAGE 3 — Produtos (KPIs, Categorias, Top 10 Produtos, Detalhamento)
421-445: PAGE 4 — Geografica (Estado, Regiao, Top 15 Municipios)
446-450: Footer
```

---

## 5. Paleta de Cores

```python
C = {
    "brand":       "#7C3AED",  # primary violet
    "brand_l":     "#A78BFA",
    "second":      "#06B6D4",  # cyan accent
    "second_l":    "#22D3EE",
    "success":     "#22C55E",  # green
    "warn":        "#F59E0B",  # amber
    "danger":      "#EF4444",  # red
    "bg":          "#0B1120",  # page background (deep blue-black)
    "sidebar":     "#111827",  # sidebar background
    "surface":     "#1E293B",  # card/surface background
    "border":      "#334155",  # borders
    "text":        "#F1F5F9",  # primary text
    "text_sec":    "#94A3B8",  # secondary text
    "text_muted":  "#64748B",  # muted labels
}
```

**Fonte:** Inter (Google Fonts), carregada via `@import`.

---

## 6. Dados (Schema)

### fact_vendas (8000 linhas)
```
pedido_id, id_cliente, id_produto, data_pedido (DATE), id_vendedor,
quantidade (1-4), valor_frete (5-35), total_pedido (calculado),
municipio, estado, regiao
```
Faturamento total: ~R$ 31,5 Mi | Periodo: 2025-01-01 a 2026-06-09

### dim_clientes (1500)
`id_cliente, nome, cidade, estado, regiao`

### dim_produtos (250)
`id_produto, nome_produto, categoria, preco_venda`
Categorias: Smartphones, Notebooks, Acessorios, Audio, Tablets, Monitores, Perifericos, Armazenamento

### dim_calendario (525 dias)
`data, dia, mes, nome_mes (Janeiro..Dezembro), mes_num, trimestre, ano`

### dim_vendedores (15)
`id_vendedor, nome, regiao`
Cada vendedor tem uma regiao de atuacao.

**ATENCAO:** `fact_vendas.regiao` e `dim_vendedores.regiao` sao colunas diferentes! A do fato e a regiao da venda (baseada no cliente). A da dimensao e a regiao do vendedor. No merge, usar `suffixes=("_v", "_d")` para evitar colisao.

---

## 7. Filtros Disponiveis

| Filtro | Tipo | Local |
|--------|------|-------|
| Ano | `st.selectbox` | Sidebar |
| Regiao | `st.multiselect` (vazio = Todas) | Sidebar |
| Estado | `st.multiselect` (vazio = Todos) | Sidebar |
| Categoria | `st.multiselect` (vazio = Todas) | Sidebar |
| Periodo inicio | `st.date_input` | Sidebar |
| Periodo fim | `st.date_input` | Sidebar |
| Limpar / Atualizar | `st.button` x2 | Sidebar |

---

## 8. Problemas Conhecidos (a melhorar)

### 8.1 Visuais / UI
1. **Graficos ainda ocupam muito espaco vertical** — alturas de 240-340px poderiam ser 200-280px.
2. **Falta diferenciacao visual entre secoes** — tudo no mesmo plano, mesmo com sombras.
3. **Cards de KPI sem icones** — a funcao `kpi_card()` atual nao tem icones SVG (foram removidos).
4. **Sidebar sem scroll** — overflow hidden forcado, mas com muitos filtros pode cortar conteudo.
5. **Botao de colapso usa Unicode** `◀/▶` — frágil, depende de fallback de fonte.
6. **Top KPI band usa emojis** — `📈🎯🏆🌎⚡` podem nao renderizar em todos os SOs.

### 8.2 Dados / Metricas
1. **Delta do periodo anterior** calcula janela de mesma duracao antes do inicio do filtro — se nao houver dados, retorna None.
2. **Crescimento MoM** usa apenas os ultimos 2 meses do periodo filtrado.
3. **Meta de R$ 40 Mi** e hardcoded — sem relacao com dados reais.
4. **Insights automaticos** sao basicos (3 frases fixas) — poderiam ser mais dinamicos.

### 8.3 Tecnico
1. **Tudo em um arquivo** (~500 linhas) — sem separacao de componentes.
2. **CSS inline via st.markdown** — sem arquivo .css externo.
3. **Sem testes automatizados**.
4. **Cache TTL fixo de 600s** — poderia ser mais inteligente.

---

## 9. Diretrizes para Melhoria

### Prioridade Alta
- [ ] Reduzir altura dos graficos em mais 15-20% para aumentar densidade de informacao
- [ ] Adicionar icones SVG de volta aos KPI cards (via funcao `kpi_card`)
- [ ] Criar hierarquia visual mais clara entre secoes (bordas sutis, backgrounds levemente diferentes)
- [ ] Melhorar os insights automaticos — gerar frases realmente uteis com base nos dados
- [ ] Substituir emojis da top KPI band por icones SVG ou CSS puro

### Prioridade Media
- [ ] Separar CSS em constante Python multi-linha para facilitar manutencao
- [ ] Adicionar tooltips explicativas nos filtros
- [ ] Criar funcao para exportacao de dados (CSV/Excel)
- [ ] Adicionar indicador de "periodo comparativo" nos cards de KPI
- [ ] Melhorar responsividade para telas menores

### Prioridade Baixa
- [ ] Separar paginas em modulos Python
- [ ] Adicionar testes com `streamlit.testing`
- [ ] Documentar funcoes com docstrings
- [ ] Adicionar suporte a temas (claro/escuro)

---

## 10. Funcoes-Chave que o Agente Precisa Conhecer

### `chart_config(fig, height=300, showlegend=False)`
Configura layout padrao de qualquer grafico Plotly. Aplica:
- Fundo transparente, sem gridlines
- Fonte Inter, cor `text_sec`
- Margens zero
- Hover tooltip customizado

### `kpi_card(label, value, delta_str=None)`
Renderiza um card de metrica com fundo `surface`, borda, sombra.
`delta_str` e opcional — HTML com indicador de variacao.

### `smart_kpi(icon, label, value, sub="")`
Card compacto para a faixa superior de KPIs inteligentes.

### `insight_card(icon, text, color)`
Card de insight com borda esquerda colorida.

### `filtrar(df)`
Aplica todos os filtros (ano, regiao, estado, categoria, data_ini, data_fim) em um DataFrame.

### `delta_badge(current, previous)`
Retorna HTML com % de variacao colorida (verde positivo, vermelho negativo).

---

## 11. Variaveis Globais Importantes

```python
ff          # DataFrame fact_vendas filtrado
fat_total   # float — faturamento total no periodo
ped_total   # int — numero de pedidos unicos
tkt_medio   # float — ticket medio
vend_total  # int — vendedores distintos
fat_prev    # float ou None — faturamento no periodo anterior (para delta)
ped_prev    # int ou None — pedidos no periodo anterior
tkt_prev    # float ou None — ticket medio no periodo anterior
mom_growth  # float ou None — crescimento mes-a-mes (%)
top_seller_name  # str — nome do melhor vendedor
top_seller_pct   # float — % do faturamento do melhor vendedor
top_reg_name     # str — nome da melhor regiao
top_reg_pct      # float — % do faturamento da melhor regiao
dias_filtro      # int — dias entre data_ini e data_fim
```

---

## 12. Como Testar Localmente

```bash
cd C:\dev\projetoInt\bi_ecommerce\deploy
streamlit run app.py --server.port 8501
```

Ou para regenerar dados e testar tudo:
```bash
cd C:\dev\projetoInt\bi_ecommerce
python src/run_pipeline.py
```

---

## 13. Deploy

O projeto esta hospedado em:
- **HF Spaces:** https://Nagalli-01-bi-ecommerce-dashboard.hf.space
- **GitHub:** https://github.com/Nagalli01/bi-ecommerce-dashboard

Para deploy: commit na branch `main` do repositorio `deploy/` e push — o HF Spaces faz build automatico via Docker.

**IMPORTANTE:** O Dockerfile usa `COPY data/ data/` para incluir os CSVs na imagem. Nao remover essa linha.

---

## 14. Restricoes

- Nao usar bibliotecas externas alem de streamlit, pandas, plotly (para manter deploy simples)
- Nao adicionar dependencia de banco de dados (SQLite/MySQL) — usar apenas CSVs
- Nao alterar o schema dos dados
- Manter compatibilidade com Hugging Face Spaces (Docker SDK)
- Manter as 4 paginas: Visao Executiva, Vendedores, Produtos, Geografica

---

## 15. Exemplo do que um Dashboard 9/10 entrega

- Ao abrir, o usuario entende a situacao do negocio em **menos de 10 segundos**
- A faixa superior responde: estamos crescendo? batemos a meta? quem lidera? ha alertas?
- Os KPIs mostram nao so o valor absoluto, mas a **tendencia** (subindo/caindo)
- Insights automaticos destacam **fatos nao obvios** (nao apenas "X representa Y%")
- Graficos sao **compactos e densos** — cada pixel entrega informacao
- A hierarquia visual guia o olhar: KPIs -> Insights -> Graficos -> Tabelas
- Nao ha elementos distrativos (bordas desnecessarias, cores vibrantes, espacos vazios)
- O tema e consistente em todas as paginas
