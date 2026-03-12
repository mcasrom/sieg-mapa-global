#!/usr/bin/env python3
import requests, json, os
from datetime import datetime, timedelta

BASE="/home/miguelc/sieg-mapa-global/data"
os.makedirs(BASE, exist_ok=True)

today=datetime.utcnow()
yesterday=today - timedelta(days=1)

url=f"https://api.gdeltproject.org/api/v2/events/search?query=conflict&mode=ArtList&maxrecords=500&format=json&startdatetime={yesterday.strftime('%Y%m%d000000')}&enddatetime={today.strftime('%Y%m%d235959')}"

try:
    r=requests.get(url)
    r.raise_for_status()
    events=r.json().get("events", [])
except Exception as e:
    print("Error fetching GDELT:", e)
    events=[]

clean=[]
for e in events:
    lat=e.get("ActionGeo_Lat")
    lon=e.get("ActionGeo_Long")
    if lat is None or lon is None:
        continue
    try:
        lat=float(lat)
        lon=float(lon)
    except:
        continue
    if lat!=lat or lon!=lon:
        continue
    date_str=e.get("ActionGeo_Date") or today.strftime("%Y-%m-%d")
    clean.append({
        "lat": lat,
        "lon": lon,
        "name": e.get("Actor1Name","Event"),
        "detail": e.get("EventCode",""),
        "intensity": 1,
        "date": date_str
    })

with open(os.path.join(BASE,"conflicts.json"),"w") as f:
    json.dump(clean,f, indent=2)

print("Events collected:", len(clean))
