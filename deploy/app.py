#!/usr/bin/env python3
"""
BI E-Commerce Dashboard — Streamlit (Self-contained)
Deploy: Hugging Face Spaces, Render, Streamlit Cloud
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

st.set_page_config(page_title="BI E-Commerce", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #1B1B1B; }
    [data-testid="stSidebar"] { background-color: #141414; border-right: 1px solid #2D2D2D; }
    [data-testid="stSidebar"] * { color: #AAAAAA; }
    [data-testid="stMetric"] { background-color: #2D2D2D; border: 1px solid #3A3A3A; border-radius: 10px; padding: 16px; }
    [data-testid="stMetric"] label { color: #888888 !important; font-size: 0.8rem; }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 700; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Segoe UI', sans-serif; }
    p, span, div { color: #AAAAAA; }
    .stSelectbox label, .stMultiselect label { color: #AAAAAA !important; }
    div[data-baseweb="select"] > div { background-color: #2D2D2D; border-color: #3A3A3A; color: #FFFFFF; }
    header[data-testid="stHeader"] { background-color: #1B1B1B; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# DATABASE
# =====================================================================
@st.cache_resource
def get_conn():
    path = os.path.join(os.path.dirname(__file__), "bi_ecommerce.db")
    if os.path.exists(path):
        return sqlite3.connect(path, check_same_thread=False)
    path2 = os.path.join(os.path.dirname(__file__), "data", "bi_ecommerce.db")
    if os.path.exists(path2):
        return sqlite3.connect(path2, check_same_thread=False)
    return None

@st.cache_data(ttl=30)
def q(sql):
    conn = get_conn()
    return pd.read_sql(sql, conn) if conn else pd.DataFrame()

# =====================================================================
# DATA
# =====================================================================
fact = q("SELECT * FROM fact_vendas")
dim_vend = q("SELECT * FROM dim_vendedores")
dim_prod = q("SELECT * FROM dim_produtos")

# =====================================================================
# SIDEBAR
# =====================================================================
st.sidebar.markdown("## 🛒 BI E-Commerce")
st.sidebar.markdown("---")
pagina = st.sidebar.radio("Navegacao", ["Visao Executiva", "Vendedores", "Produtos"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros")
anos = sorted(fact["data_pedido"].apply(lambda x: str(x)[:4]).unique()) if len(fact) > 0 else []
ano_sel = st.sidebar.selectbox("Ano", ["Todos"] + anos)
regioes = sorted(fact["regiao"].unique()) if len(fact) > 0 else []
regiao_sel = st.sidebar.multiselect("Regiao", regioes, default=regioes)
estados = sorted(fact["estado"].unique()) if len(fact) > 0 else []
estado_sel = st.sidebar.multiselect("Estado", estados, default=[])
cats = sorted(dim_prod["categoria"].unique()) if len(dim_prod) > 0 else []
cat_sel = st.sidebar.multiselect("Categoria", cats, default=[])
st.sidebar.caption("Dados: bi_ecommerce (SQLite)")

# =====================================================================
# FILTER
# =====================================================================
def filtrar(df):
    if ano_sel != "Todos": df = df[df["data_pedido"].apply(lambda x: str(x)[:4]) == ano_sel]
    if regiao_sel: df = df[df["regiao"].isin(regiao_sel)]
    if estado_sel: df = df[df["estado"].isin(estado_sel)]
    if cat_sel:
        prods = dim_prod[dim_prod["categoria"].isin(cat_sel)]["id_produto"].tolist()
        df = df[df["id_produto"].isin(prods)]
    return df

ff = filtrar(fact)
fat = ff["total_pedido"].sum() if len(ff) > 0 else 0
ped = ff["pedido_id"].nunique() if len(ff) > 0 else 0
tkt = fat / ped if ped > 0 else 0
vend = ff["id_vendedor"].nunique() if len(ff) > 0 else 0
cli = ff["id_cliente"].nunique() if len(ff) > 0 else 0

def fmt(v):
    if abs(v) >= 1e6: return f"R$ {v/1e6:,.2f}M"
    if abs(v) >= 1e3: return f"R$ {v/1e3:,.0f}K"
    return f"R$ {v:.2f}"

# =====================================================================
# PAGE 1
# =====================================================================
if pagina == "Visao Executiva":
    st.markdown('<h2 style="color:#4A90D9;">Visao Executiva</h2>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", fmt(fat))
    c2.metric("Pedidos", f"{ped:,}")
    c3.metric("Ticket Medio", fmt(tkt))
    c4.metric("Vendedores", vend)

    st.markdown("---")
    cr, cl = st.columns([1, 1])
    with cr:
        st.markdown("### Faturamento por Estado")
        dfe = ff.groupby("estado")["total_pedido"].sum().reset_index().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfe, x="total_pedido", y="estado", orientation="h", color_discrete_sequence=["#4A90D9"],
                     labels={"total_pedido": "", "estado": ""})
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"))
        st.plotly_chart(fig, use_container_width=True)

    with cl:
        st.markdown("### Ranking Vendedores")
        dv = ff.merge(dim_vend, on="id_vendedor", how="left")
        dvr = dv.groupby("nome")["total_pedido"].sum().reset_index().sort_values("total_pedido")
        fig = go.Figure(go.Bar(y=dvr["nome"], x=dvr["total_pedido"], orientation="h",
                               marker=dict(color="#4A90D9"),
                               text=[fmt(v) for v in dvr["total_pedido"]],
                               textposition="outside", textfont=dict(color="#AAAAAA", size=10)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=400, margin=dict(l=0,r=100,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### Top 10 Municipios")
        dm = ff.groupby("municipio")["total_pedido"].sum().reset_index().sort_values("total_pedido").tail(10)
        fig = go.Figure(go.Bar(y=dm["municipio"], x=dm["total_pedido"], orientation="h",
                               marker=dict(color="#4A90D9"),
                               text=[fmt(v) for v in dm["total_pedido"]],
                               textposition="outside", textfont=dict(color="#AAAAAA", size=9)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=350, margin=dict(l=0,r=80,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### Evolucao Mensal")
        fe = ff.copy()
        fe["mes"] = fe["data_pedido"].apply(lambda x: str(x)[:7])
        dmes = fe.groupby("mes")["total_pedido"].sum().reset_index().sort_values("mes")
        fig = go.Figure(go.Scatter(x=dmes["mes"], y=dmes["total_pedido"], mode="lines+markers+text",
                                   line=dict(color="#4A90D9", width=3),
                                   fill="tozeroy", fillcolor="rgba(74,144,217,0.12)",
                                   marker=dict(size=7, color="#4A90D9"),
                                   text=[fmt(v) for v in dmes["total_pedido"]],
                                   textposition="top center", textfont=dict(color="#AAAAAA", size=8)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"),
                          yaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# PAGE 2
# =====================================================================
elif pagina == "Vendedores":
    st.markdown('<h2 style="color:#4A90D9;">Analise de Vendedores</h2>', unsafe_allow_html=True)
    dv = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_venda", "_vendedor"))
    dvf = dv.groupby(["id_vendedor", "nome", "regiao_vendedor"])["total_pedido"].sum().reset_index().sort_values("total_pedido", ascending=False).rename(columns={"regiao_vendedor": "regiao"})
    melhor = dvf.iloc[0] if len(dvf) > 0 else None
    fat_med = fat / vend if vend > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Melhor Vendedor", melhor["nome"] if melhor is not None else "-", fmt(melhor["total_pedido"]) if melhor is not None else "")
    c2.metric("Fat. Medio/Vendedor", fmt(fat_med))
    c3.metric("Vendedores Ativos", vend)

    cd, cr = st.columns([1, 1])
    with cd:
        st.markdown("### Participacao %")
        fig = go.Figure(go.Pie(labels=dvf["nome"], values=dvf["total_pedido"], hole=0.55,
                               textinfo="percent", textfont=dict(size=10, color="#FFFFFF"),
                               marker=dict(colors=px.colors.sequential.Blues_r)))
        fig.update_layout(paper_bgcolor="#1B1B1B", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        st.markdown("### Faturamento por Regiao")
        dr = dvf.groupby("regiao")["total_pedido"].sum().reset_index().sort_values("total_pedido")
        fig = go.Figure(go.Bar(y=dr["regiao"], x=dr["total_pedido"], orientation="h",
                               marker=dict(color="#4A90D9"),
                               text=[f"{fmt(v)}" for v in dr["total_pedido"]],
                               textposition="outside", textfont=dict(color="#AAAAAA", size=11)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=400, margin=dict(l=0,r=120,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Ranking Completo")
    dvf["#"] = range(1, len(dvf)+1)
    dvf["$"] = dvf["total_pedido"].apply(fmt)
    dvf["%"] = (dvf["total_pedido"] / dvf["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
    st.dataframe(dvf[["#", "nome", "regiao", "$", "%"]].rename(columns={"nome": "Vendedor", "regiao": "Regiao"}),
                 use_container_width=True, hide_index=True, height=530)

# =====================================================================
# PAGE 3
# =====================================================================
elif pagina == "Produtos":
    st.markdown('<h2 style="color:#4A90D9;">Produtos & Categorias</h2>', unsafe_allow_html=True)
    fc = ff.merge(dim_prod, on="id_produto", how="left")

    c1, c2, c3 = st.columns(3)
    c1.metric("Categorias", dim_prod["categoria"].nunique())
    c2.metric("Preco Medio", fmt(dim_prod["preco_venda"].mean()))
    c3.metric("Produtos Vendidos", ff["id_produto"].nunique())

    cc, cp = st.columns([1, 1])
    with cc:
        st.markdown("### Faturamento por Categoria")
        dc = fc.groupby("categoria")["total_pedido"].sum().reset_index().sort_values("total_pedido")
        fig = go.Figure(go.Bar(y=dc["categoria"], x=dc["total_pedido"], orientation="h",
                               marker=dict(color="#4A90D9"),
                               text=[fmt(v) for v in dc["total_pedido"]],
                               textposition="outside", textfont=dict(color="#AAAAAA", size=11)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=400, margin=dict(l=0,r=100,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with cp:
        st.markdown("### Top 10 Produtos")
        dpt = fc.groupby("nome_produto")["total_pedido"].sum().reset_index().sort_values("total_pedido").tail(10)
        fig = go.Figure(go.Bar(y=dpt["nome_produto"], x=dpt["total_pedido"], orientation="h",
                               marker=dict(color="#4A90D9"),
                               text=[fmt(v) for v in dpt["total_pedido"]],
                               textposition="outside", textfont=dict(color="#AAAAAA", size=9)))
        fig.update_layout(paper_bgcolor="#1B1B1B", plot_bgcolor="#1B1B1B", font_color="#AAAAAA",
                          height=400, margin=dict(l=0,r=100,t=0,b=0), xaxis=dict(gridcolor="#3A3A3A"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Detalhamento por Categoria")
    dd = fc.groupby("categoria").agg(Faturamento=("total_pedido", "sum"), Pedidos=("pedido_id", "nunique"),
                                     Ticket=("total_pedido", "mean"), Qtd=("quantidade", "sum")).reset_index()
    dd["Fat."] = dd["Faturamento"].apply(fmt)
    dd["Tkt"] = dd["Ticket"].apply(fmt)
    st.dataframe(dd[["categoria", "Fat.", "Pedidos", "Tkt", "Qtd"]].rename(
        columns={"categoria": "Categoria"}), use_container_width=True, hide_index=True, height=300)
