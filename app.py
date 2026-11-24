import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime

from translations import TRANSLATIONS

st.set_page_config(
    page_title="PULSE · Patagonian Interference Engine",
    page_icon="🫀",
    layout="wide"
)

# ============================================================
# IDIOMAS
# ============================================================
LANGS = [
    ("pt", "🇧🇷", "PT"), ("en", "🇺🇸", "EN"), ("es", "🇪🇸", "ES"),
]
CODES = [c for c, _, _ in LANGS]
FLAGS = {c: f"{flag} {label}" for c, flag, label in LANGS}

DECIMAL = {"pt": ",", "en": ".", "es": ","}
THOUSANDS = {"pt": ".", "en": ",", "es": "."}
PLOTLY_SEP = {"pt": ",.", "en": ".,", "es": ",."}


def _initial_lang():
    q = st.query_params.get("lang")
    if isinstance(q, list):
        q = q[0] if q else None
    return q if q in CODES else "pt"


if "lang" not in st.session_state:
    st.session_state.lang = _initial_lang()


def render_lang_selector():
    try:
        escolha = st.pills(
            "Language", CODES, selection_mode="single",
            default=st.session_state.lang, format_func=lambda c: FLAGS[c],
            key="lang_pick", label_visibility="collapsed",
        )
    except AttributeError:
        escolha = st.radio(
            "Language", CODES, index=CODES.index(st.session_state.lang),
            format_func=lambda c: FLAGS[c], horizontal=True,
            key="lang_pick", label_visibility="collapsed",
        )
    if escolha and escolha != st.session_state.lang:
        st.session_state.lang = escolha
        st.query_params["lang"] = escolha
        st.rerun()


render_lang_selector()
LANG = st.session_state.lang
T = TRANSLATIONS[LANG]


def fmt(x, nd=1):
    return f"{x:.{nd}f}".replace(".", DECIMAL[LANG])


def fmt_int(x):
    return f"{int(round(x)):,}".replace(",", THOUSANDS[LANG])


def plot(fig):
    fig.update_layout(separators=PLOTLY_SEP[LANG])
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ESTILOS (adaptados para identidade PULSE)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&family=DM+Mono&display=swap');

:root{
  --pulse:#E11D48;
  --pulse-dark:#BE123C;
  --night:#0D1A2E;
  --night-mid:#142238;
  --cream:#FDFAF4;
  --warm-gray:#8A7B6B;
  --green:#2D7A3A;
  --sky:#2C8FD9;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--cream);
  color: #0D1117;
}

