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


def fmt(x, nd=2):
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
# LÓGICA DO ÍNDICE DE INTERFERÊNCIA
# ============================================================
def calcular_interferencia(W, I, S, C, V):
    """
    Índice de Interferência (0 a 1)
    Baseado em interações reais observadas em Puerto Williams.
    """
    inter1 = I * W * 1.0      # Invasoras × Água
    inter2 = W * C * 0.8      # Água × Clima
    inter3 = I * V * 0.9      # Invasoras × Vegetação (muito forte na região)
    inter4 = S * W * 0.5      # Sísmico × Água
    inter5 = C * V * 0.7      # Clima × Vegetação
    inter6 = I * S * 0.4      # Invasoras × Sísmico (interação secundária)

    ii_bruto = inter1 + inter2 + inter3 + inter4 + inter5 + inter6
    ii_final = 1 - np.exp(-ii_bruto)
    return round(float(ii_final), 3)


# ============================================================
# DADOS REALISTAS BASEADOS NOS PROJETOS DO PORTFÓLIO
# ============================================================
# Fontes:
# - Água: patagonia-water-quality (WQI Beagle Channel = 97)
# - Invasoras: invasive-alien-species-impact (castores + campo 2025)
# - Sísmico: patagonia-seismic (M7.4 maio/2025 + falha Magallanes-Fagnano)
# - Vegetação: impacto dos castores (NDVI + observação de campo)
# - Clima: condições subantárticas da região

zonas = [
    {
        "nome": "Zona Norte - Canal Beagle",
        "lat": -54.910, "lon": -67.580,
        "W": 0.12,   # Água excelente (próximo da estação WQI 97)
        "I": 0.78,   # Presença significativa de castores
        "S": 0.75,   # Alta exposição sísmica
        "C": 0.58,
        "V": 0.70
    },
    {
        "nome": "Zona Centro - Puerto Williams",
        "lat": -54.933, "lon": -67.617,
        "W": 0.08,   # Melhor qualidade de água (WQI 97)
        "I": 0.85,   # Castoreiras documentadas perto do centro
        "S": 0.82,   # Diretamente sobre a falha + vivência do M7.4
        "C": 0.60,
        "V": 0.72
    },
    {
        "nome": "Zona Sul - Interior Navarino",
        "lat": -54.960, "lon": -67.650,
        "W": 0.18,
        "I": 0.91,   # Maior densidade de impacto de castores
        "S": 0.70,
        "C": 0.55,
        "V": 0.85    # Forte degradação florestal
    },
    {
        "nome": "Zona Leste - Laguna Rosa / Área Úmida",
        "lat": -54.925, "lon": -67.550,
        "W": 0.22,
        "I": 0.88,   # Castoreira 2 documentada (Laguna Rosa)
        "S": 0.68,
        "C": 0.62,
        "V": 0.80
    },
    {
        "nome": "Zona Oeste - Interior",
        "lat": -54.940, "lon": -67.700,
        "W": 0.15,
        "I": 0.72,
        "S": 0.73,
        "C": 0.52,
        "V": 0.65
    },
]

# Calcula o II de cada zona
for z in zonas:
    z["II"] = calcular_interferencia(z["W"], z["I"], z["S"], z["C"], z["V"])

zonas_sorted = sorted(zonas, key=lambda x: x["II"], reverse=True)
indice_geral = round(np.mean([z["II"] for z in zonas]), 3)
zonas_criticas = sum(1 for z in zonas if z["II"] >= 0.60)

