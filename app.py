#!/usr/bin/env python3
import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import pandas as pd
import json, os, math
from datetime import datetime

# ---------------------------
# RUTAS
# ---------------------------
BASE = "/home/miguelc/sieg-mapa-global/data"
CONFLICTS_FILE = os.path.join(BASE,"conflicts.json")
HOTSPOTS_FILE = os.path.join(BASE,"hotspots.json")
RANKING_FILE = os.path.join(BASE,"ranking.json")
os.makedirs(BASE, exist_ok=True)

# ---------------------------
# CARGA Y LIMPIEZA DE DATOS
# ---------------------------
def load_json(path):
    if not os.path.exists(path): return []
    with open(path) as f:
        return json.load(f)

def clean_coords(data):
    clean=[]
    for e in data:
        lat=e.get("lat")
        lon=e.get("lon")
        if lat is None or lon is None: continue
        try:
            lat=float(lat)
            lon=float(lon)
        except:
            continue
        if math.isnan(lat) or math.isnan(lon): continue
        e["lat"]=lat
        e["lon"]=lon
        clean.append(e)
    return clean

conflicts = clean_coords(load_json(CONFLICTS_FILE))
hotspots = clean_coords(load_json(HOTSPOTS_FILE))
ranking = load_json(RANKING_FILE)

# ---------------------------
# STREAMLIT CONFIG
# ---------------------------
st.set_page_config(page_title="SIEG · Mapa Geopolítico Global", layout="wide")
st.title("🌍 SIEG · Mapa Geopolítico Global")
st.markdown("*Inteligencia estratégica de fuentes abiertas — Con el Odroid en la Mochila*")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("Filtros")
show_conflicts = st.sidebar.checkbox("🔴 Conflictos", True)
show_hotspots = st.sidebar.checkbox("🟠 Hotspots", True)
show_heatmap = st.sidebar.checkbox("Heatmap", False)
show_ranking = st.sidebar.checkbox("Ranking países", True)
min_intensity = st.sidebar.slider("Intensidad mínima (1-3)", 1, 3, 1)

# ---------------------------
# MAPA
# ---------------------------
m = folium.Map(location=[20,0], zoom_start=2, tiles="CartoDB positron")
cluster_conflicts = MarkerCluster(name="Conflictos").add_to(m)
cluster_hotspots = MarkerCluster(name="Hotspots").add_to(m)

def add_markers(data, cluster, color):
    for e in data:
        intensity = e.get("intensity",1)
        if intensity < min_intensity:
            continue
        folium.CircleMarker(
            location=[e["lat"], e["lon"]],
            radius=4 + intensity*2,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"<b>{e.get('name','Evento')}</b><br>{e.get('detail','')}<br>{e.get('date','')}"
        ).add_to(cluster)

if show_conflicts: add_markers(conflicts, cluster_conflicts, "red")
if show_hotspots: add_markers(hotspots, cluster_hotspots, "orange")

if show_heatmap and conflicts:
    HeatMap([[e["lat"], e["lon"], e.get("intensity",1)] for e in conflicts]).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
st_folium(m, width=1400, height=700)

# ---------------------------
# TABLA DETALLE
# ---------------------------
st.subheader("📋 Resumen de conflictos")
df_conflicts = pd.DataFrame(conflicts)
if not df_conflicts.empty:
    df_conflicts["intensity_label"] = df_conflicts["intensity"].map({1:"Bajo",2:"Medio",3:"Alto"})
    df_conflicts_display = df_conflicts[["name","detail","intensity_label","lat","lon"]]
    df_conflicts_display = df_conflicts_display.rename(columns={
        "name":"Nombre", "detail":"Detalle", "intensity_label":"Intensidad", "lat":"Lat", "lon":"Lon"
    })
    st.dataframe(df_conflicts_display, use_container_width=True)
else:
    st.write("No hay conflictos cargados.")

# ---------------------------
# RANKING PAÍSES
# ---------------------------
if show_ranking:
    st.subheader("🏆 Ranking países por incidencia")
    if ranking:
        df_rank = pd.DataFrame(ranking)
        st.dataframe(df_rank, use_container_width=True)
    else:
        st.write("Ranking no disponible.")

# ---------------------------
# FOOTER
# ---------------------------
st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y')} · Datos curados de fuentes abiertas")
