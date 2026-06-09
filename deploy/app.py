#!/usr/bin/env python3
"""
Nexus Dashboard v4.0 — Executive Decision Intelligence
Professional dark theme, SVG icons, dense layout, dynamic insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Nexus BI", layout="wide", initial_sidebar_state="expanded")

# =====================================================================
# CSS — ENTERPRISE v4
# =====================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ---------- RESET & BASE ---------- */
*, *::before, *::after { box-sizing: border-box; }
.stApp * { font-family: 'Inter', system-ui, sans-serif !important; }
.stApp, .main { background-color: #080E1C; padding-top: 0 !important; }
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"], #MainMenu, footer,
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: #0D1422 !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
    width: 230px !important;
    min-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; overflow-y: auto !important; overflow-x: hidden !important; }

/* Collapse button — SVG-safe */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    background: #0D1422 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 6px !important;
}

/* ---------- SIDEBAR: NAV BUTTONS ---------- */
.nav-btn {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    padding: 7px 10px !important;
    margin: 1px 0 !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    background: transparent !important;
    border: none !important;
    cursor: pointer !important;
    transition: all 0.12s ease !important;
    text-align: left !important;
    font-family: 'Inter', sans-serif !important;
}
.nav-btn:hover { background: rgba(109,40,217,0.12) !important; color: #A78BFA !important; }
.nav-btn.nav-active { background: rgba(109,40,217,0.18) !important; color: #C4B5FD !important; }

/* ---------- INPUTS ---------- */
div[data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    transition: border-color 0.15s !important;
}
div[data-baseweb="select"] > div:hover { border-color: rgba(109,40,217,0.5) !important; }
div[data-baseweb="select"] > div:focus-within { border-color: #6D28D9 !important; box-shadow: 0 0 0 2px rgba(109,40,217,0.15) !important; }
[data-baseweb="popover"], [data-baseweb="menu"] { background: #111827 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important; }
[data-baseweb="option"]:hover { background: rgba(109,40,217,0.15) !important; }
[data-baseweb="tag"] { background: rgba(109,40,217,0.25) !important; border: 1px solid rgba(109,40,217,0.4) !important; border-radius: 4px !important; }
[data-baseweb="tag"] span { color: #C4B5FD !important; font-size: 0.75rem !important; }

.stSelectbox label, .stMultiselect label, .stDateInput label {
    font-size: 0.62rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.7px !important;
    color: #475569 !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}

input[type="date"] {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    padding: 6px 10px !important;
}

/* ---------- BUTTONS ---------- */
.stButton button {
    background: transparent !important;
    color: #A78BFA !important;
    border: 1px solid rgba(109,40,217,0.35) !important;
    border-radius: 8px !important;
    padding: 5px 14px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}
.stButton button:hover {
    background: rgba(109,40,217,0.15) !important;
    border-color: #7C3AED !important;
    color: #C4B5FD !important;
    transform: translateY(-1px) !important;
}
.stButton button:active { transform: translateY(0px) !important; }

/* ---------- DATAFRAME ---------- */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] thead th {
    background: #0D1422 !important;
    color: #475569 !important;
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    padding: 8px 12px !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stDataFrame"] tbody td {
    font-size: 0.78rem !important;
    padding: 7px 12px !important;
    color: #CBD5E1 !important;
    border-bottom: 1px solid rgba(255,255,255,0.03) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td { background: rgba(109,40,217,0.06) !important; }

/* ---------- SCROLLBAR ---------- */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ---------- MISC ---------- */
hr { border: none; border-top: 1px solid rgba(255,255,255,0.04); margin: 8px 0; }
*:focus { outline: none !important; }

/* ---------- MAIN LAYOUT WRAPPER ---------- */
.nexus-main {
    padding: 14px 28px 12px 28px;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =====================================================================
# COLOR SYSTEM
# =====================================================================
C = {
    "brand":       "#7C3AED",
    "brand_l":     "#A78BFA",
    "brand_d":     "#4C1D95",
    "second":      "#0EA5E9",
    "second_l":    "#38BDF8",
    "success":     "#10B981",
    "warn":        "#F59E0B",
    "danger":      "#EF4444",
    "bg":          "#080E1C",
    "bg2":         "#0D1422",
    "sidebar":     "#0D1422",
    "surface":     "#111827",
    "surface2":    "#1A2234",
    "border":      "rgba(255,255,255,0.05)",
    "border2":     "rgba(255,255,255,0.08)",
    "text":        "#F1F5F9",
    "text_sec":    "#94A3B8",
    "text_muted":  "#475569",
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
    v = float(v) if not isinstance(v, float) else v
    if abs(v) >= 1e9: return f"R$ {v/1e9:,.2f}Bi"
    if abs(v) >= 1e6: return f"R$ {v/1e6:,.1f}Mi"
    if abs(v) >= 1e3: return f"R$ {v/1e3:,.0f}K"
    return f"R$ {v:,.2f}"

def fmt_int(v):
    return f"{int(v):,}".replace(",", ".")

def delta_badge(current, previous):
    if previous is None or previous == 0: return None
    pct = (current - previous) / previous * 100
    if pct >= 0:
        return f'<span style="display:inline-flex;align-items:center;gap:2px;color:{C["success"]};font-size:0.7rem;font-weight:600;background:rgba(16,185,129,0.1);padding:2px 7px;border-radius:20px;">▲ +{pct:.1f}%</span>'
    else:
        return f'<span style="display:inline-flex;align-items:center;gap:2px;color:{C["danger"]};font-size:0.7rem;font-weight:600;background:rgba(239,68,68,0.1);padding:2px 7px;border-radius:20px;">▼ {pct:.1f}%</span>'

def chart_config(fig, height=260, showlegend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter", font_color=C["text_sec"], font_size=10,
        height=height, margin=dict(l=0, r=4, t=4, b=0),
        xaxis=dict(showgrid=False, zeroline=False, tickfont_size=9, tickfont_color=C["text_muted"],
                   showline=False),
        yaxis=dict(showgrid=False, zeroline=False, tickfont_size=9, tickfont_color=C["text_muted"],
                   showline=False),
        showlegend=showlegend,
        hoverlabel=dict(bgcolor=C["surface2"], bordercolor=C["border2"],
                        font_family="Inter", font_color=C["text"], font_size=12),
    )
    return fig

def bar_chart(df, x, y, color, height=240, orientation="h"):
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y],
        orientation=orientation,
        marker=dict(
            color=color,
            opacity=0.85,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>" if orientation == "h"
                      else "<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    chart_config(fig, height=height)
    return fig

# ---- UI COMPONENTS ----

def sidebar_section(label):
    st.markdown(
        f'<div style="font-size:0.58rem;text-transform:uppercase;letter-spacing:1.2px;'
        f'color:{C["text_muted"]};font-weight:700;padding:14px 16px 5px 16px;'
        f'margin:0;">{label}</div>',
        unsafe_allow_html=True
    )

def section_header(text, sub=None):
    sub_html = f'<span style="font-size:0.72rem;color:{C["text_muted"]};font-weight:400;margin-left:10px;">{sub}</span>' if sub else ""
    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:0;margin:12px 0 8px 0;">'
        f'<span style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;'
        f'color:{C["text_sec"]};font-weight:600;">{text}</span>{sub_html}</div>',
        unsafe_allow_html=True
    )

def kpi_card(label, value, delta_str=None, icon_svg=None, accent=None):
    accent = accent or C["brand"]
    delta_html = f'<div style="margin-top:8px;">{delta_str}</div>' if delta_str else ""
    icon_html = (
        f'<div style="width:32px;height:32px;border-radius:8px;background:rgba(124,58,237,0.12);'
        f'display:flex;align-items:center;justify-content:center;margin-bottom:10px;">'
        f'{icon_svg}</div>'
    ) if icon_svg else ""
    st.markdown(f"""
    <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:12px;
         padding:18px 20px;position:relative;overflow:hidden;
         box-shadow:0 1px 3px rgba(0,0,0,0.3),0 8px 24px rgba(0,0,0,0.15);">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;
             background:linear-gradient(90deg,{accent},transparent);"></div>
        {icon_html}
        <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.8px;
             color:{C['text_muted']};font-weight:600;margin-bottom:6px;">{label}</div>
        <div style="font-size:1.5rem;font-weight:700;color:{C['text']};
             letter-spacing:-0.03em;line-height:1;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def smart_kpi(label, value, sub="", accent=None, icon_svg=None):
    accent = accent or C["brand"]
    icon_html = icon_svg or ""
    st.markdown(f"""
    <div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;
         padding:12px 16px;display:flex;align-items:center;gap:12px;
         box-shadow:0 1px 3px rgba(0,0,0,0.25);">
        <div style="width:36px;height:36px;border-radius:9px;
             background:rgba(0,0,0,0.2);flex-shrink:0;
             display:flex;align-items:center;justify-content:center;">
            {icon_html}
        </div>
        <div style="min-width:0;">
            <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.6px;
                 color:{C['text_muted']};font-weight:600;white-space:nowrap;">{label}</div>
            <div style="font-size:1.05rem;font-weight:700;color:{C['text']};
                 line-height:1.2;margin-top:1px;white-space:nowrap;overflow:hidden;
                 text-overflow:ellipsis;">{value}</div>
            <div style="font-size:0.62rem;color:{C['text_muted']};margin-top:1px;">{sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def insight_card(text, color=None, icon_svg=None):
    col = color or C["second"]
    icon_html = icon_svg or ""
    st.markdown(f"""
    <div style="background:{C['surface']};border:1px solid {C['border']};
         border-left:3px solid {col};border-radius:0 10px 10px 0;padding:11px 14px;
         margin:4px 0;display:flex;align-items:flex-start;gap:10px;">
        <span style="flex-shrink:0;margin-top:1px;">{icon_html}</span>
        <span style="color:{C['text_sec']};font-size:0.76rem;line-height:1.5;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle=None):
    sub_html = f'<div style="font-size:0.8rem;color:{C["text_muted"]};margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <h1 style="font-size:1.25rem;font-weight:700;color:{C['text']};
             letter-spacing:-0.02em;margin:0;">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def divider():
    st.markdown(f'<hr style="border:none;border-top:1px solid {C["border"]};margin:14px 0;">', unsafe_allow_html=True)

def spacer(h=8):
    st.markdown(f'<div style="height:{h}px;"></div>', unsafe_allow_html=True)

# ---- SVG ICONS ----
def icon(name, color="#A78BFA", size=16):
    icons = {
        "trending_up": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
        "target":      f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
        "award":       f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>',
        "map_pin":     f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
        "alert":       f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        "dollar":      f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
        "shopping":    f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>',
        "receipt":     f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/></svg>',
        "users":       f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "box":         f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>',
        "tag":         f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>',
        "globe":       f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "lightbulb":   f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg>',
        "bar_chart":   f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
    }
    return icons.get(name, "")

# =====================================================================
# LOAD DATA
# =====================================================================
fact, dim_vend, dim_prod, dim_cal = load_all()

if len(fact) == 0:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
         height:80vh;text-align:center;">
        <div style="font-size:2rem;margin-bottom:16px;opacity:.3;">!</div>
        <h3 style="color:{C['text']};margin:0;">Base de dados indisponivel</h3>
        <p style="color:{C['text_muted']};margin-top:8px;">
            Execute <code style="background:{C['surface']};color:{C['brand_l']};
            padding:2px 8px;border-radius:4px;">python src/run_pipeline.py</code>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="padding:20px 16px 0 16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
            <div style="width:28px;height:28px;border-radius:7px;
                 background:linear-gradient(135deg,{C['brand']},{C['second']});
                 display:flex;align-items:center;justify-content:center;">
                {icon("bar_chart","#fff",13)}
            </div>
            <span style="font-size:1.1rem;font-weight:700;color:{C['text']};
                  letter-spacing:-0.04em;">nexus</span>
        </div>
        <div style="font-size:0.6rem;color:{C['text_muted']};
             padding-left:38px;margin-bottom:4px;">Inteligencia Executiva</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<hr style="border:none;border-top:1px solid {C["border"]};margin:12px 0 6px 0;">', unsafe_allow_html=True)

    # Navigation
    sidebar_section("Navegacao")
    st.markdown('<div style="padding:4px 8px;">', unsafe_allow_html=True)

    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "Visao Executiva"

    pages = ["Visao Executiva", "Vendedores", "Produtos", "Geografica"]
    for p in pages:
        active = "nav-active" if st.session_state.nav_page == p else ""
        if st.button(p, key=f"nav_{p}", use_container_width=True,
                     type="secondary",
                     help=""):
            st.session_state.nav_page = p
            st.rerun()

    pagina = st.session_state.nav_page
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<hr style="border:none;border-top:1px solid {C["border"]};margin:10px 0 4px 0;">', unsafe_allow_html=True)

    # Filters
    sidebar_section("Filtros")
    st.markdown('<div style="padding:0 10px;">', unsafe_allow_html=True)

    anos_uniq = sorted(fact["data_pedido"].apply(lambda x: str(x)[:4]).unique())
    ano_sel = st.selectbox("Ano", ["Todos"] + anos_uniq)

    regioes_uniq = sorted(fact["regiao"].unique())
    regiao_sel = st.multiselect("Regiao", regioes_uniq, default=[], placeholder="Todas")

    estados_uniq = sorted(fact["estado"].unique())
    estado_sel = st.multiselect("Estado", estados_uniq, default=[], placeholder="Todos")

    cats_uniq = sorted(dim_prod["categoria"].unique())
    cat_sel = st.multiselect("Categoria", cats_uniq, default=[], placeholder="Todas")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<hr style="border:none;border-top:1px solid {C["border"]};margin:10px 0 4px 0;">', unsafe_allow_html=True)
    sidebar_section("Periodo")
    st.markdown('<div style="padding:0 10px;">', unsafe_allow_html=True)

    all_dates_raw = pd.to_datetime(fact["data_pedido"])
    data_min_global = all_dates_raw.min().date()
    data_max_global = all_dates_raw.max().date()
    data_ini = st.date_input("Inicio", value=data_min_global, min_value=data_min_global, max_value=data_max_global)
    data_fim = st.date_input("Fim",    value=data_max_global, min_value=data_min_global, max_value=data_max_global)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<hr style="border:none;border-top:1px solid {C["border"]};margin:10px 0 8px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 10px 16px 10px;">', unsafe_allow_html=True)
    c1b, c2b = st.columns(2)
    with c1b:
        if st.button("Limpar", use_container_width=True): st.rerun()
    with c2b:
        if st.button("Aplicar", use_container_width=True): st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer info
    now_br = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div style="padding:12px 16px;border-top:1px solid {C['border']};
         font-size:0.58rem;color:{C['text_muted']};">
        Atualizado {now_br}
    </div>
    """, unsafe_allow_html=True)

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
    df = df.copy()
    df["_data_dt"] = pd.to_datetime(df["data_pedido"])
    df = df[(df["_data_dt"] >= pd.Timestamp(data_ini)) & (df["_data_dt"] <= pd.Timestamp(data_fim))]
    return df.drop(columns=["_data_dt"])

ff = filtrar(fact)

if len(ff) == 0:
    st.markdown(f"""
    <div style="text-align:center;padding:80px 20px;color:{C['text_muted']};">
        <div style="font-size:1.8rem;opacity:.3;margin-bottom:12px;">--</div>
        <div style="font-size:0.9rem;">Nenhum dado para os filtros selecionados.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---- Shared KPIs ----
fat_total   = ff["total_pedido"].sum()
ped_total   = ff["pedido_id"].nunique()
tkt_medio   = fat_total / ped_total if ped_total > 0 else 0
vend_total  = ff["id_vendedor"].nunique()
dias_filtro = (data_fim - data_ini).days or 1

# ---- Previous period ----
prev_ini = data_ini - timedelta(days=dias_filtro)
prev_fim = data_ini - timedelta(days=1)
ff_prev = fact.copy()
ff_prev["_dt"] = pd.to_datetime(ff_prev["data_pedido"])
ff_prev = ff_prev[(ff_prev["_dt"] >= pd.Timestamp(prev_ini)) & (ff_prev["_dt"] <= pd.Timestamp(prev_fim))].drop(columns=["_dt"])
fat_prev = ff_prev["total_pedido"].sum() if len(ff_prev) > 0 else None
ped_prev = ff_prev["pedido_id"].nunique() if len(ff_prev) > 0 else None
tkt_prev = fat_prev / ped_prev if ped_prev and ped_prev > 0 else None

# ---- Best seller / region ----
dv_merged = ff.merge(dim_vend, on="id_vendedor", how="left", suffixes=("_v", "_d"))
top_seller_row = dv_merged.groupby("nome")["total_pedido"].sum().nlargest(1)
top_seller_name = top_seller_row.index[0] if len(top_seller_row) > 0 else "-"
top_seller_pct  = (top_seller_row.iloc[0] / fat_total * 100) if fat_total else 0
top_seller_val  = top_seller_row.iloc[0] if len(top_seller_row) > 0 else 0

top_reg_row  = ff.groupby("regiao")["total_pedido"].sum().nlargest(1)
top_reg_name = top_reg_row.index[0] if len(top_reg_row) > 0 else "-"
top_reg_pct  = (top_reg_row.iloc[0] / fat_total * 100) if fat_total else 0

# ---- MoM ----
ff_months = ff.copy()
ff_months["dt"]  = pd.to_datetime(ff_months["data_pedido"])
ff_months["mes"] = ff_months["dt"].dt.to_period("M").astype(str)
monthly    = ff_months.groupby("mes")["total_pedido"].sum().sort_index()
mom_growth = (monthly.iloc[-1] / monthly.iloc[-2] - 1) * 100 if len(monthly) >= 2 else None

# ---- Dynamic insights ----
def build_insights():
    insights = []
    # Insight 1: MoM trend
    if mom_growth is not None:
        if mom_growth > 10:
            insights.append((f"Crescimento acelerado: faturamento subiu <b>{mom_growth:+.1f}%</b> no ultimo mes — ritmo acima da media historica.", C["success"]))
        elif mom_growth < -5:
            insights.append((f"Atencao: queda de <b>{abs(mom_growth):.1f}%</b> no ultimo mes. Avalie sazonalidade e acoes de recuperacao.", C["danger"]))
        else:
            insights.append((f"Evolucao estavel: variacao de <b>{mom_growth:+.1f}%</b> no ultimo mes, dentro da banda de crescimento.", C["second"]))
    # Insight 2: Concentration risk
    if top_seller_pct > 25:
        insights.append((f"Concentracao: <b>{top_seller_name}</b> representa <b>{top_seller_pct:.1f}%</b> do faturamento — risco de dependencia de um unico vendedor.", C["warn"]))
    else:
        insights.append((f"Carteira equilibrada: <b>{top_seller_name}</b> lidera com <b>{top_seller_pct:.1f}%</b> — boa distribuicao entre vendedores.", C["success"]))
    # Insight 3: Meta progress
    meta_pct = fat_total / 40_000_000 * 100
    falta = 40_000_000 - fat_total
    if meta_pct >= 100:
        insights.append((f"Meta atingida: {fmt(fat_total)} — <b>{meta_pct:.1f}%</b> da meta anual de R$ 40Mi superada.", C["success"]))
    elif meta_pct >= 75:
        insights.append((f"Proximo da meta: <b>{meta_pct:.1f}%</b> concluido. Faltam {fmt(falta)} para atingir R$ 40Mi.", C["second"]))
    else:
        insights.append((f"Meta em andamento: {fmt(fat_total)} realizados (<b>{meta_pct:.1f}%</b>). Faltam {fmt(falta)} para R$ 40Mi.", C["warn"]))
    return insights

all_insights = build_insights()

# =====================================================================
# MAIN CONTENT WRAPPER
# =====================================================================
st.markdown('<div class="nexus-main">', unsafe_allow_html=True)

# =====================================================================
# TOP KPI BAND — sempre visivel
# =====================================================================
alert_text  = "Estavel"
alert_color = C["success"]
alert_icon  = "alert"
if mom_growth is not None and mom_growth < -5:
    alert_text  = f"Queda {abs(mom_growth):.1f}%"
    alert_color = C["danger"]
elif mom_growth is not None and mom_growth > 15:
    alert_text  = f"Alta {mom_growth:.1f}%"
    alert_color = C["success"]

meta_pct = min(100, int(fat_total / 40_000_000 * 100))

sk1, sk2, sk3, sk4, sk5 = st.columns(5)
with sk1:
    smart_kpi(
        "Crescimento MoM",
        f"{mom_growth:+.1f}%" if mom_growth is not None else "--",
        "vs. mes anterior",
        accent=C["brand"],
        icon_svg=icon("trending_up", C["brand_l"], 16),
    )
with sk2:
    smart_kpi(
        "Meta R$ 40 Mi",
        f"{meta_pct}%",
        f"{fmt(fat_total)} realizados",
        accent=C["second"],
        icon_svg=icon("target", C["second_l"], 16),
    )
with sk3:
    first_name = top_seller_name.split()[0] if top_seller_name != "-" else "-"
    smart_kpi(
        "Melhor Vendedor",
        first_name,
        f"{top_seller_pct:.1f}% do total",
        accent=C["warn"],
        icon_svg=icon("award", C["warn"], 16),
    )
with sk4:
    smart_kpi(
        "Regiao Lider",
        top_reg_name,
        f"{top_reg_pct:.1f}% do total",
        accent=C["success"],
        icon_svg=icon("map_pin", C["success"], 16),
    )
with sk5:
    smart_kpi(
        "Alerta Mensal",
        alert_text,
        "crescimento MoM",
        accent=alert_color,
        icon_svg=icon("alert", alert_color, 16),
    )

spacer(14)

# =====================================================================
# PAGE 1 — VISÃO EXECUTIVA
# =====================================================================
if pagina == "Visao Executiva":

    page_header("Visao Executiva",
                f"Periodo: {data_ini.strftime('%d/%m/%y')} – {data_fim.strftime('%d/%m/%y')} · {dias_filtro} dias")

    # ---- KPI Cards ----
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Faturamento Total", fmt(fat_total),
                 delta_badge(fat_total, fat_prev),
                 icon_svg=icon("dollar", C["brand_l"], 14), accent=C["brand"])
    with c2:
        kpi_card("Total de Pedidos", fmt_int(ped_total),
                 delta_badge(ped_total, ped_prev),
                 icon_svg=icon("shopping", C["second_l"], 14), accent=C["second"])
    with c3:
        kpi_card("Ticket Medio", fmt(tkt_medio),
                 delta_badge(tkt_medio, tkt_prev),
                 icon_svg=icon("receipt", C["warn"], 14), accent=C["warn"])
    with c4:
        kpi_card("Vendedores Ativos", vend_total,
                 icon_svg=icon("users", C["success"], 14), accent=C["success"])

    spacer(10)

    # ---- Insights ----
    i1, i2, i3 = st.columns(3)
    for col, (txt, col_c) in zip([i1, i2, i3], all_insights):
        with col:
            insight_card(txt, col_c, icon_svg=icon("lightbulb", col_c, 13))

    spacer(12)

    # ---- Charts Row 1 ----
    cr, cl = st.columns(2)
    with cr:
        section_header("Faturamento por Estado")
        dfe = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(15)
        fig = bar_chart(dfe, "total_pedido", "estado", C["brand"], height=250)
        fig.update_traces(hovertemplate="<b>%{y}</b> — R$ %{x:,.0f}<extra></extra>",
                          marker_color=C["brand"], marker_opacity=0.8)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cl:
        section_header("Faturamento por Regiao")
        dfr = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True)
        fig = bar_chart(dfr, "total_pedido", "regiao", C["second"], height=250)
        fig.update_traces(hovertemplate="<b>%{y}</b> — R$ %{x:,.0f}<extra></extra>",
                          marker_color=C["second"], marker_opacity=0.8)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- Charts Row 2 ----
    c1, c2 = st.columns(2)
    with c1:
        section_header("Ranking de Vendedores")
        rank = (dv_merged.groupby(["nome", "regiao_d"], as_index=False)["total_pedido"]
                .sum().sort_values("total_pedido", ascending=False))
        rank.insert(0, "#", range(1, len(rank)+1))
        rank["Faturamento"] = rank["total_pedido"].apply(fmt)
        rank["%"] = (rank["total_pedido"] / rank["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            rank[["#", "nome", "regiao_d", "Faturamento", "%"]].rename(
                columns={"nome": "Vendedor", "regiao_d": "Regiao"}),
            use_container_width=True, hide_index=True, height=280
        )

    with c2:
        section_header("Top 5 e Bottom 5 Municipios")
        dm = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido")
        bottom5 = dm.head(5).copy(); bottom5["Tipo"] = "Bottom"
        top5 = dm.tail(5).sort_values("total_pedido", ascending=False).copy(); top5["Tipo"] = "Top"
        tb = pd.concat([top5, bottom5], ignore_index=True)
        tb["Faturamento"] = tb["total_pedido"].apply(fmt)
        st.dataframe(
            tb[["Tipo", "municipio", "Faturamento"]].rename(columns={"municipio": "Municipio"}),
            use_container_width=True, hide_index=True, height=280
        )

    # ---- Evolucao Mensal ----
    section_header("Evolucao Mensal do Faturamento")
    fe = ff.copy()
    fe["dt"] = pd.to_datetime(fe["data_pedido"])
    fe["ano_mes"] = fe["dt"].dt.to_period("M").astype(str)
    dmes = fe.groupby("ano_mes", as_index=False).agg(
        total=("total_pedido","sum"), min_dt=("dt","min")
    ).sort_values("ano_mes")
    dmes["label"] = dmes["min_dt"].dt.strftime("%b/%y")

    fig = go.Figure()
    # Gradient area fill
    fig.add_trace(go.Scatter(
        x=dmes["label"], y=dmes["total"],
        mode="lines",
        line=dict(color=C["brand"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.07)",
        showlegend=False,
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    # Dot markers on top
    fig.add_trace(go.Scatter(
        x=dmes["label"], y=dmes["total"],
        mode="markers",
        marker=dict(size=5, color=C["brand_l"], line=dict(width=1.5, color=C["brand"])),
        showlegend=False,
        hoverinfo="skip",
    ))
    chart_config(fig, height=200)
    fig.update_xaxes(tickangle=-30, tickfont_size=8, tickfont_color=C["text_muted"])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# PAGE 2 — VENDEDORES
# =====================================================================
elif pagina == "Vendedores":

    page_header("Desempenho de Vendedores",
                f"{vend_total} vendedores no periodo selecionado")

    dvf = (dv_merged.groupby(["id_vendedor", "nome", "regiao_d"], as_index=False)["total_pedido"]
           .sum().sort_values("total_pedido", ascending=False))
    dvf["rank"] = range(1, len(dvf)+1)
    top1 = dvf.iloc[0] if len(dvf) > 0 else None
    fat_med = fat_total / vend_total if vend_total > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        val_top = fmt(top1["total_pedido"]) if top1 is not None else ""
        kpi_card("Melhor Vendedor",
                 top1["nome"].split()[0] if top1 is not None else "-",
                 f'<span style="font-size:0.72rem;color:{C["text_muted"]};">{val_top}</span>',
                 icon_svg=icon("award", C["brand_l"], 14), accent=C["brand"])
    with c2:
        kpi_card("Fat. Medio / Vendedor", fmt(fat_med),
                 icon_svg=icon("dollar", C["second_l"], 14), accent=C["second"])
    with c3:
        kpi_card("Total Faturado", fmt(fat_total),
                 icon_svg=icon("trending_up", C["warn"], 14), accent=C["warn"])

    spacer(10)

    # ---- Ranking table + donut ----
    t_col, d_col = st.columns([1.2, 1])
    with t_col:
        section_header("Ranking Completo")
        rank_d = dvf.copy()
        rank_d["Faturamento"] = rank_d["total_pedido"].apply(fmt)
        rank_d["%"] = (rank_d["total_pedido"] / rank_d["total_pedido"].sum() * 100).apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            rank_d[["rank","nome","regiao_d","Faturamento","%"]].rename(
                columns={"rank":"#","nome":"Vendedor","regiao_d":"Regiao"}),
            use_container_width=True, hide_index=True, height=400
        )

    with d_col:
        section_header("Participacao %")
        palette = [C["brand"], C["brand_l"], C["second"], C["second_l"], C["warn"],
                   C["success"], "#F472B6", "#34D399", "#60A5FA", "#FBBF24",
                   "#A78BFA", "#6EE7B7", "#93C5FD", "#FCD34D", "#C084FC"]
        fig = go.Figure(go.Pie(
            labels=dvf["nome"], values=dvf["total_pedido"], hole=0.62,
            textinfo="none",
            marker=dict(colors=palette[:len(dvf)], line=dict(width=1.5, color=C["bg"])),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        # Center annotation
        fig.add_annotation(
            text=f"<b>{vend_total}</b><br><span style='font-size:9px'>vendedores</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=C["text"]),
            xref="paper", yref="paper"
        )
        chart_config(fig, height=320, showlegend=True)
        fig.update_layout(
            legend=dict(
                orientation="v", x=1.02, y=0.5, xanchor="left",
                font=dict(size=8, color=C["text_sec"]),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                itemsizing="constant",
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    spacer(8)
    # ---- Stacked by region ----
    section_header("Faturamento por Regiao do Vendedor")
    dv_stacked = dvf.groupby(["regiao_d", "nome"], as_index=False)["total_pedido"].sum()
    fig = px.bar(
        dv_stacked, x="total_pedido", y="regiao_d", color="nome", orientation="h",
        color_discrete_sequence=palette,
        labels={"total_pedido": "", "regiao_d": ""},
    )
    chart_config(fig, height=220, showlegend=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.18,
                    font=dict(size=8), title_text="", bgcolor="rgba(0,0,0,0)")
    )
    fig.update_traces(hovertemplate="<b>%{y}</b> · %{x:,.0f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# PAGE 3 — PRODUTOS
# =====================================================================
elif pagina == "Produtos":

    fc = ff.merge(dim_prod, on="id_produto", how="left")
    n_cats = dim_prod["categoria"].nunique()
    preco_medio = dim_prod["preco_venda"].mean()
    n_prods = ff["id_produto"].nunique()

    page_header("Analise de Produtos",
                f"{n_prods} produtos vendidos · {n_cats} categorias")

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Categorias Ativas", n_cats,
                 icon_svg=icon("tag", C["brand_l"], 14), accent=C["brand"])
    with c2:
        kpi_card("Preco Medio do Catalogo", fmt(preco_medio),
                 icon_svg=icon("box", C["second_l"], 14), accent=C["second"])
    with c3:
        kpi_card("Produtos Distintos Vendidos", fmt_int(n_prods),
                 icon_svg=icon("shopping", C["warn"], 14), accent=C["warn"])

    spacer(10)

    cc, cp = st.columns(2)
    with cc:
        section_header("Faturamento por Categoria")
        dc = fc.groupby("categoria", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True)
        # Color scale from muted to brand
        colors = [C["brand"]] * len(dc)
        fig = go.Figure(go.Bar(
            y=dc["categoria"], x=dc["total_pedido"], orientation="h",
            marker=dict(
                color=dc["total_pedido"],
                colorscale=[[0, "#2D1B69"], [1, C["brand"]]],
                showscale=False,
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        ))
        chart_config(fig, height=260)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cp:
        section_header("Top 10 Produtos por Faturamento")
        dpt = (fc.groupby("nome_produto", as_index=False)["total_pedido"]
               .sum().sort_values("total_pedido", ascending=True).tail(10))
        fig = go.Figure(go.Bar(
            y=dpt["nome_produto"], x=dpt["total_pedido"], orientation="h",
            marker=dict(
                color=dpt["total_pedido"],
                colorscale=[[0, "#0C3854"], [1, C["second"]]],
                showscale=False,
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        ))
        chart_config(fig, height=260)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    spacer(8)
    section_header("Detalhamento por Categoria")
    dd = fc.groupby("categoria").agg(
        Faturamento=("total_pedido","sum"),
        Pedidos=("pedido_id","nunique"),
        Ticket=("total_pedido","mean"),
        Quantidade=("quantidade","sum")
    ).reset_index().sort_values("Faturamento", ascending=False)
    dd["Fat."] = dd["Faturamento"].apply(fmt)
    dd["Ticket Medio"] = dd["Ticket"].apply(fmt)
    dd["%"] = (dd["Faturamento"] / dd["Faturamento"].sum() * 100).apply(lambda x: f"{x:.1f}%")
    st.dataframe(
        dd[["categoria","Fat.","%","Pedidos","Ticket Medio","Quantidade"]].rename(
            columns={"categoria":"Categoria"}),
        use_container_width=True, hide_index=True, height=260
    )

# =====================================================================
# PAGE 4 — GEOGRÁFICA
# =====================================================================
elif pagina == "Geografica":

    page_header("Distribuicao Geografica",
                "Faturamento por estado, regiao e municipio")

    # Summary KPIs
    n_estados = ff["estado"].nunique()
    n_munic   = ff["municipio"].nunique()
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Regiao Lider", top_reg_name,
                 f'<span style="font-size:0.72rem;color:{C["text_muted"]};">{top_reg_pct:.1f}% do faturamento</span>',
                 icon_svg=icon("map_pin", C["brand_l"], 14), accent=C["brand"])
    with c2:
        kpi_card("Estados Ativos", n_estados,
                 icon_svg=icon("globe", C["second_l"], 14), accent=C["second"])
    with c3:
        kpi_card("Municipios Ativos", fmt_int(n_munic),
                 icon_svg=icon("map_pin", C["warn"], 14), accent=C["warn"])

    spacer(10)

    # Estado + Regiao side by side
    ce, cr = st.columns([1.6, 1])
    with ce:
        section_header("Faturamento por Estado")
        dfe2 = ff.groupby("estado", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True)
        fig = go.Figure(go.Bar(
            y=dfe2["estado"], x=dfe2["total_pedido"], orientation="h",
            marker=dict(
                color=dfe2["total_pedido"],
                colorscale=[[0,"#2D1B69"],[1, C["brand"]]],
                showscale=False, line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        ))
        chart_config(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cr:
        section_header("Faturamento por Regiao")
        dfr2 = ff.groupby("regiao", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=False)
        fig = go.Figure(go.Pie(
            labels=dfr2["regiao"], values=dfr2["total_pedido"], hole=0.55,
            textinfo="percent+label",
            textfont=dict(size=9, color=C["text"]),
            marker=dict(
                colors=[C["brand"], C["second"], C["warn"], C["success"], C["brand_l"]],
                line=dict(width=1.5, color=C["bg"])
            ),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        chart_config(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Top municipios
    section_header("Top 15 Municipios")
    dm2 = ff.groupby("municipio", as_index=False)["total_pedido"].sum().sort_values("total_pedido", ascending=True).tail(15)
    fig = go.Figure(go.Bar(
        y=dm2["municipio"], x=dm2["total_pedido"], orientation="h",
        marker=dict(
            color=dm2["total_pedido"],
            colorscale=[[0,"#0C3854"],[1, C["second"]]],
            showscale=False, line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    chart_config(fig, height=310)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# =====================================================================
# FOOTER
# =====================================================================
st.markdown('</div>', unsafe_allow_html=True)  # fecha nexus-main
st.markdown(f"""
<div style="border-top:1px solid {C['border']};padding:10px 28px;
     display:flex;align-items:center;justify-content:space-between;
     background:{C['bg']};">
    <span style="font-size:0.62rem;color:{C['text_muted']};">
        Nexus BI · Dados 2025–2026 · {fmt(fat_total)} · {fmt_int(ped_total)} pedidos · {vend_total} vendedores
    </span>
    <a href="https://github.com/Nagalli01/bi-ecommerce-dashboard"
       style="font-size:0.62rem;color:{C['text_muted']};text-decoration:none;
              opacity:.6;">GitHub</a>
</div>
""", unsafe_allow_html=True)