# ============================================================
# ESTILOS
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
  font-size: 2.5rem;
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
  font-size: 1.8rem;
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
    st.markdown(f'<div class="metric-box"><div class="metric-val">{fmt(indice_geral)}</div><div class="metric-label">{T["m1"]}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box green"><div class="metric-val">5</div><div class="metric-label">{T["m2"]}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box sky"><div class="metric-val">{zonas_criticas}</div><div class="metric-label">{T["m3"]}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-box night"><div class="metric-val">{T["m4_value"]}</div><div class="metric-label">{T["m4"]}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# ABAS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5"]])

# --- TAB 1: MAPA + TABELA ---
with tab1:
    st.markdown(f'<div class="section-label">{T["map_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["map_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">{T["map_hint"]}</div>', unsafe_allow_html=True)

    m = folium.Map(location=[-54.933, -67.617], zoom_start=11, tiles="CartoDB positron")

    for z in zonas:
        cor = "#E11D48" if z["II"] >= 0.70 else "#F97316" if z["II"] >= 0.55 else "#22C55E"
        folium.Circle(
            location=[z["lat"], z["lon"]],
            radius=900 + (z["II"] * 900),
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.35,
            popup=f"<b>{z['nome']}</b><br>Índice de Interferência: {z['II']}"
        ).add_to(m)

    folium.Marker(
        [-54.933, -67.617],
        popup="<b>Puerto Williams</b><br>Centro de análise PULSE",
        tooltip="Puerto Williams",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    folium_static(m, width=1100, height=420)

    st.markdown("### Índice de Interferência por Zona")
    st.caption("Valores derivados dos projetos: patagonia-water-quality · invasive-alien-species-impact · patagonia-seismic")

    df = pd.DataFrame([
        {
            "Zona": z["nome"],
            "Água (W)": z["W"],
            "Invasoras (I)": z["I"],
            "Sísmico (S)": z["S"],
            "Clima (C)": z["C"],
            "Vegetação (V)": z["V"],
            "Índice II": z["II"]
        } for z in zonas_sorted
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info("**Leitura:** Mesmo com água de excelente qualidade (W baixo), a combinação de alta pressão de castores + risco sísmico elevado gera interferência significativa, especialmente nas zonas Sul e Leste.")

# --- TAB 2: RADAR ---
with tab2:
    st.markdown(f'<div class="section-label">{T["radar_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["radar_title"]}</div>', unsafe_allow_html=True)

    media_W = np.mean([z["W"] for z in zonas])
    media_I = np.mean([z["I"] for z in zonas])
    media_S = np.mean([z["S"] for z in zonas])
    media_C = np.mean([z["C"] for z in zonas])
    media_V = np.mean([z["V"] for z in zonas])

    if LANG == "en":
        categories = ["Water Quality", "Invasive Species", "Seismicity", "Climate Stress", "Vegetation"]
    elif LANG == "es":
        categories = ["Calidad del Agua", "Especies Invasoras", "Sismicidad", "Estrés Climático", "Vegetación"]
    else:
        categories = ["Qualidade da Água", "Espécies Invasoras", "Sismicidade", "Estresse Climático", "Vegetação"]

    values = [media_W, media_I, media_S, media_C, media_V]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(225, 29, 72, 0.25)",
        line=dict(color="#E11D48", width=2),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    plot(fig)

    st.info(f"Médias do território: Água={fmt(media_W)} | Invasoras={fmt(media_I)} | Sísmico={fmt(media_S)} | Clima={fmt(media_C)} | Vegetação={fmt(media_V)}")

# --- TAB 3: EVOLUÇÃO ---
with tab3:
    st.markdown(f'<div class="section-label">{T["timeline_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["timeline_title"]}</div>', unsafe_allow_html=True)

    years = list(range(2015, 2026))
    # Tendência crescente realista (invasoras avançando + risco sísmico constante)
    base = 0.48
    interference = [round(base + (i * 0.018), 3) for i in range(11)]
    interference[-1] = indice_geral

    fig_line = px.line(x=years, y=interference, markers=True,
                       labels={"x": "Ano" if LANG != "en" else "Year", "y": T["m1"]})
    fig_line.update_traces(line_color="#E11D48", line_width=3)
    fig_line.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    plot(fig_line)

    st.caption("Tendência ilustrativa baseada no avanço documentado dos castores e na permanência do risco sísmico na região.")

# --- TAB 4: PONTOS CRÍTICOS ---
with tab4:
    st.markdown(f'<div class="section-label">{T["critical_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["critical_title"]}</div>', unsafe_allow_html=True)

    for z in zonas_sorted[:3]:
        if z["II"] >= 0.70:
            st.error(f"**{z['nome']}** — Índice II = **{z['II']}**\n\n"
                     f"- Invasoras: {z['I']} | Vegetação: {z['V']} | Sísmico: {z['S']}\n"
                     f"- Principal motor: **Invasoras × Vegetação** + risco sísmico elevado")
        elif z["II"] >= 0.55:
            st.warning(f"**{z['nome']}** — Índice II = **{z['II']}**\n\n"
                       f"- Invasoras: {z['I']} | Água: {z['W']} | Sísmico: {z['S']}\n"
                       f"- Monitoramento prioritário recomendado")
        else:
            st.info(f"**{z['nome']}** — Índice II = **{z['II']}**\n\n"
                    f"- Situação relativamente mais estável")

# --- TAB 5: SOBRE ---
with tab5:
    st.markdown(f'<div class="section-label">{T["about_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["about_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">{T["about_text"]}</div>', unsafe_allow_html=True)

    st.markdown("### Fontes dos valores utilizados")
    st.markdown("""
- **Qualidade da Água** → projeto `patagonia-water-quality` (WQI Beagle Channel = 97)
- **Espécies Invasoras** → projeto `invasive-alien-species-impact` (campo 2025 + literatura)
- **Sismicidade** → projeto `patagonia-seismic` (M7.4 maio/2025 + falha Magallanes-Fagnano)
- **Vegetação** → impacto documentado dos castores (NDVI + observação de campo)
""")

    st.markdown("### Fórmula")
    st.code("""
II = 1 - exp( -(I×W×1.0 + W×C×0.8 + I×V×0.9 + S×W×0.5 + C×V×0.7 + I×S×0.4) )
""", language="text")

# ============================================================
# RODAPÉ
# ============================================================
st.markdown(f"""
<div class="footer-wrap">
  <div class="footer-title">{T['footer_title']}</div>
  <div>{T['footer_copy']}</div>
</div>
""", unsafe_allow_html=True)
