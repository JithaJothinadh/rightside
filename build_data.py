"""Build stops.json for the Rightside prototype.

For each candidate stop: look it up on transport.opendata.ch (official name + coords),
then query OpenStreetMap (Overpass) for the physical platforms, the bus/tram routes
that serve each one (in stop order), and the streets around it.
Run:  python build_data.py   -> writes stops.json
"""
import os, json, math, sys, time, urllib.parse, urllib.request

CANDIDATES = [
    "Zürich, Milchbuck", "Zürich, Bucheggplatz", "Zürich, Schaffhauserplatz",
    "Bern, Zytglogge", "Basel, Aeschenplatz", "Luzern, Kantonalbank",
    "Lausanne, Chauderon", "Genève, Plainpalais", "Lugano, Centro",
    "Winterthur, Technikum", "St. Gallen, Marktplatz", "Fribourg, Tilleul/Cathédrale",
]
OVERPASS = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "rightside-prototype/0.1 (hackathon demo)"}
R_PLAT, R_MAP = 220, 170  # metres


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def overpass(lat, lon):
    q = f"""[out:json][timeout:90];
(nw(around:{R_PLAT},{lat},{lon})["public_transport"="platform"];
 node(around:{R_PLAT},{lat},{lon})["highway"="bus_stop"];
 node(around:{R_PLAT},{lat},{lon})["railway"="tram_stop"];)->.p;
(rel(bn.p)["type"="route"]["route"~"^(bus|tram|trolleybus)$"];
 rel(bw.p)["type"="route"]["route"~"^(bus|tram|trolleybus)$"];)->.r;
.r out body;
node(r.r)["name"];
out body;
way(r.r)["public_transport"="platform"];
out tags center;
way(around:{R_MAP},{lat},{lon})["highway"~"^(trunk|primary|secondary|tertiary|residential|unclassified|living_street|pedestrian|service|footway)$"];
out geom;
node(around:{R_MAP},{lat},{lon})["highway"="crossing"];
out body;"""
    for attempt in range(3):
        try:
            return get(OVERPASS, urllib.parse.urlencode({"data": q}).encode())
        except Exception as e:  # rate limit / timeout
            print("  overpass retry", attempt, e, file=sys.stderr)
            time.sleep(10)
    raise RuntimeError("overpass failed")


def xy(lat, lon, lat0, lon0):
    return ((lon - lon0) * 111320 * math.cos(math.radians(lat0)), -(lat - lat0) * 110540)


def bearing(a, b):
    la1, la2 = math.radians(a["lat"]), math.radians(b["lat"])
    dl = math.radians(b["lon"] - a["lon"])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def short(name):
    return name.split(",")[-1].strip()


def build(query):
    loc = get("https://transport.opendata.ch/v1/locations?" + urllib.parse.urlencode({"query": query, "type": "station"}))
    st = loc["stations"][0]
    lat0, lon0 = st["coordinate"]["x"], st["coordinate"]["y"]
    key = short(st["name"]).lower()
    data = overpass(lat0, lon0)
    nodes = {}  # (type,id) -> element with lat/lon (platform ways use their centre)
    for e in data["elements"]:
        if e["type"] == "node":
            nodes[("node", e["id"])] = e
        elif e["type"] == "way" and "center" in e:
            nodes[("way", e["id"])] = {**e, "lat": e["center"]["lat"], "lon": e["center"]["lon"]}
    rels = [e for e in data["elements"] if e["type"] == "relation"]
    ways = [e for e in data["elements"] if e["type"] == "way" and "geometry" in e]

    def is_ours(n):
        nm = n.get("tags", {}).get("name", "").lower()
        return nm and (short(nm) == key or nm == st["name"].lower())

    plats = {}
    for r in rels:
        t = r.get("tags", {})
        seq = [(m["type"], m["ref"]) for m in r["members"]
               if m["role"].startswith("platform") and (m["type"], m["ref"]) in nodes]
        for i, ref in enumerate(seq):
            n = nodes[ref]
            if not is_ours(n) or math.dist((0, 0), xy(n["lat"], n["lon"], lat0, lon0)) > R_PLAT:
                continue
            if i == len(seq) - 1:
                continue  # terminus arrival: nobody boards here in this direction
            later = [nodes[x].get("tags", {}).get("name") for x in seq[i + 1:]]
            later = [short(x) for x in later if x]
            nxt = nodes[seq[i + 1]]
            p = plats.setdefault(ref, {"id": f"{ref[0]}/{ref[1]}", "lat": n["lat"], "lon": n["lon"],
                                        "pole": n.get("tags", {}).get("local_ref"), "routes": []})
            if any(x["line"] == t.get("ref") and x["to"] == later[-1] for x in p["routes"]):
                continue
            p["routes"].append({
                "line": t.get("ref", "?"), "mode": t.get("route"), "colour": t.get("colour"),
                "to": short(t.get("to") or later[-1]) if later else "?",
                "next": short(nxt.get("tags", {}).get("name", "?")),
                "bearing": round(bearing(n, nxt)),
                "via": list(dict.fromkeys(later)),
            })
    plats = [p for p in plats.values() if p["routes"]]
    if len(plats) < 2:
        return None
    # merge_data.py gives every pole its final label; here only the fallback letter
    plats.sort(key=lambda p: (p["pole"] or "~", p["lon"]))
    for i, p in enumerate(plats):
        p["x"], p["y"] = [round(v, 1) for v in xy(p["lat"], p["lon"], lat0, lon0)]
        p["label"] = p["pole"] or "ABCDEFGHJK"[i]
        p["routes"].sort(key=lambda r: (len(r["line"]), r["line"]))
    streets = []
    for w in ways:
        hw = w["tags"].get("highway")
        pts = [xy(g["lat"], g["lon"], lat0, lon0) for g in w.get("geometry", [])]
        streets.append({"k": hw, "n": w["tags"].get("name"), "p": [[round(a, 1), round(b, 1)] for a, b in pts]})
    crossings = [[round(v, 1) for v in xy(n["lat"], n["lon"], lat0, lon0)] for n in nodes.values()
                 if n.get("tags", {}).get("highway") == "crossing"
                 and math.dist((0, 0), xy(n["lat"], n["lon"], lat0, lon0)) < R_MAP]
    return {"name": st["name"], "sbbId": st["id"], "lat": lat0, "lon": lon0,
            "platforms": plats, "streets": streets, "crossings": crossings}


out = []
for q in (sys.argv[1:] or CANDIDATES):
    print("->", q, file=sys.stderr)
    try:
        s = build(q)
    except Exception as e:
        print("  failed:", e, file=sys.stderr); continue
    if s:
        dirs = {r["to"] for p in s["platforms"] for r in p["routes"]}
        print(f"  {len(s['platforms'])} platforms, {len(dirs)} directions", file=sys.stderr)
        out.append(s)
    time.sleep(3)
json.dump({"generated": time.strftime("%Y-%m-%d"), "stops": out}, open(os.environ.get("OUT","stops.json"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
print("wrote", len(out), "stops", file=sys.stderr)
