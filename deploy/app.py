#!/usr/bin/env python3
"""
Nexus Dashboard v3.0 — Executive Decision Intelligence
Monochrome violet + cyan accent, depth layers, auto-insights, compact density
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Nexus", layout="wide")

# =====================================================================
# CSS — ENTERPRISE v3 (depth layers, tighter spacing, compact charts)
# =====================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

    .stApp * { font-family: 'Inter', sans-serif; }
    .stApp, .main { background-color: #0B1120; padding-top: 0 !important; margin-top: 0 !important; }
    header[data-testid="stHeader"] { display: none; }

    /* ---- sidebar ---- */
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1E293B; overflow: hidden; }
    section[data-testid="stSidebar"] { padding-top: 0 !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 0.8rem !important; }
    [data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; color: #94A3B8; }
    [data-testid="stSidebarContent"] { padding-top: 10px; overflow-y: hidden !important; }

    /* ---- collapse button ---- */
    [data-testid="collapsedControl"] { top: 14px !important; left: 10px !important; font-size: 0 !important; color: transparent !important; }
    [data-testid="collapsedControl"]::before { content: "\25C0"; font-size: 14px !important; color: #A78BFA !important; }
    [data-testid="stSidebarCollapsedControl"] { font-size: 0 !important; color: transparent !important; }
    [data-testid="stSidebarCollapsedControl"]::before { content: "\25B6"; font-size: 14px !important; color: #A78BFA !important; }

    /* ---- nav radio (remove red, use violet) ---- */
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] div:first-child { border-color: #7C3AED !important; background-color: #7C3AED !important; }
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] div:first-child { background-color: #7C3AED !important; border-color: #7C3AED !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important; }
    [data-testid="stSidebar"] .stRadio label:hover { background: rgba(124,58,237,0.08) !important; border-radius: 8px !important; cursor: pointer; }

    [data-testid="stToolbar"] { display: none; }
    #MainMenu, footer { display: none; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stDataFrameResizable"] { display: none; }
    *:focus { outline: none !important; box-shadow: none !important; }
    .block-container { padding: 0.8rem 2rem 0.4rem 2rem; }

    h1, h2, h3, h4 { color: #F1F5F9; font-weight: 600; letter-spacing: -0.02em; }
    p, span, label, caption { color: #94A3B8; }
    hr { border-color: #1E293B; margin: 0.3rem 0; }

    div[data-baseweb="select"] > div {
        background-color: #1E293B; border: 1px solid #334155; color: #F1F5F9;
        border-radius: 8px; font-size: 0.82rem;
    }
    div[data-baseweb="select"] > div:hover { border-color: #475569; }
    .stSelectbox label, .stMultiselect label {
        font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.6px; color: #64748B; font-weight: 600;
    }

    .stButton button {
        background-color: transparent; color: #A78BFA;
        border: 1px solid #5B21B6; border-radius: 8px;
        padding: 5px 18px; font-size: 0.76rem; font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton button:hover { background-color: rgba(124,58,237,0.12); border-color: #7C3AED; color: #C4B5FD; }

    div[data-testid="stRadio"] label {
        padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 500; cursor: pointer;
    }
    div[data-testid="stRadio"] label[data-selected="true"] {
        background-color: rgba(124,58,237,0.15); color: #A78BFA;
    }

    [data-testid="stDataFrame"] { border: 1px solid #1E293B; border-radius: 8px; overflow: hidden; }
    .dataframe { font-size: 0.76rem; }
    .dataframe thead th { background-color: #1E293B; color: #64748B; font-weight: 600; font-size: 0.65rem; text-transform: uppercase; padding: 8px 12px; border-bottom: 1px solid #334155; }
    .dataframe tbody td { padding: 6px 12px; color: #CBD5E1; border-bottom: 1px solid rgba(30,41,59,0.4); }
    .dataframe tbody tr:nth-child(even) td { background-color: rgba(124,58,237,0.015); }
    .dataframe tbody tr:hover td { background-color: rgba(124,58,237,0.05); }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0B1120; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# COLOR SYSTEM — BRAND + SECONDARY + STATUS
# =====================================================================
C = {
    "brand":       "#7C3AED",  # primary violet
    "brand_l":     "#A78BFA",
    "second":      "#06B6D4",  # cyan accent
    "second_l":    "#22D3EE",
    "success":     "#22C55E",
    "warn":        "#F59E0B",
    "danger":      "#EF4444",
    "bg":          "#0B1120",
    "sidebar":     "#111827",
    "surface":     "#1E293B",
    "border":      "#334155",
    "text":        "#F1F5F9",
    "text_sec":    "#94A3B8",
    "text_muted":  "#64748B",
}

# =====================================================================
# DATABASE
# =====================================================================
@st.cache_data(ttl=600)
def load_csv(table):
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    return pd.read_csv(os.path.join(data_dir, f"{table}.csv"))

@st.cache_data(ttl=600)
def load_all():
    return load_csv("fact_vendas"), load_csv("dim_vendedores"), load_csv("dim_produtos"), load_csv("dim_calendario")

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

def delta_badge(current, previous):
    if previous is None or previous == 0: return None
    pct = (current - previous) / previous * 100
    arrow = "+" if pct >= 0 else ""
    col = C["success"] if pct >= 0 else C["danger"]
    return f'<span style="color:{col};font-weight:600;">{arrow}{pct:.1f}%</span>'

def chart_config(fig, height=300, showlegend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter", font_color=C["text_sec"], font_size=10,
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont_size=9),
        yaxis=dict(showgrid=False, zeroline=False, tickfont_size=9),
        showlegend=showlegend,
        hoverlabel=dict(bgcolor=C["surface"], bordercolor=C["border"], font_family="Inter", font_color=C["text"]),
    )
    fig.update_traces(hovertemplate="<b>%{x:,.2f}</b><br>%{y}<extra></extra>", marker=dict(line=dict(width=0)))
    return fig

def kpi_card(label, value, delta_str=None):
    delta_html = ""
    if delta_str:
        delta_html = f'<div style="margin-top:6px;font-size:0.72rem;">{delta_str}</div>'
    st.markdown(f"""
    <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:12px;padding:16px 18px;box-shadow:0 8px 24px rgba(0,0,0,0.18);">
        <div style="font-size:0.66rem;text-transform:uppercase;letter-spacing:0.7px;color:{C['text_muted']};font-weight:600;margin-bottom:8px;">{label}</div>
        <div style="font-size:1.55rem;font-weight:700;color:{C['text']};letter-spacing:-0.03em;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def smart_kpi(icon, label, value, sub=""):
    st.markdown(f"""
    <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;padding:10px 14px;box-shadow:0 4px 12px rgba(0,0,0,0.12);text-align:center;">
        <div style="font-size:0.62rem;text-transform:uppercase;color:{C['text_muted']};font-weight:600;letter-spacing:0.5px;margin-bottom:4px;">{label}</div>
        <div style="font-size:1.1rem;font-weight:700;color:{C['text']};">{value}</div>
        <div style="font-size:0.6rem;color:{C['text_muted']};margin-top:2px;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def section_title(text):
    st.markdown(f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;color:{C["text_muted"]};font-weight:600;margin:6px 0 4px 0;">{text}</div>', unsafe_allow_html=True)

def insight_card(icon, text, color=None):
    col = color or C["second"]
    st.markdown(f"""
    <div style="background:{C['surface']};border-left:3px solid {col};border-radius:0 10px 10px 0;padding:10px 14px;margin:4px 0;box-shadow:0 2px 6px rgba(0,0,0,0.1);">
        <span style="color:{col};font-size:0.85rem;">{icon}</span>
        <span style="color:{C['text_sec']};font-size:0.76rem;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# LOAD DATA
# =====================================================================
fact, dim_vend, dim_prod, dim_cal = load_all()

if len(fact) == 0:
    st.markdown(f'<div style="text-align:center;padding:60px 20px;"><h3 style="color:{C["text"]};">Base indisponivel</h3><p style="color:{C["text_sec"]};">Execute <code style="background:{C["surface"]};color:{C["brand"]};">python src/run_pipeline.py</code></p></div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown(f'<div style="font-size:1.35rem;font-weight:700;color:{C["brand"]};letter-spacing:-0.03em;margin-top:-6px;">NEXUS</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.6rem;color:#64748B;margin-bottom:6px;">Dashboard Executivo</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:{C["text_muted"]};margin:14px 0 6px 0;">Menu</div>', unsafe_allow_html=True)
    pagina = st.radio("", ["Visao Executiva", "Vendedores", "Produtos", "Geografica"], label_visibility="collapsed")

    st.markdown(f'<div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:{C["text_muted"]};margin:14px 0 6px 0;">Filtros</div>', unsafe_allow_html=True)

    anos_uniq = sorted(fact["data_pedido"].apply(lambda x: str(x)[:4]).unique())
    ano_sel = st.selectbox("Ano", ["Todos"] + anos_uniq)

    regioes_uniq = sorted(fact["regiao"].unique())
    regiao_sel = st.multiselect("Regiao", regioes_uniq, default=[], placeholder="Todas")

    estados_uniq = sorted(fact["estado"].unique())
    estado_sel = st.multiselect("Estado", estados_uniq, default=[], placeholder="Todos")

    cats_uniq = sorted(dim_prod["categoria"].unique())
    cat_sel = st.multiselect("Categoria", cats_uniq, default=[], placeholder="Todas")

    st.markdown(f'<div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:{C["text_muted"]};margin:14px 0 6px 0;">Periodo</div>', unsafe_allow_html=True)

    all_dates_raw = pd.to_datetime(fact["data_pedido"])
    data_min_global = all_dates_raw.min().date()
    data_max_global = all_dates_raw.max().date()
    data_ini = st.date_input("Inicio", value=data_min_global, min_value=data_min_global, max_value=data_max_global)
    data_fim = st.date_input("Fim", value=data_max_global, min_value=data_min_global, max_value=data_max_global)

    st.markdown(f'<div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:{C["text_muted"]};margin:14px 0 6px 0;">Acoes</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Limpar", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Atualizar", use_container_width=True):
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
    st.info("Nenhum dado para os filtros selecionados.")
    st.stop()

# ---- shared KPIs ----
fat_total    = ff["total_pedido"].sum()
ped_total    = ff["pedido_id"].nunique()
tkt_medio    = fat_total / ped_total if ped_total > 0 else 0
vend_total   = ff["id_vendedor"].nunique()
dias_filtro  = (data_fim - data_ini).days or 1

# ---- previous period for deltas ----
prev_ini = data_ini - timedelta(days=dias_filtro)
prev_fim = data_ini - timedelta(days=1)
ff_prev = fact.copy()
ff_prev["_dt"] = pd.to_datetime(ff_prev["data_pedido"])
ff_prev = ff_prev[(ff_prev["_dt"] >= pd.Timestamp(prev_ini)) & (ff_prev["_dt"] <= pd.Timestamp(prev_fim))]
ff_prev = ff_prev.drop(columns=["_dt"])
fat_prev = ff_prev["total_pedido"].sum() if len(ff_prev) > 0 else None
ped_prev = ff_prev["pedido_id"].nunique() if len(ff_prev) > 0 else None
tkt_prev = fat_prev / ped_prev if ped_prev and ped_prev > 0 else None

# ---- best seller / region ----
dv_merged = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_v", "_d"))
top_seller_row = dv_merged.groupby("nome")["total_pedido"].sum().nlargest(1)
top_seller_name = top_seller_row.index[0] if len(top_seller_row) > 0 else "-"
top_seller_pct  = (top_seller_row.iloc[0] / fat_total * 100) if fat_total else 0

top_reg_row = ff.groupby("regiao")["total_pedido"].sum().nlargest(1)
top_reg_name = top_reg_row.index[0] if len(top_reg_row) > 0 else "-"
top_reg_pct  = (top_reg_row.iloc[0] / fat_total * 100) if fat_total else 0

# ---- MoM growth of last 2 months ----
ff_months = ff.copy()
ff_months["dt"] = pd.to_datetime(ff_months["data_pedido"])
ff_months["mes"] = ff_months["dt"].dt.to_period("M").astype(str)
monthly = ff_months.groupby("mes")["total_pedido"].sum().sort_index()
mom_growth = (monthly.iloc[-1] / monthly.iloc[-2] - 1) * 100 if len(monthly) >= 2 else None

# ---- last updated ----
now_br = datetime.now().strftime("%d/%m/%Y as %H:%M")

# =====================================================================
# TOP KPI BAND
# =====================================================================
st.markdown(f'<div style="color:{C["text_muted"]};font-size:0.6rem;margin-bottom:6px;">Ultima atualizacao: {now_br}</div>', unsafe_allow_html=True)
sc1, sc2, sc3, sc4, sc5 = st.columns(5)
with sc1:
    smart_kpi("📈", "Crescimento MoM",
              f"{mom_growth:+.1f}%" if mom_growth is not None else "--",
              "vs mes anterior")
with sc2:
    meta_pct = min(100, int(fat_total / 40_000_000 * 100))
    smart_kpi("🎯", "Meta (R$ 40 Mi)",
              f"{meta_pct}%",
              f"R$ {fat_total/1e6:.1f}Mi / R$ 40Mi")
with sc3:
    smart_kpi("🏆", "Melhor Vendedor",
              top_seller_name.split()[0],
              f"{top_seller_pct:.1f}% do total")
with sc4:
    smart_kpi("🌎", "Melhor Regiao",
              top_reg_name,
              f"{top_reg_pct:.1f}% do total")
with sc5:
    alert_text = "Estavel"
    alert_color = C["success"]
    if mom_growth is not None and mom_growth < 0:
        alert_text = f"Queda {abs(mom_growth):.1f}%"
        alert_color = C["danger"]
    elif mom_growth is not None and mom_growth > 15:
        alert_text = f"Alta {mom_growth:.1f}%"
        alert_color = C["success"]
    smart_kpi("⚡", "Alerta",
              alert_text,
              "Crescimento mensal")

st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

# =====================================================================
# PAGE 1 — VISÃO EXECUTIVA
# =====================================================================
if pagina == "Visao Executiva":

    # ---- ROW 0: KPI CARDS WITH DELTAS ----
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Faturamento", fmt(fat_total), delta_badge(fat_total, fat_prev))
    with c2: kpi_card("Total Pedidos", fmt_int(ped_total), delta_badge(ped_total, ped_prev))
    with c3: kpi_card("Ticket Medio", fmt(tkt_medio), delta_badge(tkt_medio, tkt_prev))
    with c4: kpi_card("Vendedores", vend_total)

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # ---- AUTO INSIGHTS ----
    i1, i2, i3 = st.columns(3)
    with i1: insight_card("💡", f"{top_reg_name} representa {top_reg_pct:.1f}% do faturamento total.", C["second"])
    with i2: insight_card("💡", f"{top_seller_name} e responsavel por {top_seller_pct:.1f}% das vendas.", C["brand_l"])
    with i3: insight_card("💡", f"Ticket medio de {fmt(tkt_medio)} — {'estavel nos ultimos meses' if mom_growth is not None and abs(mom_growth) < 5 else f'variacao de {mom_growth:+.1f}% vs mes anterior' if mom_growth is not None else 'sem historico suficiente'}.", C["second"])

    # ---- ROW 1: FAT. ESTADO + FAT. REGIÃO (compact) ----
    cr, cl = st.columns([1, 1])
    with cr:
        section_title("Faturamento por Estado")
        dfe = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfe, x="total_pedido", y="estado", orientation="h", color_discrete_sequence=[C["brand"]], labels={"total_pedido":"","estado":""})
        chart_config(fig, height=280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cl:
        section_title("Faturamento por Regiao")
        dfr = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = px.bar(dfr, x="total_pedido", y="regiao", orientation="h", color_discrete_sequence=[C["second"]], labels={"total_pedido":"","regiao":""})
        chart_config(fig, height=280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- ROW 2: RANKING VENDEDORES + TOP/BOTTOM MUNICIPIOS ----
    c1, c2 = st.columns([1, 1])
    with c1:
        section_title("Ranking Vendedores")
        rank = dv_merged.groupby(["nome", "regiao_d"], as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        rank.insert(0, "#", range(1, len(rank)+1))
        rank["Fat"] = rank["total_pedido"].apply(fmt)
        st.dataframe(rank[["#", "nome", "regiao_d", "Fat"]].rename(columns={"nome":"Vendedor","regiao_d":"Regiao","Fat":"Faturamento"}), use_container_width=True, hide_index=True, height=320)

    with c2:
        section_title("Top 5 e Bottom 5 Municipios")
        dm = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido")
        bottom = dm.head(5).copy()
        top = dm.tail(5).sort_values("total_pedido", ascending=False).copy()
        tb = pd.concat([top, bottom], ignore_index=True)
        tb["Fat"] = tb["total_pedido"].apply(fmt)
        tb["Tipo"] = ["Top"]*5 + ["Bottom"]*5
        st.dataframe(tb[["Tipo", "municipio", "Fat"]].rename(columns={"municipio":"Municipio","Fat":"Faturamento"}), use_container_width=True, hide_index=True, height=340)

    # ---- ROW 3: EVOLUÇÃO MENSAL (compact) ----
    section_title("Evolucao Mensal do Faturamento")
    fe = ff.copy()
    fe["dt"] = pd.to_datetime(ff["data_pedido"])
    fe["ano_mes"] = fe["dt"].dt.to_period("M").astype(str)
    dmes = fe.groupby("ano_mes", as_index=False).agg(total=("total_pedido","sum"), min_dt=("dt","min")).sort_values("ano_mes")
    dmes["label"] = dmes["min_dt"].dt.strftime("%b/%y")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dmes["label"], y=dmes["total"], mode="lines+markers",
                             line=dict(color=C["brand"], width=2),
                             fill="tozeroy", fillcolor="rgba(124,58,237,0.06)",
                             marker=dict(size=3, color=C["brand"])))
    chart_config(fig, height=240)
    fig.update_xaxes(tickangle=-30, tickfont_size=8)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# PAGE 2 — VENDEDORES
# =====================================================================
elif pagina == "Vendedores":

    dvf = dv_merged.groupby(["id_vendedor", "nome", "regiao_d"], as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    dvf["rank"] = range(1, len(dvf)+1)
    top1 = dvf.iloc[0] if len(dvf) > 0 else None
    fat_med = fat_total / vend_total if vend_total > 0 else 0

    c1, c2 = st.columns(2)
    with c1:
        nome_top = top1["nome"] if top1 is not None else "-"
        val_top = fmt(top1["total_pedido"]) if top1 is not None else ""
        kpi_card("Melhor Vendedor", f"{nome_top} — {val_top}")
    with c2:
        kpi_card("Fat. Medio por Vendedor", fmt(fat_med))

    section_title("Ranking Completo")
    rank_d = dvf.copy()
    rank_d["Faturamento"] = rank_d["total_pedido"].apply(fmt)
    rank_d["%"] = (rank_d["total_pedido"] / rank_d["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
    st.dataframe(rank_d[["rank","nome","regiao_d","Faturamento","%"]].rename(columns={"rank":"#","nome":"Vendedor","regiao_d":"Regiao"}), use_container_width=True, hide_index=True, height=460)

    cd, cr2 = st.columns([1, 1])
    with cd:
        section_title("Participacao %")
        fig = go.Figure(go.Pie(labels=dvf["nome"], values=dvf["total_pedido"], hole=0.6,
                               textinfo="percent", textfont=dict(size=9, color=C["text"], family="Inter"),
                               marker=dict(colors=[C["brand"],C["brand_l"],C["second"],C["second_l"],C["warn"]], line=dict(width=0))))
        chart_config(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cr2:
        section_title("Fat. por Regiao do Vendedor")
        dv_stacked = dvf.groupby(["regiao_d", "nome"], as_index=False)["total_pedido"].sum()
        fig = px.bar(dv_stacked, x="total_pedido", y="regiao_d", color="nome", orientation="h",
                     color_discrete_sequence=[C["brand"],C["brand_l"],C["second"],C["second_l"],C["warn"]],
                     labels={"total_pedido":"","regiao_d":""})
        chart_config(fig, height=300, showlegend=True)
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.12, font_size=7, title_text=""))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# PAGE 3 — PRODUTOS
# =====================================================================
elif pagina == "Produtos":

    fc = ff.merge(dim_prod, on="id_produto", how="left")

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Categorias", dim_prod["categoria"].nunique())
    with c2: kpi_card("Preco Medio", fmt(dim_prod["preco_venda"].mean()))
    with c3: kpi_card("Produtos Vendidos", ff["id_produto"].nunique())

    cc, cp = st.columns([1, 1])
    with cc:
        section_title("Faturamento por Categoria")
        dc = fc.groupby("categoria", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True)
        fig = go.Figure(go.Bar(y=dc["categoria"], x=dc["total_pedido"], orientation="h", marker=dict(color=C["brand"])))
        chart_config(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cp:
        section_title("Top 10 Produtos")
        dpt = fc.groupby("nome_produto", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(10)
        fig = go.Figure(go.Bar(y=dpt["nome_produto"], x=dpt["total_pedido"], orientation="h", marker=dict(color=C["second"])))
        chart_config(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section_title("Detalhamento por Categoria")
    dd = fc.groupby("categoria").agg(Faturamento=("total_pedido","sum"), Pedidos=("pedido_id","nunique"), Ticket=("total_pedido","mean"), Quantidade=("quantidade","sum")).reset_index()
    dd["Fat. Fmt"] = dd["Faturamento"].apply(fmt)
    dd["Tkt Fmt"] = dd["Ticket"].apply(fmt)
    st.dataframe(dd[["categoria","Fat. Fmt","Pedidos","Tkt Fmt","Quantidade"]].rename(columns={"categoria":"Categoria","Fat. Fmt":"Faturamento","Tkt Fmt":"Ticket Medio","Quantidade":"Qtd. Vendida"}), use_container_width=True, hide_index=True, height=240)

# =====================================================================
# PAGE 4 — GEOGRÁFICA
# =====================================================================
elif pagina == "Geografica":

    section_title("Faturamento por Estado")
    dfe2 = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    fig = go.Figure(go.Bar(y=dfe2["estado"], x=dfe2["total_pedido"], orientation="h", marker=dict(color=C["brand"])))
    chart_config(fig, height=300)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section_title("Faturamento por Regiao")
    dfr2 = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
    fig = go.Figure(go.Bar(y=dfr2["regiao"], x=dfr2["total_pedido"], orientation="h", marker=dict(color=C["second"])))
    chart_config(fig, height=260)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section_title("Top 15 Municipios")
    dm2 = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(15)
    fig = go.Figure(go.Bar(y=dm2["municipio"], x=dm2["total_pedido"], orientation="h", marker=dict(color=C["brand_l"])))
    chart_config(fig, height=340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# FOOTER
# =====================================================================
st.markdown("---")
st.caption(f"Nexus · Dados 2025–2026 · {fmt(fat_total)} · {fmt_int(ped_total)} pedidos · {vend_total} vendedores · [GitHub](https://github.com/Nagalli01/bi-ecommerce-dashboard)")
