#!/usr/bin/env python3
"""
Dashboard Profissional BI E-Commerce — Streamlit (Dark Mode | Real-Time)
Conecta ao MySQL bi_ecommerce e exibe 3 páginas de análise.
Execute: streamlit run src/dashboard_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sqlalchemy import create_engine, text
import os

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="BI E-Commerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# CSS DARK MODE PROFISSIONAL
# =====================================================================
st.markdown("""
<style>
    /* Fundo principal */
    .stApp { background-color: #1B1B1B; }
    .main { background-color: #1B1B1B; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #141414;
        border-right: 1px solid #2D2D2D;
    }
    [data-testid="stSidebar"] * { color: #AAAAAA; }
    
    /* Cards métricos */
    [data-testid="stMetric"] {
        background-color: #2D2D2D;
        border: 1px solid #3A3A3A;
        border-radius: 10px;
        padding: 16px;
    }
    [data-testid="stMetric"] label { color: #888888 !important; font-size: 0.8rem; }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 700; }
    
    /* Títulos */
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Segoe UI', sans-serif; }
    p, span, div { color: #AAAAAA; }
    
    /* Select boxes e filtros */
    .stSelectbox label, .stMultiselect label { color: #AAAAAA !important; }
    div[data-baseweb="select"] > div {
        background-color: #2D2D2D;
        border-color: #3A3A3A;
        color: #FFFFFF;
    }
    
    /* DataFrame / Tabelas */
    .stDataFrame { background-color: #2D2D2D; }
    .stDataFrame thead th { background-color: #2D2D2D !important; color: #FFFFFF !important; }
    .stDataFrame tbody td { background-color: #1B1B1B !important; color: #AAAAAA !important; }
    
    /* Esconder header padrão */
    header[data-testid="stHeader"] { background-color: #1B1B1B; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# CONEXÃO COM MYSQL
# =====================================================================
@st.cache_resource
def get_engine():
    return create_engine("mysql+pymysql://root:root@localhost:3306/bi_ecommerce")

@st.cache_data(ttl=30)
def query_df(sql):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)

# =====================================================================
# FUNÇÕES AUXILIARES — FORMATAR MOEDA
# =====================================================================
def fmt_brl(v):
    if abs(v) >= 1e6:
        return f"R$ {v/1e6:,.2f}M"
    elif abs(v) >= 1e3:
        return f"R$ {v/1e3:,.1f}K"
    return f"R$ {v:,.2f}"

# =====================================================================
# CARREGAR DADOS BASE
# =====================================================================
fact = query_df("SELECT * FROM fact_vendas")
dim_cli = query_df("SELECT * FROM dim_clientes")
dim_prod = query_df("SELECT * FROM dim_produtos")
dim_cal = query_df("SELECT * FROM dim_calendario")
dim_vend = query_df("SELECT * FROM dim_vendedores")

# Converter datas
fact['data_pedido'] = pd.to_datetime(fact['data_pedido'])
dim_cal['data'] = pd.to_datetime(dim_cal['data'])

# =====================================================================
# MÉTRICAS GLOBAIS
# =====================================================================
faturamento = fact['total_pedido'].sum()
total_pedidos = fact['pedido_id'].nunique()
ticket_medio = faturamento / total_pedidos if total_pedidos > 0 else 0
total_vendedores = fact['id_vendedor'].nunique()
total_categorias = dim_prod['categoria'].nunique()
preco_medio = dim_prod['preco_venda'].mean()
total_clientes = fact['id_cliente'].nunique()

# =====================================================================
# SIDEBAR — NAVEGAÇÃO + FILTROS
# =====================================================================
st.sidebar.markdown("## 🛒 BI E-Commerce")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Visão Executiva", "👥 Vendedores", "📦 Produtos & Categorias"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros Globais")

# Filtro de Ano
anos_disponiveis = sorted(fact['data_pedido'].dt.year.unique())
ano_sel = st.sidebar.selectbox("Ano", ["Todos"] + [str(a) for a in anos_disponiveis])

# Filtro de Região
regioes_disponiveis = sorted(fact['regiao'].unique())
regiao_sel = st.sidebar.multiselect("Região", regioes_disponiveis, default=regioes_disponiveis)

# Filtro de Estado
estados_disponiveis = sorted(fact['estado'].unique())
estado_sel = st.sidebar.multiselect("Estado", estados_disponiveis, default=[])

# Filtro de Categoria
cats_disponiveis = sorted(dim_prod['categoria'].unique())
cat_sel = st.sidebar.multiselect("Categoria", cats_disponiveis, default=[])

# Aplicar filtros
fact_f = fact.copy()
if ano_sel != "Todos":
    fact_f = fact_f[fact_f['data_pedido'].dt.year == int(ano_sel)]
if regiao_sel:
    fact_f = fact_f[fact_f['regiao'].isin(regiao_sel)]
if estado_sel:
    fact_f = fact_f[fact_f['estado'].isin(estado_sel)]
if cat_sel:
    produtos_filtrados = dim_prod[dim_prod['categoria'].isin(cat_sel)]['id_produto'].tolist()
    fact_f = fact_f[fact_f['id_produto'].isin(produtos_filtrados)]

# =====================================================================
# RECALCULAR MÉTRICAS COM FILTROS
# =====================================================================
fat_f = fact_f['total_pedido'].sum()
ped_f = fact_f['pedido_id'].nunique()
ticket_f = fat_f / ped_f if ped_f > 0 else 0
vend_f = fact_f['id_vendedor'].nunique()
cli_f = fact_f['id_cliente'].nunique()

# =====================================================================
# PÁGINA 1 — VISÃO EXECUTIVA
# =====================================================================
if pagina == "📊 Visão Executiva":
    st.markdown('<h2 style="color:#4A90D9; margin-bottom:0;">📊 Visão Executiva</h2>', unsafe_allow_html=True)
    st.markdown('<p style="margin-top:0; color:#888;">Receita · Pedidos · Geografia · Tendência</p>', unsafe_allow_html=True)
    
    # LINHA 0 — KPI CARDS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Faturamento", fmt_brl(fat_f))
    with c2:
        st.metric("Total Pedidos", f"{ped_f:,}")
    with c3:
        st.metric("Ticket Médio", fmt_brl(ticket_f))
    with c4:
        st.metric("Vendedores", vend_f)
    
    st.markdown("---")
    
    # LINHA 1 — MAPA + RANKING
    c_mapa, c_rank = st.columns([1, 1])
    
    with c_mapa:
        st.markdown("### 🗺️ Faturamento por Estado")
        
        try:
            gdf = __import__('geopandas').read_file(
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'data', 'brazil_states.geojson')
            )
            df_estado = fact_f.groupby('estado')['total_pedido'].sum().reset_index()
            gdf = gdf.merge(df_estado, left_on='sigla', right_on='estado', how='left')
            gdf['total_pedido'] = gdf['total_pedido'].fillna(0)
            
            fig = px.choropleth_mapbox(
                gdf, geojson=gdf.geometry, locations=gdf.index,
                color='total_pedido', color_continuous_scale='Reds',
                mapbox_style='carto-darkmatter',
                center={'lat': -14, 'lon': -55}, zoom=3,
                opacity=0.85,
                labels={'total_pedido': 'Faturamento'},
                hover_data={'sigla': True, 'total_pedido': ':.2f'}
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='#1B1B1B',
                plot_bgcolor='#1B1B1B',
                height=450,
                coloraxis_colorbar=dict(
                    title='R$', tickfont=dict(color='#AAAAAA'),
                    titlefont=dict(color='#AAAAAA')
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Mapa indisponível: {e}")
            df_estado = fact_f.groupby('estado')['total_pedido'].sum().reset_index().sort_values('total_pedido', ascending=False)
            fig = px.bar(df_estado, x='total_pedido', y='estado', orientation='h',
                         color_discrete_sequence=['#4A90D9'])
            fig.update_layout(paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
                            font_color='#AAAAAA', height=450, margin=dict(l=0,r=0,t=0,b=0))
            fig.update_xaxes(gridcolor='#3A3A3A')
            st.plotly_chart(fig, use_container_width=True)
    
    with c_rank:
        st.markdown("### 👥 Ranking de Vendedores")
        df_vend_rank = fact_f.merge(dim_vend, on='id_vendedor', how='left')
        df_vr = df_vend_rank.groupby(['id_vendedor', 'nome'])['total_pedido'].sum().reset_index()
        df_vr = df_vr.sort_values('total_pedido', ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_vr['nome'], x=df_vr['total_pedido'],
            orientation='h', marker=dict(color='#4A90D9', line=dict(color='#357ABD', width=1)),
            text=[fmt_brl(v) for v in df_vr['total_pedido']],
            textposition='outside', textfont=dict(color='#AAAAAA', size=11),
            hovertemplate='%{y}: %{x:,.2f}<extra></extra>'
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=450,
            margin=dict(l=0, r=100, t=0, b=0),
            xaxis=dict(gridcolor='#3A3A3A', zeroline=False),
            yaxis=dict(gridcolor='#3A3A3A'),
            showlegend=False,
            title=dict(text='Faturamento por Vendedor', font=dict(color='#AAAAAA', size=14), x=0.3)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # LINHA 2 — MUNICÍPIOS + EVOLUÇÃO
    c_muni, c_evo = st.columns([1, 1])
    
    with c_muni:
        st.markdown("### 🏙️ Top 10 Municípios")
        df_muni = fact_f.groupby('municipio')['total_pedido'].sum().reset_index()
        df_muni = df_muni.sort_values('total_pedido', ascending=True).tail(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_muni['municipio'], x=df_muni['total_pedido'],
            orientation='h', marker=dict(color='#4A90D9'),
            text=[fmt_brl(v) for v in df_muni['total_pedido']],
            textposition='outside', textfont=dict(color='#AAAAAA', size=10),
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=380,
            margin=dict(l=0, r=80, t=0, b=0),
            xaxis=dict(gridcolor='#3A3A3A'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with c_evo:
        st.markdown("### 📈 Evolução Mensal")
        fact_f_month = fact_f.copy()
        fact_f_month['mes'] = fact_f_month['data_pedido'].dt.to_period('M').astype(str)
        df_mes = fact_f_month.groupby('mes')['total_pedido'].sum().reset_index()
        df_mes = df_mes.sort_values('mes')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_mes['mes'], y=df_mes['total_pedido'],
            mode='lines+markers+text',
            line=dict(color='#4A90D9', width=3),
            fill='tozeroy', fillcolor='rgba(74,144,217,0.12)',
            marker=dict(size=7, color='#4A90D9', line=dict(width=2, color='#1B1B1B')),
            text=[fmt_brl(v) for v in df_mes['total_pedido']],
            textposition='top center', textfont=dict(color='#AAAAAA', size=9),
            hovertemplate='%{x}: %{y:,.2f}<extra></extra>'
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=380,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(gridcolor='#3A3A3A', tickangle=-45),
            yaxis=dict(gridcolor='#3A3A3A'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# PÁGINA 2 — VENDEDORES
# =====================================================================
elif pagina == "👥 Vendedores":
    st.markdown('<h2 style="color:#4A90D9; margin-bottom:0;">👥 Análise de Vendedores</h2>', unsafe_allow_html=True)
    st.markdown('<p style="margin-top:0; color:#888;">Performance · Participação · Ranking</p>', unsafe_allow_html=True)
    
    # KPI Cards
    # Melhor vendedor
    df_vend_full = fact_f.merge(dim_vend, on='id_vendedor', how='left')
    df_vf = df_vend_full.groupby(['id_vendedor', 'nome', 'regiao'])['total_pedido'].sum().reset_index()
    df_vf = df_vf.sort_values('total_pedido', ascending=False)
    
    melhor = df_vf.iloc[0] if len(df_vf) > 0 else None
    fat_medio_vend = fat_f / vend_f if vend_f > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    with c1:
        nome_melhor = melhor['nome'] if melhor is not None else "-"
        fat_melhor = melhor['total_pedido'] if melhor is not None else 0
        st.metric("Melhor Vendedor", nome_melhor, delta=fmt_brl(fat_melhor))
    with c2:
        st.metric("Faturamento Médio/Vendedor", fmt_brl(fat_medio_vend))
    with c3:
        st.metric("Total Vendedores Ativos", vend_f)
    
    st.markdown("---")
    
    c_donut, c_regiao = st.columns([1, 1])
    
    with c_donut:
        st.markdown("### 🍩 Participação por Vendedor")
        df_vf['pct'] = df_vf['total_pedido'] / df_vf['total_pedido'].sum() * 100
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=df_vf['nome'], values=df_vf['total_pedido'],
            hole=0.55, textinfo='percent', textfont=dict(size=10, color='#FFFFFF'),
            marker=dict(colors=px.colors.sequential.Blues_r, line=dict(color='#1B1B1B', width=1)),
            hovertemplate='%{label}: %{percent}<br>%{value:,.2f}<extra></extra>'
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=420, margin=dict(l=0, r=0, t=0, b=0),
            annotations=[dict(text=f'{df_vf["total_pedido"].sum()/1e6:.1f}M', x=0.5, y=0.5,
                            font=dict(size=20, color='#FFFFFF'), showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with c_regiao:
        st.markdown("### 📍 Faturamento por Região")
        df_reg = df_vf.groupby('regiao')['total_pedido'].sum().reset_index().sort_values('total_pedido', ascending=True)
        df_reg['pct'] = df_reg['total_pedido'] / df_reg['total_pedido'].sum() * 100
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_reg['regiao'], x=df_reg['total_pedido'], orientation='h',
            marker=dict(color='#4A90D9'),
            text=[f"{fmt_brl(v)} ({p:.0f}%)" for v, p in zip(df_reg['total_pedido'], df_reg['pct'])],
            textposition='outside', textfont=dict(color='#AAAAAA', size=11),
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=420,
            margin=dict(l=0, r=120, t=0, b=0),
            xaxis=dict(gridcolor='#3A3A3A'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela completa
    st.markdown("### 📋 Ranking Completo de Vendedores")
    df_vf['Ranking'] = range(1, len(df_vf) + 1)
    df_vf['Faturamento'] = df_vf['total_pedido'].apply(fmt_brl)
    df_vf['Participação'] = df_vf['pct'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(
        df_vf[['Ranking', 'nome', 'regiao', 'Faturamento', 'Participação']].rename(
            columns={'nome': 'Vendedor', 'regiao': 'Região'}
        ),
        use_container_width=True,
        hide_index=True,
        height=530,
    )

# =====================================================================
# PÁGINA 3 — PRODUTOS & CATEGORIAS
# =====================================================================
elif pagina == "📦 Produtos & Categorias":
    st.markdown('<h2 style="color:#4A90D9; margin-bottom:0;">📦 Produtos & Categorias</h2>', unsafe_allow_html=True)
    st.markdown('<p style="margin-top:0; color:#888;">Categorias · Top Produtos · Ticket Médio</p>', unsafe_allow_html=True)
    
    # KPI Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Categorias", total_categorias)
    with c2:
        st.metric("Preço Médio", fmt_brl(preco_medio))
    with c3:
        prods_vendidos = fact_f['id_produto'].nunique()
        st.metric("Produtos Vendidos", prods_vendidos)
    
    st.markdown("---")
    
    c_cat, c_prod = st.columns([1, 1])
    
    with c_cat:
        st.markdown("### 📊 Faturamento por Categoria")
        fact_cat = fact_f.merge(dim_prod, on='id_produto', how='left')
        df_cat = fact_cat.groupby('categoria')['total_pedido'].sum().reset_index().sort_values('total_pedido', ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_cat['categoria'], x=df_cat['total_pedido'], orientation='h',
            marker=dict(color='#4A90D9'),
            text=[fmt_brl(v) for v in df_cat['total_pedido']],
            textposition='outside', textfont=dict(color='#AAAAAA', size=11),
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=420,
            margin=dict(l=0, r=100, t=0, b=0),
            xaxis=dict(gridcolor='#3A3A3A'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with c_prod:
        st.markdown("### 🏆 Top 10 Produtos")
        df_prod_top = fact_cat.groupby(['id_produto', 'nome_produto'])['total_pedido'].sum().reset_index()
        df_prod_top = df_prod_top.sort_values('total_pedido', ascending=True).tail(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_prod_top['nome_produto'], x=df_prod_top['total_pedido'], orientation='h',
            marker=dict(color='#4A90D9'),
            text=[fmt_brl(v) for v in df_prod_top['total_pedido']],
            textposition='outside', textfont=dict(color='#AAAAAA', size=10),
        ))
        fig.update_layout(
            paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
            font_color='#AAAAAA', height=420,
            margin=dict(l=0, r=100, t=0, b=0),
            xaxis=dict(gridcolor='#3A3A3A'),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 Detalhamento por Categoria")
    
    # Métricas por categoria
    df_detalhe = fact_cat.groupby('categoria').agg(
        Faturamento=('total_pedido', 'sum'),
        Pedidos=('pedido_id', 'nunique'),
        Ticket_Medio=('total_pedido', 'mean'),
        Quantidade_Vendida=('quantidade', 'sum'),
    ).reset_index()
    df_detalhe = df_detalhe.sort_values('Faturamento', ascending=False)
    df_detalhe['Faturamento_FMT'] = df_detalhe['Faturamento'].apply(fmt_brl)
    df_detalhe['Ticket_Medio_FMT'] = df_detalhe['Ticket_Medio'].apply(fmt_brl)
    
    st.dataframe(
        df_detalhe[['categoria', 'Faturamento_FMT', 'Pedidos', 'Ticket_Medio_FMT', 'Quantidade_Vendida']].rename(
            columns={
                'categoria': 'Categoria',
                'Faturamento_FMT': 'Faturamento',
                'Pedidos': 'Pedidos',
                'Ticket_Medio_FMT': 'Ticket Médio',
                'Quantidade_Vendida': 'Qtd. Vendida',
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=300,
    )
    
    st.markdown("---")
    st.markdown("### 📦 Quantidade Vendida por Produto (Top 25)")
    df_qtd = fact_cat.groupby(['id_produto', 'nome_produto'])['quantidade'].sum().reset_index()
    df_qtd = df_qtd.sort_values('quantidade', ascending=True).tail(25)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_qtd['nome_produto'], x=df_qtd['quantidade'], orientation='h',
        marker=dict(color='#4A90D9'),
        text=df_qtd['quantidade'].apply(lambda x: f"{x:,}"),
        textposition='outside', textfont=dict(color='#AAAAAA', size=9),
    ))
    fig.update_layout(
        paper_bgcolor='#1B1B1B', plot_bgcolor='#1B1B1B',
        font_color='#AAAAAA', height=600,
        margin=dict(l=0, r=60, t=0, b=0),
        xaxis=dict(gridcolor='#3A3A3A'),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# RODAPÉ
# =====================================================================
st.sidebar.markdown("---")
st.sidebar.caption(f"Clientes ativos: {cli_f} | Produtos: {prods_vendidos}")
st.sidebar.caption(f"Dados em tempo real — MySQL bi_ecommerce")
