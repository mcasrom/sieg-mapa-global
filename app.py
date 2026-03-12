#!/usr/bin/env python3
import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import json, os, math, pandas as pd

BASE="/home/miguelc/sieg-mapa-global/data"

def load_json(path):
    if not os.path.exists(path): return []
    with open(path) as f: return json.load(f)

def clean_coords(data):
    clean=[]
    for e in data:
        lat=e.get("lat"); lon=e.get("lon")
        if lat is None or lon is None: continue
        try: lat=float(lat); lon=float(lon)
        except: continue
        if math.isnan(lat) or math.isnan(lon): continue
        e["lat"]=lat; e["lon"]=lon
        clean.append(e)
    return clean

conflicts=clean_coords(load_json(os.path.join(BASE,"conflicts.json")))
hotspots=clean_coords(load_json(os.path.join(BASE,"hotspots.json")))
ranking=load_json(os.path.join(BASE,"ranking.json"))

st.set_page_config(layout="wide", page_title="SIEG-MAP v2")
st.title("🌍 SIEG-MAP v2 – Global Conflict Map")

st.sidebar.header("Filtros")
show_conflicts=st.sidebar.checkbox("Show conflict events",True)
show_hotspots=st.sidebar.checkbox("Show hotspots",True)
show_heatmap=st.sidebar.checkbox("Show heatmap",True)
show_timeline=st.sidebar.checkbox("Show timeline",True)
show_ranking=st.sidebar.checkbox("Show country ranking",True)

m=folium.Map(location=[20,0], zoom_start=2, tiles="cartodbpositron")
cluster=MarkerCluster().add_to(m)

def draw_markers(data,color):
    for e in data:
        folium.CircleMarker(
            location=[e["lat"], e["lon"]],
            radius=4+e.get("intensity",1)*2,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"{e.get('name','event')}<br>{e.get('detail','')}<br>{e.get('date','')}"
        ).add_to(cluster)

if show_conflicts: draw_markers(conflicts,"red")
if show_hotspots: draw_markers(hotspots,"orange")
if show_heatmap and conflicts:
    HeatMap([[e["lat"], e["lon"], e.get("intensity",1)] for e in conflicts]).add_to(m)

st_folium(m, width=1400, height=700)

# Timeline
if show_timeline and conflicts:
    st.subheader("📅 Timeline of Conflicts")
    df=pd.DataFrame(conflicts)
    df["date"]=pd.to_datetime(df["date"], errors='coerce')
    df=df.dropna(subset=["date"])
    timeline=df.groupby(df["date"].dt.date).size().reset_index(name="events")
    st.line_chart(timeline.set_index("date"))

# Ranking
if show_ranking and ranking:
    st.subheader("🏆 Countries in Tension")
    st.dataframe(pd.DataFrame(ranking))