.hero-wrap{
  background: linear-gradient(135deg, var(--night) 0%, var(--night-mid) 55%, #1E3560 100%);
  border-radius: 20px;
  padding: 3rem 2.5rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.hero-wrap::before{
  content: "🫀";
  font-size: 180px;
  position: absolute;
  right: -10px;
  top: -20px;
  opacity: 0.07;
}
.hero-tag{
  background: var(--pulse);
  color: white;
  font-family: 'DM Mono', monospace;
  font-size: 0.7rem;
  font-weight: bold;
  letter-spacing: 2px;
  padding: 4px 12px;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 1rem;
  text-transform: uppercase;
}
.hero-title{
  font-family: 'Playfair Display', serif;
  font-size: 2.6rem;
  font-weight: 900;
  color: #fff;
  line-height: 1.15;
  margin-bottom: 0.8rem;
  white-space: pre-line;
}
.hero-subtitle{
  font-size: 1rem;
  color: rgba(255,255,255,0.75);
  max-width: 680px;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}
.hero-badges{display:flex; gap:10px; flex-wrap:wrap;}
.badge{
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.85);
  font-size: 0.72rem;
  font-family: 'DM Mono', monospace;
  padding: 5px 12px;
  border-radius: 20px;
}
.badge-pulse{
  background: rgba(225,29,72,0.25);
  border-color: var(--pulse);
  color: #FDA4AF;
}

.metric-box{
  background: white;
  border-radius: 16px;
  padding: 1.4rem 1.2rem;
  border-top: 4px solid var(--pulse);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  text-align: center;
}
.metric-box.green{border-top-color: var(--green);}
.metric-box.sky{border-top-color: var(--sky);}
.metric-box.night{border-top-color: #1A3050;}
.metric-val{
  font-family: 'Playfair Display', serif;
  font-size: 2.1rem;
  font-weight: 900;
  color: var(--night);
  line-height: 1;
  margin-bottom: 0.3rem;
}
.metric-label{
  font-size: 0.75rem;
  color: var(--warm-gray);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.section-label{
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  color: var(--pulse-dark);
  text-transform: uppercase;
  letter-spacing: 3px;
  margin-bottom: 0.3rem;
}
.section-title{
  font-family: 'Playfair Display', serif;
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--night);
  margin-bottom: 1.2rem;
}

.info-card{
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border-left: 4px solid var(--pulse);
  margin-bottom: 1rem;
}

.footer-wrap{
  background: var(--night);
  border-radius: 20px;
  padding: 2rem;
  color: rgba(255,255,255,0.8);
  text-align: center;
  margin-top: 3rem;
}
.footer-title{
  font-family: 'Playfair Display', serif;
  color: var(--pulse);
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-tag">{T['hero_tag']}</div>
  <div class="hero-title">{T['hero_title']}</div>
  <div class="hero-subtitle">{T['hero_subtitle']}</div>
  <div class="hero-badges">
    <span class="badge badge-pulse">{T['badge1']}</span>
    <span class="badge badge-pulse">{T['badge2']}</span>
    <span class="badge">{T['badge3']}</span>
    <span class="badge">{T['badge4']}</span>
    <span class="badge">{T['badge5']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Métricas
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-val">0.68</div><div class="metric-label">{T["m1"]}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box green"><div class="metric-val">4</div><div class="metric-label">{T["m2"]}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box sky"><div class="metric-val">3</div><div class="metric-label">{T["m3"]}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-box night"><div class="metric-val">{T["m4_value"]}</div><div class="metric-label">{T["m4"]}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# ABAS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5"]])

# --- TAB 1: MAPA ---
with tab1:
    st.markdown(f'<div class="section-label">{T["map_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["map_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">{T["map_hint"]}</div>', unsafe_allow_html=True)

    m = folium.Map(location=[-54.9333, -67.6167], zoom_start=11, tiles="CartoDB positron")

    folium.Marker(
        [-54.9333, -67.6167],
        popup="<b>Puerto Williams</b><br>Centro de análise PULSE",
        tooltip="Puerto Williams",
        icon=folium.Icon(color="red", icon="heart", prefix="fa")
    ).add_to(m)

    # Zonas de interferência (placeholders)
    folium.Circle(location=[-54.92, -67.60], radius=1800, color="#E11D48", fill=True,
                  fill_color="#E11D48", fill_opacity=0.35, popup="Alta Interferência").add_to(m)
    folium.Circle(location=[-54.95, -67.65], radius=1200, color="#F97316", fill=True,
                  fill_color="#F97316", fill_opacity=0.30, popup="Interferência Moderada").add_to(m)

    folium_static(m, width=1100, height=500)

# --- TAB 2: RADAR ---
with tab2:
    st.markdown(f'<div class="section-label">{T["radar_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["radar_title"]}</div>', unsafe_allow_html=True)

    categories = ["Qualidade da Água", "Espécies Invasoras", "Sismicidade", "Estresse Climático", "Cobertura Vegetal"]
    if LANG == "en":
        categories = ["Water Quality", "Invasive Species", "Seismicity", "Climate Stress", "Vegetation Cover"]
    elif LANG == "es":
        categories = ["Calidad del Agua", "Especies Invasoras", "Sismicidad", "Estrés Climático", "Cobertura Vegetal"]

    values = [0.71, 0.84, 0.48, 0.63, 0.57]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(225, 29, 72, 0.25)",
        line=dict(color="#E11D48", width=2),
        name="Pressão"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    plot(fig)

# --- TAB 3: EVOLUÇÃO ---
with tab3:
    st.markdown(f'<div class="section-label">{T["timeline_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["timeline_title"]}</div>', unsafe_allow_html=True)

    years = list(range(2015, 2026))
    interference = [0.42, 0.45, 0.48, 0.53, 0.58, 0.61, 0.64, 0.66, 0.67, 0.68, 0.69]

    fig_line = px.line(x=years, y=interference, markers=True,
                       labels={"x": "Ano" if LANG == "pt" else "Year", "y": T["m1"]})
    fig_line.update_traces(line_color="#E11D48", line_width=3)
    fig_line.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    plot(fig_line)

# --- TAB 4: PONTOS CRÍTICOS ---
with tab4:
    st.markdown(f'<div class="section-label">{T["critical_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["critical_title"]}</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.error("**Zona 1 — Alta Interferência**\n\n- Alta densidade de castores\n- Tendência de degradação da água\n- Proximidade de áreas sensíveis")
    with col_b:
        st.warning("**Zona 2 — Interferência Moderada**\n\n- Sobreposição hidrológica + clima\n- Exposição sísmica moderada\n- Monitoramento recomendado")
    with col_c:
        st.info("**Zona 3 — Atenção**\n\n- Mudança de cobertura vegetal\n- Possível interação com invasoras\n- Requer dados adicionais")

# --- TAB 5: SOBRE ---
with tab5:
    st.markdown(f'<div class="section-label">{T["about_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["about_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">{T["about_text"]}</div>', unsafe_allow_html=True)

# ============================================================
# RODAPÉ
# ============================================================
st.markdown(f"""
<div class="footer-wrap">
  <div class="footer-title">{T['footer_title']}</div>
  <div>{T['footer_copy']}</div>
</div>
""", unsafe_allow_html=True)
