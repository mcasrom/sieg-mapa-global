"""
SIEG — Mapa Geopolítico Global
Con el Odroid en la Mochila · mcasrom
Capas: Conflictos, Petróleo, Cables submarinos, Elecciones, Nuclear, Migración
"""

import streamlit as st
import folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SIEG · Mapa Geopolítico Global",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono&display=swap');
  .main { background: #0a0c10; }
  .block-container { padding-top: 1rem; }
  h1, h2, h3 { font-family: 'Space Mono', monospace; }
  .metric-card {
    background: #111318;
    border: 1px solid #1e2230;
    border-left: 3px solid;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
  }
  .stSidebar { background: #0d0f14; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATOS — Curados manualmente, actualiza según evolución
# Formato: [lat, lon, nombre, detalle, intensidad(1-3)]
# ─────────────────────────────────────────────

CONFLICTOS = [
    [48.0, 37.0,   "Guerra Ucrania-Rusia",         "Conflicto activo. Frente Donbás/Zaporiyia.", 3],
    [15.5, 32.5,   "Sudan — Guerra Civil",          "SAF vs RSF. Crisis humanitaria severa.", 3],
    [31.5, 34.5,   "Gaza — Conflicto Israel-Hamas", "Operaciones militares activas.", 3],
    [33.5, 43.5,   "Iraq — Inestabilidad",          "Ataques milicias pro-Irán. Tensión EEUU.", 2],
    [15.0, 42.5,   "Yemen — Guerra Civil",          "Houthis vs coalición. Bloqueo Mar Rojo.", 3],
    [5.5,  -4.0,   "Sahel — Insurgencia yihadista", "Mali, Burkina, Niger. Golpes militares.", 2],
    [7.0,  21.0,   "RCA — Conflicto armado",        "Grupos armados vs gobierno.", 2],
    [35.0, 38.5,   "Siria — Conflicto residual",    "Focos activos norte y este.", 2],
    [1.5,  38.0,   "Somalia — Al-Shabaab",          "Ataques continuos en sur y centro.", 2],
    [27.0, 85.0,   "Myanmar — Guerra Civil",        "Junta militar vs resistencia.", 3],
    [-1.5, 29.5,   "Este Congo (DRC)",              "M23 y grupos armados. Crisis humanitaria.", 3],
    [13.5, 14.5,   "Lago Chad — Boko Haram",        "Ataques transfronterizos.", 2],
]

PETROLEO = [
    [26.0,  50.5,  "Arabia Saudí — Ghawar",        "Mayor campo petrolífero del mundo. 8Mb/d.", 3],
    [29.0,  48.0,  "Kuwait — Gran Burgan",          "Segundo campo más grande. 1.7Mb/d.", 3],
    [25.0,  55.0,  "UAE — Abu Dhabi",               "ADNOC. 4Mb/d. Reservas 100Gb.", 3],
    [31.0,  47.5,  "Iraq — Rumaila",                "3Mb/d. Inestabilidad política.", 2],
    [32.0,  53.0,  "Irán — Ahvaz",                  "Sanciones activas. 3.5Mb/d.", 3],
    [27.0,  13.0,  "Libia — Sirte Basin",           "Inestabilidad. 1.2Mb/d intermitente.", 2],
    [56.0,  60.0,  "Rusia — Siberia Occidental",   "Yugansk. Sanciones UE/EEUU.", 3],
    [10.0, -84.0,  "Venezuela — Orinoco Belt",      "Producción mermada. 0.8Mb/d.", 2],
    [57.0,   3.0,  "Mar del Norte",                 "Noruega+UK. 3Mb/d. Declive.", 2],
    [27.5, -15.0,  "Estrecho de Hormuz",            "40% tráfico mundial. Tensión Irán.", 3],
    [11.5, -15.5,  "Golfo de Guinea",               "Nigeria+Angola. 4Mb/d.", 2],
    [-8.0,  13.5,  "Angola — Cabinda",              "TotalEnergies. 1.1Mb/d.", 2],
]

CABLES = [
    [36.0,  -5.5,  "SEA-ME-WE 3",        "SE Asia-Oriente Medio-Europa Occidental.", 2],
    [25.0,  55.0,  "FLAG/FALCON",         "Europa-Asia. Pasa por Golfo Pérsico.", 2],
    [51.5,  -1.5,  "TAT-14",             "Atlántico Norte. EEUU-Europa.", 2],
    [35.5,  23.0,  "Med Cable System",   "Mediterráneo. Europa-Norte África.", 2],
    [-6.0,  15.0,  "SACS",              "SAmerica-Africa Cable System.", 1],
    [1.3,  104.0,  "Asia-America GW",    "Pacífico. EEUU-Asia.", 2],
    [63.0, -21.0,  "AEConnect-1",        "Atlántico Norte. Irlanda-EEUU.", 1],
    [14.5,  43.0,  "Mar Rojo — Riesgo",  "Houthis. Cortes reportados 2024.", 3],
    [22.0, 114.0,  "APG Cable",         "Asia-Pacific Gateway. 10Tbps.", 2],
    [-34.0, 18.5,  "SAFE Cable",        "SAfrica-Europa. Ruta alternativa.", 1],
    [31.0,  32.0,  "Canal Suez — Nodo", "Concentración crítica de cables.", 3],
]

ELECCIONES = [
    [38.0,  -3.5,  "España — Municipales 2027",     "Próximas elecciones locales. Alta volatilidad.", 2],
    [46.0,   2.0,  "Francia — Legislativas",         "Escenario fragmentado. RN en alza.", 2],
    [51.5,  10.0,  "Alemania — Bundestag 2025",      "CDU+AfD escenario complejo.", 2],
    [55.7,  37.6,  "Rusia — Elecciones regionales",  "Sin competencia real.", 1],
    [39.9, 116.4,  "China — Congreso Nacional",      "Sin elecciones libres. Monitoreo.", 1],
    [20.0, -100.0, "México — Midterms 2026",         "Morena dominante.", 2],
    [28.6,  77.2,  "India — Elecciones estatales",   "BJP vs INDIA coalition.", 2],
    [36.8,  10.2,  "Túnez — Proceso político",       "Consolidación Saied.", 2],
    [-33.9, 18.4,  "Sudáfrica — Postelecciones",     "ANC sin mayoría. Gobierno coalición.", 2],
    [40.4, -3.7,   "España — Generales (potencial)", "Escenario anticipado si crisis gobierno.", 3],
    [41.0,  29.0,  "Turquía — Municipales",          "CHP ganó Estambul/Ankara 2024.", 2],
    [35.7, 139.7,  "Japón — Elecciones LDP",         "LDP pierde mayoría. Coalición inestable.", 2],
]

NUCLEAR = [
    [34.0,  53.0,  "Irán — Programa nuclear",       "Enriquecimiento 60-84%. AIEA preocupada.", 3],
    [33.6,  73.1,  "Pakistán — Arsenal nuclear",    "~165 ojivas. Tensión India.", 2],
    [28.6,  77.2,  "India — Modernización",         "~160 ojivas. Expansión capacidad.", 2],
    [37.5, 127.5,  "Corea del Norte — Misiles",     "Tests continuos ICBM. ~50 ojivas.", 3],
    [55.7,  37.6,  "Rusia — Doctrina nuclear",      "Retórica elevada. ~5889 ojivas.", 3],
    [38.9, -77.0,  "EEUU — Modernización",          "~5244 ojivas. AUKUS/NATO.", 2],
    [51.5,  -0.1,  "UK — Trident",                  "~225 ojivas. Incremento previsto.", 2],
    [48.8,   2.3,  "Francia — Force de Frappe",     "~290 ojivas. Autonomía estratégica.", 2],
    [31.8,  35.2,  "Israel — Ambigüedad nuclear",   "~90 ojivas estimadas. No confirmado.", 2],
    [36.0, 128.0,  "Corea del Sur — Debate",        "Presión interna por capacidad propia.", 1],
]

MIGRACION = [
    [35.9,  14.5,  "Malta — Ruta mediterránea central", "Principal punto entrada UE. 100k+/año.", 3],
    [37.9,  23.7,  "Grecia — Ruta egea",                "Llegadas desde Turquía. Lesbos.", 3],
    [36.1,  -5.4,  "España — Ceuta/Melilla",            "Ruta atlántica y terrestre.", 2],
    [37.0,  15.3,  "Sicilia — Lampedusa",               "Crisis 2023. 150k llegadas.", 3],
    [51.5,  10.7,  "Alemania — Mayor receptor UE",      "1M+ solicitudes anuales.", 2],
    [3.8,   42.0,  "Somalia-Etiopía — Desplazados",     "4M+ desplazados internos.", 3],
    [15.4,  32.6,  "Sudan — Éxodo masivo",              "8M+ desplazados. Crisis mayor 2024.", 3],
    [34.0,  36.0,  "Siria — Refugiados",                "6M+ fuera. Turquía 3.5M.", 3],
    [25.0,  57.0,  "Golfo Pérsico — Trabajadores",      "Kafala system. 20M migrantes laborales.", 2],
    [20.0, -17.0,  "Ruta atlántica — Canarias",         "Llegadas desde Senegal/Mauritania.", 2],
    [14.0,  -1.0,  "Sahel — Desplazamiento interno",    "Insurgencia. 2M+ desplazados.", 3],
    [31.5,  34.5,  "Gaza — Desplazados",                "1.9M desplazados internos.", 3],
]

# ─────────────────────────────────────────────
# COLORES Y ESTILOS
# ─────────────────────────────────────────────
LAYER_CONFIG = {
    "conflictos": {"color": "#ff4d6d", "icon": "fire",        "prefix": "fa", "label": "🔴 Conflictos activos"},
    "petroleo":   {"color": "#ffd60a", "icon": "tint",        "prefix": "fa", "label": "🟡 Geopolítica petróleo"},
    "cables":     {"color": "#00e5ff", "icon": "plug",        "prefix": "fa", "label": "🔵 Cables submarinos"},
    "elecciones": {"color": "#a0ff60", "icon": "flag",        "prefix": "fa", "label": "🟢 Elecciones"},
    "nuclear":    {"color": "#ff6b35", "icon": "warning-sign","prefix": "glyphicon", "label": "🟠 Tensiones nucleares"},
    "migracion":  {"color": "#c77dff", "icon": "user",        "prefix": "fa", "label": "🟣 Migración / fronteras"},
}

INTENSIDAD_RADIUS = {1: 8, 2: 12, 3: 18}
INTENSIDAD_LABEL  = {1: "Bajo", 2: "Medio", 3: "Alto"}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 SIEG · Mapa Global")
    st.markdown("*Con el Odroid en la Mochila*")
    st.divider()

    st.markdown("**Capas activas**")
    show_conflictos = st.toggle("🔴 Conflictos activos",   value=True)
    show_petroleo   = st.toggle("🟡 Petróleo / energía",   value=True)
    show_cables     = st.toggle("🔵 Cables submarinos",    value=False)
    show_elecciones = st.toggle("🟢 Elecciones",           value=True)
    show_nuclear    = st.toggle("🟠 Tensiones nucleares",  value=False)
    show_migracion  = st.toggle("🟣 Migración / fronteras",value=False)

    st.divider()
    st.markdown("**Estilo de mapa**")
    mapa_estilo = st.selectbox("Capa base", [
        "CartoDB dark_matter",
        "CartoDB positron",
        "OpenStreetMap",
        "Stamen Terrain",
    ])

    st.divider()
    st.markdown("**Filtro intensidad**")
    min_intensidad = st.slider("Mínimo nivel", 1, 3, 1)

    st.divider()
    st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y')}")
    st.caption("Datos curados — fuentes abiertas")
    st.caption("[SIEG Hub](https://sieg-dashboard.streamlit.app/)")

# ─────────────────────────────────────────────
# MÉTRICAS HEADER
# ─────────────────────────────────────────────
st.markdown("## 🌍 SIEG · Mapa Geopolítico Global")
st.markdown("*Inteligencia estratégica de fuentes abiertas — Con el Odroid en la Mochila*")

active_layers = sum([show_conflictos, show_petroleo, show_cables,
                     show_elecciones, show_nuclear, show_migracion])

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Conflictos", len([x for x in CONFLICTOS if x[4] >= min_intensidad]), "activos")
col2.metric("Petróleo",   len([x for x in PETROLEO   if x[4] >= min_intensidad]), "puntos")
col3.metric("Cables",     len([x for x in CABLES     if x[4] >= min_intensidad]), "nodos")
col4.metric("Elecciones", len([x for x in ELECCIONES if x[4] >= min_intensidad]), "procesos")
col5.metric("Nuclear",    len([x for x in NUCLEAR    if x[4] >= min_intensidad]), "actores")
col6.metric("Migración",  len([x for x in MIGRACION  if x[4] >= min_intensidad]), "rutas")

st.divider()

# ─────────────────────────────────────────────
# MAPA
# ─────────────────────────────────────────────
tile_map = {
    "CartoDB dark_matter": "CartoDB dark_matter",
    "CartoDB positron":    "CartoDB positron",
    "OpenStreetMap":       "OpenStreetMap",
    "Stamen Terrain":      "Stamen Terrain",
}

m = folium.Map(
    location=[20, 10],
    zoom_start=3,
    tiles=tile_map[mapa_estilo],
    prefer_canvas=True,
)

Fullscreen().add_to(m)
MiniMap(toggle_display=True, tile_layer="CartoDB dark_matter").add_to(m)

def add_layer(data, key, show):
    if not show:
        return
    cfg = LAYER_CONFIG[key]
    fg = folium.FeatureGroup(name=cfg["label"], show=show)
    for row in data:
        lat, lon, nombre, detalle, intensidad = row
        if intensidad < min_intensidad:
            continue
        radius = INTENSIDAD_RADIUS[intensidad]
        color  = cfg["color"]
        # círculo de fondo
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius + 4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.15,
            weight=1,
            opacity=0.4,
        ).add_to(fg)
        # marcador principal
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=2,
            tooltip=f"<b>{nombre}</b><br>{detalle}<br><i>Intensidad: {INTENSIDAD_LABEL[intensidad]}</i>",
            popup=folium.Popup(
                f"<div style='font-family:monospace;min-width:200px'>"
                f"<b style='color:{color}'>{nombre}</b><br><br>"
                f"{detalle}<br><br>"
                f"<span style='color:#888'>Intensidad: {INTENSIDAD_LABEL[intensidad]}</span>"
                f"</div>",
                max_width=280
            ),
        ).add_to(fg)
    fg.add_to(m)

