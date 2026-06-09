#!/usr/bin/env python3
"""
Dashboard BI E-Commerce — Versao Web (SQLite)
Deploy: Hugging Face Spaces, Render, or local via Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sqlite3
import os

# =====================================================================
# CONFIG
# =====================================================================
st.set_page_config(page_title="BI E-Commerce", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")

# =====================================================================
# CSS DARK MODE
# =====================================================================
st.markdown("""
<style>
    .stApp { background-color: #1B1B1B; }
    [data-testid="stSidebar"] { background-color: #141414; border-right: 1px solid #2D2D2D; }
    [data-testid="stSidebar"] * { color: #AAAAAA; }
    [data-testid="stMetric"] {
        background-color: #2D2D2D; border: 1px solid #3A3A3A; border-radius: 10px; padding: 16px;
    }
    [data-testid="stMetric"] label { color: #888888 !important; font-size: 0.8rem; }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 700; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Segoe UI', sans-serif; }
    p, span, div { color: #AAAAAA; }
    .stSelectbox label, .stMultiselect label { color: #AAAAAA !important; }
    div[data-baseweb="select"] > div { background-color: #2D2D2D; border-color: #3A3A3A; color: #FFFFFF; }
    .stDataFrame { background-color: #2D2D2D; }
    .stDataFrame thead th { background-color: #2D2D2D !important; color: #FFFFFF !important; }
    .stDataFrame tbody td { background-color: #1B1B1B !important; color: #AAAAAA !important; }
    header[data-testid="stHeader"] { background-color: #1B1B1B; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# BANCO DE DADOS (SQLite auto-detection)
# =====================================================================
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bi_ecommerce.db")

@st.cache_resource
def get_conn():
    if os.path.exists(DB_PATH):
        return sqlite3.connect(DB_PATH, check_same_thread=False)
    return None

@st.cache_data(ttl=30)
def query_df(sql):
    conn = get_conn()
    if conn:
        return pd.read_sql(sql, conn)
    return pd.DataFrame()

# =====================================================================
# LOAD DATA
# =====================================================================
fact = query_df("SELECT * FROM fact_vendas")
dim_cli = query_df("SELECT * FROM dim_clientes")
dim_prod = query_df("SELECT * FROM dim_produtos")
dim_cal = query_df("SELECT * FROM dim_calendario")
dim_vend = query_df("SELECT * FROM dim_vendedores")

# =====================================================================
# SIDEBAR
# =====================================================================
st.sidebar.markdown("## 🛒 BI E-Commerce")
st.sidebar.markdown("---")

pagina = st.sidebar.radio("Navegacao", ["Visao Executiva", "Vendedores", "Produtos & Categorias"],
                          label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros Globais")

anos = sorted(fact["data_pedido"].apply(lambda x: str(x)[:4]).unique()) if len(fact) > 0 else []
ano_sel = st.sidebar.selectbox("Ano", ["Todos"] + anos if anos else ["Todos"])

regioes = sorted(fact["regiao"].unique()) if len(fact) > 0 else []
regiao_sel = st.sidebar.multiselect("Regiao", regioes, default=regioes) if regioes else []

estados = sorted(fact["estado"].unique()) if len(fact) > 0 else []
estado_sel = st.sidebar.multiselect("Estado", estados, default=[])

cats = sorted(dim_prod["categoria"].unique()) if len(dim_prod) > 0 else []
cat_sel = st.sidebar.multiselect("Categoria", cats, default=[])

st.sidebar.markdown("---")
st.sidebar.caption("Dados: bi_ecommerce (SQLite)")

# =====================================================================
# FILTER
# =====================================================================
fact_f = fact.copy()
if ano_sel != "Todos" and len(fact_f) > 0:
    fact_f = fact_f[fact_f["data_pedido"].apply(lambda x: str(x)[:4]) == ano_sel]
if regiao_sel and len(fact_f) > 0:
    fact_f = fact_f[fact_f["regiao"].isin(regiao_sel)]
if estado_sel and len(fact_f) > 0:
    fact_f = fact_f[fact_f["estado"].isin(estado_sel)]
if cat_sel and len(fact_f) > 0:
    prods = dim_prod[dim_prod["categoria"].isin(cat_sel)]["id_produto"].tolist()
    fact_f = fact_f[fact_f["id_produto"].isin(prods)]

# =====================================================================
# METRICS
# =====================================================================
def fmt(v):
    if abs(v) >= 1e6: return f"R$ {v/1e6:,.2f}M"
    if abs(v) >= 1e3: return f"R$ {v/1e3:,.1f}K"
    return f"R$ {v:,.2f}"

fat_f = fact_f["total_pedido"].sum() if len(fact_f) > 0 else 0
ped_f = fact_f["pedido_id"].nunique() if len(fact_f) > 0 else 0
ticket_f = fat_f / ped_f if ped_f > 0 else 0
vend_f = fact_f["id_vendedor"].nunique() if len(fact_f) > 0 else 0
cli_f = fact_f["id_cliente"].nunique() if len(fact_f) > 0 else 0
prods_vendidos = fact_f["id_produto"].nunique() if len(fact_f) > 0 else 0

# =====================================================================
# PAGE 1 - EXECUTIVA
# =====================================================================
if pagina == "Visao Executiva":
    st.markdown('<h2 style="color:#4A90D9;">Visao Executiva</h2>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", fmt(fat_f))
    c2.metric("Total Pedidos", f"{ped_f:,}")
    c3.metric("Ticket Medio", fmt(ticket_f))
    c4.metric("Vendedores", vend_f)

    st.markdown("---")

    cc_mapa, cc_rank = st.columns([1, 1])
    with cc_mapa:
        st.markdown("### Faturamento por Estado")
        dfe = fact_f.groupby("estado")["total_pedido"].sum().reset_index().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfe, x="total_pedido", y="estado", orientation="h",
                     color_discrete_sequence=["#4A90D9"],
                     labels={"total_pedido": "Faturamento", "estado": ""})
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=450, margin=dict(l=0,r=0,t=0,b=0))
        fig.update_xaxes(gridcolor="#3A3A3A")
        st.plotly_chart(fig, use_container_width=True)

    with cc_rank:
        st.markdown("### Ranking de Vendedores")
        dv = fact_f.merge(dim_vend, on="id_vendedor", how="left")
        dvr = dv.groupby(["id_vendedor", "nome"])["total_pedido"].sum().reset_index().sort_values("total_pedido")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dvr["nome"], x=dvr["total_pedido"], orientation="h",
                             marker=dict(color="#4A90D9"),
                             text=[fmt(v) for v in dvr["total_pedido"]],
                             textposition="outside", textfont=dict(color="#AAAAAA", size=10)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=450, margin=dict(l=0,r=100,t=0,b=0),
                          xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    c_muni, c_evo = st.columns([1, 1])
    with c_muni:
        st.markdown("### Top 10 Municipios")
        dm = fact_f.groupby("municipio")["total_pedido"].sum().reset_index().sort_values("total_pedido").tail(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dm["municipio"], x=dm["total_pedido"], orientation="h",
                             marker=dict(color="#4A90D9"),
                             text=[fmt(v) for v in dm["total_pedido"]],
                             textposition="outside", textfont=dict(color="#AAAAAA", size=9)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=380, margin=dict(l=0,r=80,t=0,b=0),
                          xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c_evo:
        st.markdown("### Evolucao Mensal")
        fe = fact_f.copy()
        fe["mes"] = fe["data_pedido"].apply(lambda x: str(x)[:7])
        dmes = fe.groupby("mes")["total_pedido"].sum().reset_index().sort_values("mes")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dmes["mes"], y=dmes["total_pedido"],
                                 mode="lines+markers+text", line=dict(color="#4A90D9", width=3),
                                 fill="tozeroy", fillcolor="rgba(74,144,217,0.12)",
                                 marker=dict(size=7, color="#4A90D9"),
                                 text=[fmt(v) for v in dmes["total_pedido"]],
                                 textposition="top center", textfont=dict(color="#AAAAAA", size=8)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=380, margin=dict(l=0,r=0,t=0,b=0),
                          xaxis=dict(gridcolor="#3A3A3A"), yaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# PAGE 2 - VENDEDORES
# =====================================================================
elif pagina == "Vendedores":
    st.markdown('<h2 style="color:#4A90D9;">Analise de Vendedores</h2>', unsafe_allow_html=True)
    dv = fact_f.merge(dim_vend, on="id_vendedor", how="left")
    dvf = dv.groupby(["id_vendedor", "nome", "regiao"])["total_pedido"].sum().reset_index().sort_values("total_pedido", ascending=False)

    melhor = dvf.iloc[0] if len(dvf) > 0 else None
    fat_med = fat_f / vend_f if vend_f > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Melhor Vendedor", melhor["nome"] if melhor is not None else "-", fmt(melhor["total_pedido"]) if melhor is not None else "")
    c2.metric("Fat. Medio/Vendedor", fmt(fat_med))
    c3.metric("Vendedores Ativos", vend_f)

    st.markdown("---")
    cd, cr = st.columns([1, 1])
    with cd:
        st.markdown("### Participacao por Vendedor")
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=dvf["nome"], values=dvf["total_pedido"], hole=0.55,
                             textinfo="percent", textfont=dict(size=10, color="#FFFFFF"),
                             marker=dict(colors=px.colors.sequential.Blues_r, line=dict(color="#1B1B1B", width=1))))
        fig.update_layout(paper_bgcolor="#1B1B1B", height=420, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        st.markdown("### Faturamento por Regiao")
        dr = dvf.groupby("regiao")["total_pedido"].sum().reset_index().sort_values("total_pedido")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dr["regiao"], x=dr["total_pedido"], orientation="h",
                             marker=dict(color="#4A90D9"),
                             text=[f"{fmt(v)}" for v in dr["total_pedido"]],
                             textposition="outside", textfont=dict(color="#AAAAAA", size=11)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=420, margin=dict(l=0,r=120,t=0,b=0),
                          xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Ranking Completo de Vendedores")
    dvf["Ranking"] = range(1, len(dvf)+1)
    dvf["Fat."] = dvf["total_pedido"].apply(fmt)
    dvf["%"] = (dvf["total_pedido"] / dvf["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
    st.dataframe(dvf[["Ranking", "nome", "regiao", "Fat.", "%"]].rename(
        columns={"nome": "Vendedor", "regiao": "Regiao"}),
        use_container_width=True, hide_index=True, height=530)

# =====================================================================
# PAGE 3 - PRODUTOS
# =====================================================================
elif pagina == "Produtos & Categorias":
    st.markdown('<h2 style="color:#4A90D9;">Produtos & Categorias</h2>', unsafe_allow_html=True)
    fc = fact_f.merge(dim_prod, on="id_produto", how="left")

    c1, c2, c3 = st.columns(3)
    c1.metric("Categorias", dim_prod["categoria"].nunique())
    c2.metric("Preco Medio", fmt(dim_prod["preco_venda"].mean()))
    c3.metric("Produtos Vendidos", prods_vendidos)

    st.markdown("---")
    cc, cp = st.columns([1, 1])
    with cc:
        st.markdown("### Faturamento por Categoria")
        dc = fc.groupby("categoria")["total_pedido"].sum().reset_index().sort_values("total_pedido")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dc["categoria"], x=dc["total_pedido"], orientation="h",
                             marker=dict(color="#4A90D9"),
                             text=[fmt(v) for v in dc["total_pedido"]],
                             textposition="outside", textfont=dict(color="#AAAAAA", size=11)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=420, margin=dict(l=0,r=100,t=0,b=0),
                          xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with cp:
        st.markdown("### Top 10 Produtos")
        dpt = fc.groupby(["nome_produto"])["total_pedido"].sum().reset_index().sort_values("total_pedido").tail(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dpt["nome_produto"], x=dpt["total_pedido"], orientation="h",
                             marker=dict(color="#4A90D9"),
                             text=[fmt(v) for v in dpt["total_pedido"]],
                             textposition="outside", textfont=dict(color="#AAAAAA", size=9)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B",
                          font_color="#AAAAAA", height=420, margin=dict(l=0,r=100,t=0,b=0),
                          xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Detalhamento por Categoria")
    dd = fc.groupby("categoria").agg(
        Faturamento=("total_pedido", "sum"),
        Pedidos=("pedido_id", "nunique"),
        Ticket=("total_pedido", "mean"),
        Qtd=("quantidade", "sum"),
    ).reset_index().sort_values("Faturamento", ascending=False)
    dd["Fat."] = dd["Faturamento"].apply(fmt)
    dd["Tkt"] = dd["Ticket"].apply(fmt)
    st.dataframe(dd[["categoria", "Fat.", "Pedidos", "Tkt", "Qtd"]].rename(
        columns={"categoria": "Categoria", "Pedidos": "Pedidos", "Qtd": "Qtd. Vendida"}),
        use_container_width=True, hide_index=True, height=300)
