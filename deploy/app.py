#!/usr/bin/env python3
"""
Nexus Dashboard — SaaS Enterprise Edition
4 pages, monochromatic violet brand, Inter font, dark slate layers
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Nexus", layout="wide")

# =====================================================================
# CSS — ENTERPRISE DARK THEME (Inter, layers, shadows, ghost buttons)
# =====================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ---- base layers ---- */
    .stApp, .main { background-color: #0F172A; padding-top: 0 !important; margin-top: 0 !important; }
    header[data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { background-color: #0B1320; border-right: 1px solid #1E293B; overflow: hidden; }
    [data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; color: #94A3B8; }
    [data-testid="stSidebarContent"] { padding-top: 12px; overflow-y: hidden !important; }
    .stApp * { font-family: 'Inter', sans-serif; }

    /* ---- reset streamlit artifacts ---- */
    *:focus { outline: none !important; box-shadow: none !important; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stDataFrameResizable"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="collapsedControl"] { top: 12px !important; left: 8px !important; }
    #MainMenu, footer { display: none; }
    .stAlert { background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; color: #94A3B8 !important; }
    .stAlert [data-testid="stNotification"] { color: #F1F5F9 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 0.5rem; }

    /* ---- typography ---- */
    h1, h2, h3, h4, h5, h6 { color: #F1F5F9; font-weight: 600; letter-spacing: -0.02em; }
    p, span, label, caption { color: #94A3B8; }

    /* ---- select / multiselect ---- */
    div[data-baseweb="select"] > div {
        background-color: #1E293B; border: 1px solid #334155; color: #F1F5F9;
        border-radius: 8px; font-size: 0.82rem;
    }
    div[data-baseweb="select"] > div:hover { border-color: #475569; }
    .stSelectbox label, .stMultiselect label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.6px; color: #64748B; font-weight: 500; }

    /* ---- buttons (ghost style) ---- */
    .stButton button {
        background-color: transparent; color: #A78BFA;
        border: 1px solid #5B21B6; border-radius: 8px;
        padding: 6px 20px; font-size: 0.78rem; font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton button:hover { background-color: rgba(124,58,237,0.12); border-color: #7C3AED; color: #C4B5FD; }
    .stButton button:active { background-color: rgba(124,58,237,0.18); }

    /* ---- radio pills ---- */
    div[data-testid="stRadio"] label { padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 500; cursor: pointer; }
    div[data-testid="stRadio"] label[data-selected="true"] { background-color: rgba(124,58,237,0.15); color: #A78BFA; }

    /* ---- dataframes (zebra + mono numbers) ---- */
    [data-testid="stDataFrame"] { border: 1px solid #1E293B; border-radius: 8px; overflow: hidden; }
    .dataframe { font-size: 0.78rem; }
    .dataframe thead th { background-color: #1E293B; color: #64748B; font-weight: 600; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.5px; padding: 10px 14px; border-bottom: 1px solid #334155; }
    .dataframe tbody td { padding: 8px 14px; color: #CBD5E1; border-bottom: 1px solid rgba(30,41,59,0.5); }
    .dataframe tbody tr:nth-child(even) td { background-color: rgba(124,58,237,0.02); }
    .dataframe tbody tr:hover td { background-color: rgba(124,58,237,0.06); }

    /* ---- divider ---- */
    hr { border-color: #1E293B; margin: 0.4rem 0; }

    /* ---- scrollbar ---- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0F172A; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    /* ---- responsive ---- */
    @media (max-width: 1024px) {
        [data-testid="column"] { min-width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# COLOR SYSTEM — VIOLET MONOCHROMATIC BRAND
# =====================================================================
C = {
    "brand":       "#7C3AED",
    "brand_light": "#A78BFA",
    "brand_muted": "#5B21B6",
    "brand_bg":    "rgba(124,58,237,0.12)",
    "brand_ghost": "rgba(124,58,237,0.06)",
    "bg":          "#0F172A",
    "surface":     "#1E293B",
    "border":      "#334155",
    "text":        "#F1F5F9",
    "text_sec":    "#94A3B8",
    "text_muted":  "#64748B",
    "positive":    "#34D399",
    "negative":    "#F87171",
}
CHART_COLORS = ["#7C3AED", "#8B5CF6", "#A78BFA", "#C4B5FD", "#DDD6FE"]

# =====================================================================
# DATABASE (CSV)
# =====================================================================
@st.cache_data(ttl=600)
def load_csv(table):
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    path = os.path.join(data_dir, f"{table}.csv")
    return pd.read_csv(path)

@st.cache_data(ttl=600)
def load_all():
    return (
        load_csv("fact_vendas"),
        load_csv("dim_vendedores"),
        load_csv("dim_produtos"),
        load_csv("dim_calendario"),
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

def tooltip_pt():
    return dict(
        bgcolor=C["surface"],
        bordercolor=C["border"],
        font=dict(family="Inter", size=12, color=C["text"]),
    )

def chart_config(fig, height=360, showlegend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        font_color=C["text_sec"],
        font_size=11,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont_size=10),
        yaxis=dict(showgrid=False, zeroline=False, tickfont_size=10),
        showlegend=showlegend,
        hoverlabel=dict(bgcolor=C["surface"], bordercolor=C["border"], font_family="Inter", font_color=C["text"]),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x:,.2f}</b><br>"
            "%{y}<extra></extra>"
        ),
        marker=dict(line=dict(width=0)),
    )
    return fig

def kpi_card(icon_html, label, value, delta=None, delta_color=None):
    delta_html = ""
    if delta:
        col = C["positive"] if delta_color == "up" else C["negative"] if delta_color == "down" else C["text_sec"]
        delta_html = f'<div style="font-size:0.72rem;font-weight:500;color:{col};margin-top:6px;">{delta}</div>'
    st.markdown(f"""
    <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:12px;padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.25);">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            {icon_html}
            <span style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:{C['text_muted']};font-weight:500;">{label}</span>
        </div>
        <div style="font-size:1.55rem;font-weight:700;color:{C['text']};letter-spacing:-0.03em;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

