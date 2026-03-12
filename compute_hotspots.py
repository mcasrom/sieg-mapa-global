#!/usr/bin/env python3
import json, os
from sklearn.cluster import DBSCAN
import numpy as np
from collections import Counter

BASE="/home/miguelc/sieg-mapa-global/data"

conflicts_path=os.path.join(BASE,"conflicts.json")
hotspots_path=os.path.join(BASE,"hotspots.json")
countries_path=os.path.join(BASE,"countries.json")  # ISO + nombre + lat/lon aproximado

with open(conflicts_path) as f:
    data=json.load(f)

coords=np.array([[e["lat"],e["lon"]] for e in data])

hotspots=[]
if len(coords):
    clustering=DBSCAN(eps=2, min_samples=5).fit(coords)
    labels=clustering.labels_
    clusters={}
    for i, label in enumerate(labels):
        if label==-1: continue
        clusters.setdefault(label, []).append(data[i])
    for cluster_events in clusters.values():
        lats=[e["lat"] for e in cluster_events]
        lons=[e["lon"] for e in cluster_events]
        hotspots.append({
            "lat": sum(lats)/len(lats),
            "lon": sum(lons)/len(lons),
            "name": "Hotspot Cluster",
            "detail": f"{len(cluster_events)} events",
            "intensity": min(3,len(cluster_events)//5+1)
        })

with open(hotspots_path,"w") as f:
    json.dump(hotspots,f, indent=2)

# Ranking países
with open(countries_path) as f:
    countries=json.load(f)  # [{"name":"Spain","lat":40,"lon":-3.7},...]

ranking=[]
for c in countries:
    count=sum(1 for e in data if abs(e["lat"]-c["lat"])<5 and abs(e["lon"]-c["lon"])<5)
    if count>0:
        ranking.append({"country":c["name"],"events":count})
ranking=sorted(ranking, key=lambda x:x["events"], reverse=True)
with open(os.path.join(BASE,"ranking.json"),"w") as f:
    json.dump(ranking,f, indent=2)
