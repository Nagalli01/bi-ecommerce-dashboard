#!/usr/bin/env python3
"""
BI E-Commerce Dashboard — Streamlit Professional
4 pages, dark theme, brand colors, calendar-aware, HF Spaces / Render / Streamlit Cloud
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

st.set_page_config(page_title="BI E-Commerce", page_icon="🛒", layout="wide")

# =====================================================================
# CSS — BRANDED DARK THEME
# =====================================================================
st.markdown("""
<style>
    /* ---- base ---- */
    .stApp, .main { background-color: #262626; }
    header[data-testid="stHeader"] { background-color: #1E1E1E; border-bottom: 1px solid #333333; }
    [data-testid="stSidebar"] { background-color: #1E1E1E; border-right: 1px solid #333333; }
    [data-testid="stSidebar"] * { color: #CCCCCC; }
    h1, h2, h3, h4 { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
    p, span, label, caption { color: #B0B0B0; }

    /* ---- select / multiselect ---- */
    div[data-baseweb="select"] > div { background-color: #323130; border-color: #444444; color: #FFFFFF; border-radius: 6px; }
    .stSelectbox label, .stMultiselect label { color: #A0A0A0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }

    /* ---- metric cards ---- */
    [data-testid="stMetric"] { background-color: #323130; border: 1px solid #1A1A1A; border-radius: 8px; padding: 14px 16px; }
    [data-testid="stMetric"] label { color: #9B9B9B; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.8px; }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }

    /* ---- dataframe / table ---- */
    [data-testid="stTable"] { background-color: #323130; border-radius: 8px; overflow: hidden; }
    .dataframe { font-family: 'Segoe UI', sans-serif; font-size: 0.82rem; }

    /* ---- divider ---- */
    hr { border-color: #3A3A3A; margin: 0.5rem 0; }

    /* ---- buttons ---- */
    .stButton button { background-color: #323130; color: #CCCCCC; border: 1px solid #444444; border-radius: 6px; padding: 4px 14px; font-size: 0.78rem; }
    .stButton button:hover { border-color: #4A90D9; color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# COLOR CONSTANTS
# =====================================================================
C = {
    "blue":      "#4A90D9",
    "green":     "#50B86C",
    "orange":    "#E8A838",
    "purple":    "#8B5CF6",
    "red":       "#E05A5A",
    "gold":      "#FFD700",
    "silver":    "#C0C0C0",
    "bronze":    "#CD7F32",
    "bg":        "#262626",
    "card":      "#323130",
    "border":    "#1A1A1A",
    "text":      "#FFFFFF",
    "text_sec":  "#B0B0B0",
    "grid":      "#3A3A3A",
}
PALETTE_15 = ["#4A90D9","#50B86C","#E8A838","#E05A5A","#8B5CF6",
              "#06B6D4","#F59E0B","#EC4899","#10B981","#6366F1",
              "#F97316","#14B8A6","#EF4444","#8B5CF6","#22D3EE"]

# =====================================================================
# DATABASE
# =====================================================================
@st.cache_resource
def get_conn():
    path = os.path.join(os.path.dirname(__file__), "bi_ecommerce.db")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "data", "bi_ecommerce.db")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bi_ecommerce.db")
    return sqlite3.connect(path, check_same_thread=False) if os.path.exists(path) else None

@st.cache_data(ttl=60)
def q(sql):
    conn = get_conn()
    return pd.read_sql(sql, conn) if conn else pd.DataFrame()

@st.cache_data(ttl=60)
def load_all():
    return (
        q("SELECT * FROM fact_vendas"),
        q("SELECT * FROM dim_vendedores"),
        q("SELECT * FROM dim_produtos"),
        q("SELECT * FROM dim_calendario ORDER BY data"),
    )

# =====================================================================
# HELPERS
# =====================================================================
def fmt(v):
    v = abs(v) if isinstance(v, (int, float)) else v
    if abs(v) >= 1e9: return f"R$ {v/1e9:,.2f} Bi"
    if abs(v) >= 1e6: return f"R$ {v/1e6:,.2f} Mi"
    if abs(v) >= 1e3: return f"R$ {v/1e3:,.0f} K"
    return f"R$ {v:,.2f}"

def fmt_int(v):
    return f"{int(v):,}".replace(",", ".")

def chart_layout(fig, height=380, showlegend=False):
    fig.update_layout(
        paper_bgcolor=C["bg"], plot_bgcolor=C["bg"], font_color=C["text_sec"],
        font_family="Segoe UI", height=height,
        margin=dict(l=0, r=24, t=0, b=0),
        xaxis=dict(gridcolor=C["grid"], zeroline=False),
        yaxis=dict(gridcolor=C["grid"], zeroline=False),
        showlegend=showlegend,
    )
    return fig

def kpi_section(color_hex, label, value):
    return st.markdown(f"""
    <div style="background:{C['card']};border:1px solid {C['border']};border-radius:8px;padding:12px 16px;position:relative;">
        <div style="position:absolute;left:0;top:0;bottom:0;width:4px;background:{color_hex};border-radius:8px 0 0 8px;"></div>
        <div style="margin-left:6px;">
            <div style="color:{C['text_sec']};font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">{label}</div>
            <div style="color:{C['text']};font-size:1.55rem;font-weight:700;">{value}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# LOAD DATA
# =====================================================================
fact, dim_vend, dim_prod, dim_cal = load_all()

if len(fact) == 0:
    st.error("Banco de dados nao encontrado. Execute o pipeline primeiro.")
    st.stop()

# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("## 🛒 BI E-Commerce")
    st.caption("Dashboard de Vendas")
    st.markdown("---")

    pagina = st.radio("", ["Visao Executiva", "Vendedores", "Produtos", "Geografica"],
                       label_visibility="collapsed")

    st.markdown("---")
    st.markdown("#### Filtros")

    anos_uniq = sorted(fact["data_pedido"].apply(lambda x: str(x)[:4]).unique())
    ano_sel = st.selectbox("Ano", ["Todos"] + anos_uniq)

    regioes_uniq = sorted(fact["regiao"].unique())
    regiao_sel = st.multiselect("Regiao", regioes_uniq, default=regioes_uniq,
                                placeholder="Todas")

    estados_uniq = sorted(fact["estado"].unique())
    estado_sel = st.multiselect("Estado", estados_uniq, default=[],
                                placeholder="Todos")

    cats_uniq = sorted(dim_prod["categoria"].unique())
    cat_sel = st.multiselect("Categoria", cats_uniq, default=[],
                             placeholder="Todas")

    if st.button("Limpar filtros", use_container_width=True):
        st.rerun()

    st.markdown("---")

# =====================================================================
# FILTER LOGIC
# =====================================================================
def filtrar(df):
    if ano_sel != "Todos":
        df = df[df["data_pedido"].apply(lambda x: str(x)[:4]) == ano_sel]
    if regiao_sel:
        df = df[df["regiao"].isin(regiao_sel)]
    if estado_sel:
        df = df[df["estado"].isin(estado_sel)]
    if cat_sel:
        prods = dim_prod[dim_prod["categoria"].isin(cat_sel)]["id_produto"].tolist()
        df = df[df["id_produto"].isin(prods)]
    return df

ff = filtrar(fact)

if len(ff) == 0:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

# shared KPIs
fat_total = ff["total_pedido"].sum()
ped_total = ff["pedido_id"].nunique()
tkt_medio = fat_total / ped_total if ped_total > 0 else 0
vend_total = ff["id_vendedor"].nunique()

# date range for header
all_dates = pd.to_datetime(ff["data_pedido"])
data_min = all_dates.min().strftime("%d/%m/%Y")
data_max = all_dates.max().strftime("%d/%m/%Y")

# =====================================================================
# HEADER
# =====================================================================
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0 12px 0;">
    <div>
        <span style="font-size:1.5rem;font-weight:700;color:{C['text']};">🛒 BI E-Commerce</span>
        <span style="color:{C['text_sec']};font-size:0.8rem;margin-left:16px;">Período: {data_min} — {data_max}</span>
    </div>
    <div style="display:flex;gap:24px;">
        <div><span style="color:{C['text_sec']};font-size:0.65rem;text-transform:uppercase;">Faturamento</span><br><span style="color:{C['blue']};font-weight:700;">{fmt(fat_total)}</span></div>
        <div><span style="color:{C['text_sec']};font-size:0.65rem;text-transform:uppercase;">Pedidos</span><br><span style="color:{C['text']};font-weight:700;">{fmt_int(ped_total)}</span></div>
        <div><span style="color:{C['text_sec']};font-size:0.65rem;text-transform:uppercase;">Ticket Medio</span><br><span style="color:{C['green']};font-weight:700;">{fmt(tkt_medio)}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# =====================================================================
# PAGE 1 — VISÃO EXECUTIVA
# =====================================================================
if pagina == "Visao Executiva":

    # ---- ROW 0: KPI CARDS ----
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_section(C["blue"],   "Faturamento",      fmt(fat_total))
    with c2: kpi_section(C["green"],  "Total Pedidos",    fmt_int(ped_total))
    with c3: kpi_section(C["blue"],   "Ticket Medio",     fmt(tkt_medio))
    with c4: kpi_section(C["orange"], "Vendedores",       vend_total)

    # ---- ROW 1: FAT. ESTADO + FAT. REGIÃO ----
    st.markdown("---")
    cr, cl = st.columns([1, 1])
    with cr:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Faturamento por Estado</h4>", unsafe_allow_html=True)
        dfe = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfe, x="total_pedido", y="estado", orientation="h",
                     color_discrete_sequence=[C["blue"]],
                     labels={"total_pedido": "", "estado": ""})
        chart_layout(fig, height=420)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cl:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Faturamento por Regiao</h4>", unsafe_allow_html=True)
        dfr = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfr, x="total_pedido", y="regiao", orientation="h",
                     color_discrete_sequence=[C["green"]],
                     labels={"total_pedido": "", "regiao": ""})
        chart_layout(fig, height=420)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- ROW 2: TOP 10 MUNICIPIOS + RANKING VENDEDORES (TABLE) ----
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Top 10 Municipios</h4>", unsafe_allow_html=True)
        dm = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(10)
        fig = go.Figure(go.Bar(y=dm["municipio"], x=dm["total_pedido"], orientation="h",
                               marker=dict(color=C["orange"]),
                               text=[fmt(v) for v in dm["total_pedido"]],
                               textposition="outside", textfont=dict(color=C["text_sec"], size=9)))
        chart_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Ranking Vendedores</h4>", unsafe_allow_html=True)
        dv_r = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_v", "_d"))
        rank = dv_r.groupby(["nome", "regiao_d"], as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        rank.insert(0, "#", range(1, len(rank)+1))
        rank["Faturamento"] = rank["total_pedido"].apply(fmt)
        rank["%"] = (rank["total_pedido"] / rank["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
        display = rank[["#", "nome", "regiao_d", "Faturamento", "%"]].rename(
            columns={"nome": "Vendedor", "regiao_d": "Regiao"})
        st.dataframe(display, use_container_width=True, hide_index=True, height=380)

    # ---- ROW 3: EVOLUÇÃO MENSAL (FULL WIDTH) ----
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Evolucao Mensal do Faturamento</h4>", unsafe_allow_html=True)

    ff_dates = pd.to_datetime(ff["data_pedido"])
    cal = dim_cal[["data", "nome_mes", "mes_num", "ano"]].copy()
    cal["data"] = pd.to_datetime(cal["data"])
    fe = ff.copy()
    fe["data_pedido_dt"] = ff_dates
    fe["ano_mes"] = fe["data_pedido_dt"].dt.to_period("M").astype(str)

    dmes = fe.groupby("ano_mes", as_index=False).agg(
        total=("total_pedido", "sum"),
        pedidos=("pedido_id", "nunique"),
        min_dt=("data_pedido_dt", "min"),
    ).sort_values("ano_mes")
    dmes["label"] = dmes["min_dt"].dt.strftime("%b/%y")
    dmes["cresc"] = dmes["total"].pct_change()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dmes["label"], y=dmes["total"], mode="lines+markers+text",
                             line=dict(color=C["blue"], width=2.5),
                             fill="tozeroy", fillcolor="rgba(74,144,217,0.10)",
                             marker=dict(size=6, color=C["blue"]),
                             text=[fmt(v) for v in dmes["total"]],
                             textposition="top center", textfont=dict(color=C["text_sec"], size=8)))
    chart_layout(fig, height=320)
    fig.update_xaxes(tickangle=-30, tickfont_size=9)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # MoM indicator
    if len(dmes) >= 2:
        last_cresc = dmes["cresc"].iloc[-1]
        if pd.notna(last_cresc):
            ccor = C["green"] if last_cresc >= 0 else C["red"]
            ss = "▲" if last_cresc >= 0 else "▼"
            st.caption(f"Crescimento mensal: {ss} {abs(last_cresc)*100:.1f}% vs mes anterior")

# =====================================================================
# PAGE 2 — VENDEDORES
# =====================================================================
elif pagina == "Vendedores":

    dv = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_v", "_d"))
    dvf = dv.groupby(["id_vendedor", "nome", "regiao_d"], as_index=False)["total_pedido"].sum() \
            .sort_values("total_pedido", ascending=False)
    dvf["rank"] = range(1, len(dvf)+1)
    top1 = dvf.iloc[0] if len(dvf) > 0 else None
    fat_med = fat_total / vend_total if vend_total > 0 else 0

    # ---- ROW 0: 2 KPIs ----
    c1, c2 = st.columns(2)
    with c1:
        nome_top = top1["nome"] if top1 is not None else "-"
        kpi_section(C["gold"], "Melhor Vendedor", f"{nome_top} — {fmt(top1['total_pedido']) if top1 is not None else ''}")
    with c2:
        kpi_section(C["green"], "Fat. Medio por Vendedor", fmt(fat_med))

    # ---- ROW 1: RANKING COMPLETO (FULL WIDTH, CONDITIONAL FORMAT) ----
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Ranking Completo</h4>", unsafe_allow_html=True)

    def medal(r):
        if r == 1: return "🥇 1"
        if r == 2: return "🥈 2"
        if r == 3: return "🥉 3"
        return str(r)

    rank_display = dvf.copy()
    rank_display["Faturamento"] = rank_display["total_pedido"].apply(fmt)
    rank_display["%"] = (rank_display["total_pedido"] / rank_display["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
    rank_display["#"] = rank_display["rank"].apply(medal)
    tbl = rank_display[["#", "nome", "regiao_d", "Faturamento", "%"]].rename(
        columns={"#": "#", "nome": "Vendedor", "regiao_d": "Regiao"})

    st.dataframe(tbl, use_container_width=True, hide_index=True, height=520,
                 column_config={"#": st.column_config.TextColumn(width="small"),
                                "Vendedor": st.column_config.TextColumn(width="large"),
                                "Regiao": st.column_config.TextColumn(width="medium"),
                                "Faturamento": st.column_config.TextColumn(width="medium"),
                                "%": st.column_config.TextColumn(width="small")})

    # ---- ROW 2: DONUT + BARRAS EMPILHADAS ----
    st.markdown("---")
    cd, cr2 = st.columns([1, 1])
    with cd:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Participacao %</h4>", unsafe_allow_html=True)
        fig = go.Figure(go.Pie(labels=dvf["nome"], values=dvf["total_pedido"], hole=0.55,
                               textinfo="percent", textfont=dict(size=10, color=C["text"]),
                               marker=dict(colors=PALETTE_15)))
        chart_layout(fig, height=380)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cr2:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Fat. por Regiao do Vendedor</h4>", unsafe_allow_html=True)
        dv_stacked = dvf.groupby(["regiao_d", "nome"], as_index=False)["total_pedido"].sum()
        fig = px.bar(dv_stacked, x="total_pedido", y="regiao_d", color="nome",
                     orientation="h", color_discrete_sequence=PALETTE_15,
                     labels={"total_pedido": "", "regiao_d": ""})
        chart_layout(fig, height=380, showlegend=True)
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, font_size=8, title_text=""))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# PAGE 3 — PRODUTOS
# =====================================================================
elif pagina == "Produtos":

    fc = ff.merge(dim_prod, on="id_produto", how="left")

    # ---- ROW 0: KPIs ----
    c1, c2, c3 = st.columns(3)
    with c1: kpi_section(C["purple"], "Categorias", dim_prod["categoria"].nunique())
    with c2: kpi_section(C["purple"], "Preco Medio", fmt(dim_prod["preco_venda"].mean()))
    with c3: kpi_section(C["purple"], "Produtos Vendidos", ff["id_produto"].nunique())

    # ---- ROW 1: FAT. CATEGORIA + TOP 10 PRODUTOS ----
    st.markdown("---")
    cc, cp = st.columns([1, 1])
    with cc:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Faturamento por Categoria</h4>", unsafe_allow_html=True)
        dc = fc.groupby("categoria", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True)
        fig = go.Figure(go.Bar(y=dc["categoria"], x=dc["total_pedido"], orientation="h",
                               marker=dict(color=C["purple"]),
                               text=[fmt(v) for v in dc["total_pedido"]],
                               textposition="outside", textfont=dict(color=C["text_sec"], size=10)))
        chart_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cp:
        st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Top 10 Produtos</h4>", unsafe_allow_html=True)
        dpt = fc.groupby("nome_produto", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(10)
        fig = go.Figure(go.Bar(y=dpt["nome_produto"], x=dpt["total_pedido"], orientation="h",
                               marker=dict(color=C["purple"]),
                               text=[fmt(v) for v in dpt["total_pedido"]],
                               textposition="outside", textfont=dict(color=C["text_sec"], size=9)))
        chart_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- ROW 2: DETALHAMENTO ----
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Detalhamento por Categoria</h4>", unsafe_allow_html=True)
    dd = fc.groupby("categoria").agg(
        Faturamento=("total_pedido", "sum"),
        Pedidos=("pedido_id", "nunique"),
        Ticket=("total_pedido", "mean"),
        Quantidade=("quantidade", "sum"),
    ).reset_index()
    dd["Fat. Formatado"] = dd["Faturamento"].apply(fmt)
    dd["Ticket Formatado"] = dd["Ticket"].apply(fmt)
    st.dataframe(dd[["categoria", "Fat. Formatado", "Pedidos", "Ticket Formatado", "Quantidade"]].rename(
        columns={"categoria": "Categoria", "Fat. Formatado": "Faturamento",
                 "Ticket Formatado": "Ticket Medio", "Quantidade": "Qtd. Vendida"}),
        use_container_width=True, hide_index=True, height=280)

# =====================================================================
# PAGE 4 — GEOGRÁFICA (NEW)
# =====================================================================
elif pagina == "Geografica":

    # ---- FAT. POR ESTADO (FULL WIDTH) ----
    st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Faturamento por Estado</h4>", unsafe_allow_html=True)
    dfe2 = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    fig = go.Figure(go.Bar(y=dfe2["estado"], x=dfe2["total_pedido"], orientation="h",
                           marker=dict(color=C["blue"]),
                           text=[fmt(v) for v in dfe2["total_pedido"]],
                           textposition="outside", textfont=dict(color=C["text_sec"], size=10)))
    chart_layout(fig, height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- FAT. POR REGIAO (FULL WIDTH) ----
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Faturamento por Regiao</h4>", unsafe_allow_html=True)
    dfr2 = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    fig = go.Figure(go.Bar(y=dfr2["regiao"], x=dfr2["total_pedido"], orientation="h",
                           marker=dict(color=C["green"]),
                           text=[fmt(v) for v in dfr2["total_pedido"]],
                           textposition="outside", textfont=dict(color=C["text_sec"], size=11)))
    chart_layout(fig, height=340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- TOP 15 MUNICIPIOS (FULL WIDTH) ----
    st.markdown("---")
    st.markdown(f"<h4 style='color:{C['text']};margin:0 0 8px 0;'>Top 15 Municipios</h4>", unsafe_allow_html=True)
    dm2 = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(15)
    fig = go.Figure(go.Bar(y=dm2["municipio"], x=dm2["total_pedido"], orientation="h",
                           marker=dict(color=C["orange"]),
                           text=[fmt(v) for v in dm2["total_pedido"]],
                           textposition="outside", textfont=dict(color=C["text_sec"], size=9)))
    chart_layout(fig, height=460)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# FOOTER
# =====================================================================
st.markdown("---")
st.caption(f"Dados simulados — Pipeline Medallion (Bronze → Silver → Gold → Star Schema) | "
           f"250 produtos · 1.500 clientes · 8.000 pedidos · Faturamento: {fmt(fat_total)} | "
           f"[GitHub](https://github.com/Nagalli01/bi-ecommerce-dashboard)")