add_layer(CONFLICTOS, "conflictos", show_conflictos)
add_layer(PETROLEO,   "petroleo",   show_petroleo)
add_layer(CABLES,     "cables",     show_cables)
add_layer(ELECCIONES, "elecciones", show_elecciones)
add_layer(NUCLEAR,    "nuclear",    show_nuclear)
add_layer(MIGRACION,  "migracion",  show_migracion)

folium.LayerControl(collapsed=False).add_to(m)

# Render
st_folium(m, width=None, height=600, returned_objects=[])

# ─────────────────────────────────────────────
# TABLA DETALLE
# ─────────────────────────────────────────────
st.divider()
st.markdown("### 📋 Detalle por capa")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔴 Conflictos", "🟡 Petróleo", "🔵 Cables",
    "🟢 Elecciones", "🟠 Nuclear",  "🟣 Migración"
])

def render_table(data, tab):
    with tab:
        df = pd.DataFrame(data, columns=["Lat","Lon","Nombre","Detalle","Intensidad"])
        df = df[df["Intensidad"] >= min_intensidad][["Nombre","Detalle","Intensidad"]]
        df["Intensidad"] = df["Intensidad"].map(INTENSIDAD_LABEL)
        st.dataframe(df, use_container_width=True, hide_index=True)

render_table(CONFLICTOS, tab1)
render_table(PETROLEO,   tab2)
render_table(CABLES,     tab3)
render_table(ELECCIONES, tab4)
render_table(NUCLEAR,    tab5)
render_table(MIGRACION,  tab6)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.caption(
    "🧠 **SIEG — Sistema de Inteligencia Estratégica Geopolítica** · "
    "Con el Odroid en la Mochila · mcasrom · "
    "Datos de fuentes abiertas (ACLED, IISS, AIEA, Wikipedia, medios internacionales) · "
    f"Actualizado {datetime.now().strftime('%B %Y')}"
)