SVG = {
    "fat":   '<svg width="12" height="12"><circle cx="6" cy="6" r="5" fill="#7C3AED"/></svg>',
    "ped":   '<svg width="12" height="12"><rect x="1" y="1" width="10" height="10" rx="2" fill="#A78BFA"/></svg>',
    "tkt":   '<svg width="12" height="12"><polygon points="6,1 11,11 1,11" fill="#8B5CF6"/></svg>',
    "vend":  '<svg width="12" height="12"><polygon points="6,1 11,5 11,11 1,11 1,5" fill="#C4B5FD"/></svg>',
    "cat":   '<svg width="12" height="12"><circle cx="6" cy="6" r="5" fill="#8B5CF6"/></svg>',
    "preco": '<svg width="12" height="12"><rect x="1" y="1" width="10" height="10" rx="2" fill="#A78BFA"/></svg>',
    "star":  '<svg width="12" height="12"><polygon points="6,1 7.8,4.5 11.7,5.1 8.8,8 9.5,12 6,10.2 2.5,12 3.2,8 0.3,5.1 4.2,4.5" fill="#A78BFA"/></svg>',
}

def section_title(text):
    st.markdown(f'<div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.8px;color:{C["text_muted"]};font-weight:600;margin:0 0 6px 0;">{text}</div>', unsafe_allow_html=True)

# =====================================================================
# LOAD DATA
# =====================================================================
fact, dim_vend, dim_prod, dim_cal = load_all()

if len(fact) == 0:
    st.markdown(f"""
    <div style="text-align:center;padding:60px 20px;">
        <div style="font-size:3rem;margin-bottom:16px;color:{C['text_muted']};">&#9888;</div>
        <h3 style="color:{C['text']};">Base de dados indisponivel</h3>
        <p style="color:{C['text_sec']};">Execute o pipeline primeiro para gerar os dados.</p>
        <code style="background:{C['surface']};padding:6px 14px;border-radius:6px;color:{C['brand_light']};">python src/run_pipeline.py</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown(f'<div style="font-size:1.4rem;font-weight:700;color:{C["brand"]};letter-spacing:-0.03em;margin-top:-8px;">NEXUS</div>', unsafe_allow_html=True)
    st.caption("Dashboard de Vendas")
    st.markdown("---")

    pagina = st.radio("", ["Visao Executiva", "Vendedores", "Produtos", "Geografica"],
                       label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:{C["text_muted"]};font-weight:600;margin-bottom:8px;">Filtros</div>', unsafe_allow_html=True)

    anos_uniq = sorted(fact["data_pedido"].apply(lambda x: str(x)[:4]).unique())
    ano_sel = st.selectbox("Ano", ["Todos"] + anos_uniq)

    regioes_uniq = sorted(fact["regiao"].unique())
    regiao_sel = st.multiselect("Regiao", regioes_uniq, default=[], placeholder="Todas")

    estados_uniq = sorted(fact["estado"].unique())
    estado_sel = st.multiselect("Estado", estados_uniq, default=[], placeholder="Todos")

    cats_uniq = sorted(dim_prod["categoria"].unique())
    cat_sel = st.multiselect("Categoria", cats_uniq, default=[], placeholder="Todas")

    st.markdown(f'<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:{C["text_muted"]};font-weight:600;margin-bottom:8px;">Periodo</div>', unsafe_allow_html=True)

    all_dates_raw = pd.to_datetime(fact["data_pedido"])
    data_min_global = all_dates_raw.min().date()
    data_max_global = all_dates_raw.max().date()

    data_ini = st.date_input("Data inicial", value=data_min_global, min_value=data_min_global, max_value=data_max_global)
    data_fim = st.date_input("Data final", value=data_max_global, min_value=data_min_global, max_value=data_max_global)

    st.markdown(f'<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
    if st.button("Limpar filtros", use_container_width=True):
        st.rerun()

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
    df["_data_dt"] = pd.to_datetime(df["data_pedido"])
    df = df[(df["_data_dt"] >= pd.Timestamp(data_ini)) & (df["_data_dt"] <= pd.Timestamp(data_fim))]
    df = df.drop(columns=["_data_dt"])
    return df

ff = filtrar(fact)

if len(ff) == 0:
    st.markdown(f"""
    <div style="text-align:center;padding:40px 20px;">
        <div style="font-size:2.5rem;margin-bottom:12px;color:{C['text_muted']};">&#128269;</div>
        <p style="color:{C['text_sec']};font-size:0.95rem;">Nenhum dado para os filtros selecionados.</p>
        <p style="color:{C['text_muted']};font-size:0.78rem;">Tente ampliar os criterios de busca.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# shared KPIs
fat_total = ff["total_pedido"].sum()
ped_total = ff["pedido_id"].nunique()
tkt_medio = fat_total / ped_total if ped_total > 0 else 0
vend_total = ff["id_vendedor"].nunique()

# =====================================================================
# PAGE 1 — VISÃO EXECUTIVA
# =====================================================================
if pagina == "Visao Executiva":

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card(SVG["fat"],  "Faturamento",   fmt(fat_total))
    with c2: kpi_card(SVG["ped"],  "Total Pedidos", fmt_int(ped_total))
    with c3: kpi_card(SVG["tkt"],  "Ticket Medio",  fmt(tkt_medio))
    with c4: kpi_card(SVG["vend"], "Vendedores",    vend_total)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    cr, cl = st.columns([1, 1])
    with cr:
        section_title("Faturamento por Estado")
        dfe = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfe, x="total_pedido", y="estado", orientation="h",
                     color_discrete_sequence=[C["brand"]], labels={"total_pedido": "", "estado": ""})
        chart_config(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cl:
        section_title("Faturamento por Regiao")
        dfr = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfr, x="total_pedido", y="regiao", orientation="h",
                     color_discrete_sequence=[C["brand_muted"]], labels={"total_pedido": "", "regiao": ""})
        chart_config(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        section_title("Top 10 Municipios")
        dm = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(10)
        fig = go.Figure(go.Bar(y=dm["municipio"], x=dm["total_pedido"], orientation="h", marker=dict(color=C["brand"])))
        chart_config(fig, height=350)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        section_title("Ranking Vendedores")
        dv_r = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_v", "_d"))
        rank = dv_r.groupby(["nome", "regiao_d"], as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        rank.insert(0, "#", range(1, len(rank)+1))
        rank["Faturamento"] = rank["total_pedido"].apply(fmt)
        rank["%"] = (rank["total_pedido"] / rank["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
        display = rank[["#", "nome", "regiao_d", "Faturamento", "%"]].rename(columns={"nome": "Vendedor", "regiao_d": "Regiao"})
        st.dataframe(display, use_container_width=True, hide_index=True, height=350)

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    section_title("Evolucao Mensal do Faturamento")
    fe = ff.copy()
    fe["data_pedido_dt"] = pd.to_datetime(ff["data_pedido"])
    fe["ano_mes"] = fe["data_pedido_dt"].dt.to_period("M").astype(str)
    dmes = fe.groupby("ano_mes", as_index=False).agg(
        total=("total_pedido", "sum"), pedidos=("pedido_id", "nunique"), min_dt=("data_pedido_dt", "min")
    ).sort_values("ano_mes")
    dmes["label"] = dmes["min_dt"].dt.strftime("%b/%y")
    dmes["cresc"] = dmes["total"].pct_change()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dmes["label"], y=dmes["total"], mode="lines+markers",
                             line=dict(color=C["brand"], width=2.2),
                             fill="tozeroy", fillcolor=C["brand_ghost"],
                             marker=dict(size=4, color=C["brand"])))
    chart_config(fig, height=300)
    fig.update_xaxes(tickangle=-30, tickfont_size=9)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if len(dmes) >= 2:
        last_cresc = dmes["cresc"].iloc[-1]
        if pd.notna(last_cresc):
            direction = "up" if last_cresc >= 0 else "down"
            arr = "+" if last_cresc >= 0 else ""
            kpi_card(SVG["fat"], "Crescimento vs mes anterior", f"{arr}{last_cresc*100:.1f}%")

# =====================================================================
# PAGE 2 — VENDEDORES
# =====================================================================
elif pagina == "Vendedores":

    dv = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_v", "_d"))
    dvf = dv.groupby(["id_vendedor", "nome", "regiao_d"], as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    dvf["rank"] = range(1, len(dvf)+1)
    top1 = dvf.iloc[0] if len(dvf) > 0 else None
    fat_med = fat_total / vend_total if vend_total > 0 else 0

    c1, c2 = st.columns(2)
    with c1:
        nome_top = top1["nome"] if top1 is not None else "-"
        val_top = fmt(top1["total_pedido"]) if top1 is not None else ""
        kpi_card(SVG["star"], "Melhor Vendedor", f"{nome_top} — {val_top}")
    with c2:
        kpi_card(SVG["tkt"], "Fat. Medio por Vendedor", fmt(fat_med))

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    section_title("Ranking Completo")
    rank_display = dvf.copy()
    rank_display["Faturamento"] = rank_display["total_pedido"].apply(fmt)
    rank_display["%"] = (rank_display["total_pedido"] / rank_display["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
    tbl = rank_display[["rank", "nome", "regiao_d", "Faturamento", "%"]].rename(
        columns={"rank": "#", "nome": "Vendedor", "regiao_d": "Regiao"})
    st.dataframe(tbl, use_container_width=True, hide_index=True, height=520)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    cd, cr2 = st.columns([1, 1])
    with cd:
        section_title("Participacao %")
        fig = go.Figure(go.Pie(labels=dvf["nome"], values=dvf["total_pedido"], hole=0.6,
                               textinfo="percent", textfont=dict(size=10, color=C["text"], family="Inter"),
                               marker=dict(colors=CHART_COLORS * 3, line=dict(width=0))))
        chart_config(fig, height=340)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cr2:
        section_title("Fat. por Regiao do Vendedor")
        dv_stacked = dvf.groupby(["regiao_d", "nome"], as_index=False)["total_pedido"].sum()
        fig = px.bar(dv_stacked, x="total_pedido", y="regiao_d", color="nome",
                     orientation="h", color_discrete_sequence=CHART_COLORS * 3,
                     labels={"total_pedido": "", "regiao_d": ""})
        chart_config(fig, height=340, showlegend=True)
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.15, font_size=8, title_text="", itemclick=False, itemdoubleclick=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# PAGE 3 — PRODUTOS
# =====================================================================
elif pagina == "Produtos":

    fc = ff.merge(dim_prod, on="id_produto", how="left")

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card(SVG["cat"],   "Categorias",       dim_prod["categoria"].nunique())
    with c2: kpi_card(SVG["preco"], "Preco Medio",      fmt(dim_prod["preco_venda"].mean()))
    with c3: kpi_card(SVG["ped"],   "Produtos Vendidos", ff["id_produto"].nunique())

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    cc, cp = st.columns([1, 1])
    with cc:
        section_title("Faturamento por Categoria")
        dc = fc.groupby("categoria", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True)
        fig = go.Figure(go.Bar(y=dc["categoria"], x=dc["total_pedido"], orientation="h", marker=dict(color=C["brand"])))
        chart_config(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cp:
        section_title("Top 10 Produtos")
        dpt = fc.groupby("nome_produto", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(10)
        fig = go.Figure(go.Bar(y=dpt["nome_produto"], x=dpt["total_pedido"], orientation="h", marker=dict(color=C["brand_light"])))
        chart_config(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    section_title("Detalhamento por Categoria")
    dd = fc.groupby("categoria").agg(
        Faturamento=("total_pedido", "sum"), Pedidos=("pedido_id", "nunique"),
        Ticket=("total_pedido", "mean"), Quantidade=("quantidade", "sum"),
    ).reset_index()
    dd["Fat. Formatado"] = dd["Faturamento"].apply(fmt)
    dd["Ticket Formatado"] = dd["Ticket"].apply(fmt)
    st.dataframe(dd[["categoria", "Fat. Formatado", "Pedidos", "Ticket Formatado", "Quantidade"]].rename(
        columns={"categoria": "Categoria", "Fat. Formatado": "Faturamento", "Ticket Formatado": "Ticket Medio", "Quantidade": "Qtd. Vendida"}),
        use_container_width=True, hide_index=True, height=280)

# =====================================================================
# PAGE 4 — GEOGRÁFICA
# =====================================================================
elif pagina == "Geografica":

    section_title("Faturamento por Estado")
    dfe2 = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    fig = go.Figure(go.Bar(y=dfe2["estado"], x=dfe2["total_pedido"], orientation="h", marker=dict(color=C["brand"])))
    chart_config(fig, height=360)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    section_title("Faturamento por Regiao")
    dfr2 = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    fig = go.Figure(go.Bar(y=dfr2["regiao"], x=dfr2["total_pedido"], orientation="h", marker=dict(color=C["brand_muted"])))
    chart_config(fig, height=320)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    section_title("Top 15 Municipios")
    dm2 = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(15)
    fig = go.Figure(go.Bar(y=dm2["municipio"], x=dm2["total_pedido"], orientation="h", marker=dict(color=C["brand_light"])))
    chart_config(fig, height=420)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# FOOTER
# =====================================================================
st.markdown("---")
st.caption(f"Nexus — Dados simulados (2025–2026) | "
           f"250 produtos · 1.500 clientes · 8.000 pedidos · Faturamento: {fmt(fat_total)} | "
           f"[GitHub](https://github.com/Nagalli01/bi-ecommerce-dashboard)")
