"""Add step-free / accessibility details from OpenStreetMap into access.json.

merge_data.py writes stops.json from the raw batches and then re-applies access.json, so
enrichment survives every data refresh and never has to be redone.

Run:
    python build_data.py ...   ->  python merge_data.py  ->  python add_access.py

For each pole (platform) it reads:  wheelchair, tactile_paving, bench, shelter
and stores them in access.json as  {"poles": {"<platform id>": {"wc": "yes|limited|no", ...}}}
(keys only when OSM records them).

For each pedestrian crossing near the stop it stores
    "xings": [{"x", "y", "sig": bool, "kerb": "lowered|flush|raised|...", "tact": ..., "snd": ...}]
where sig = has traffic lights. Positions use the same local metre grid as the rest of stops.json.

The public Overpass servers are often busy. The script saves after every stop and skips stops
it has already done, so if some fail, just run it again later.
"""
import json, math, os, sys, time, urllib.parse, urllib.request

SERVERS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
UA = {"User-Agent": "rightside-prototype/0.1 (hackathon demo)"}
R_MAP = 170


def overpass(q):
    for attempt in range(8):
        url = SERVERS[attempt % len(SERVERS)]
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print(f"  retry {attempt} ({url.split('/')[2]}): {e}", file=sys.stderr)
            time.sleep(10 + 5 * attempt)  # back off: the public servers are often busy
    raise RuntimeError("overpass failed")


def xy(lat, lon, lat0, lon0):
    return ((lon - lon0) * 111320 * math.cos(math.radians(lat0)), -(lat - lat0) * 110540)


def enrich(s):
    nodes = [p["id"].split("/")[1] for p in s["platforms"] if p["id"].startswith("node/")]
    ways = [p["id"].split("/")[1] for p in s["platforms"] if p["id"].startswith("way/")]
    q = "[out:json][timeout:90];("
    if nodes:
        q += f"node(id:{','.join(nodes)});"
    if ways:
        q += f"way(id:{','.join(ways)});"
    q += f');out tags;node(around:{R_MAP},{s["lat"]},{s["lon"]})["highway"~"^(crossing|traffic_signals)$"];out body;'
    els = overpass(q)["elements"]

    tags = {f'{e["type"]}/{e["id"]}': e.get("tags", {}) for e in els}
    poles = {}
    for p in s["platforms"]:
        t = tags.get(p["id"], {})
        poles[p["id"]] = {k2: t[k1] for k1, k2 in [("wheelchair", "wc"), ("tactile_paving", "tact"),
                                                   ("bench", "bench"), ("shelter", "shelter")] if k1 in t}

    xings = []
    for e in els:
        t = e.get("tags", {})
        if e["type"] != "node" or "lat" not in e:
            continue
        if not (t.get("highway") == "crossing" or (t.get("highway") == "traffic_signals" and t.get("crossing"))):
            continue
        x, y = xy(e["lat"], e["lon"], s["lat"], s["lon"])
        if math.hypot(x, y) > R_MAP:
            continue
        sig = (t.get("highway") == "traffic_signals" or t.get("crossing") == "traffic_signals"
               or t.get("crossing:signals") == "yes")
        xi = {"x": round(x, 1), "y": round(y, 1), "sig": bool(sig)}
        for k1, k2 in [("kerb", "kerb"), ("tactile_paving", "tact"), ("traffic_signals:sound", "snd")]:
            if k1 in t:
                xi[k2] = t[k1]
        xings.append(xi)

    wc = [poles[p["id"]].get("wc", "?") for p in s["platforms"]]
    print(f"   poles wheelchair: {wc}   crossings: {len(xings)} ({sum(x['sig'] for x in xings)} with lights, "
          f"{sum(1 for x in xings if x.get('kerb') in ('lowered', 'flush'))} lowered kerb)", file=sys.stderr)
    return {"poles": poles, "xings": xings}


def save(data):
    json.dump(data, open("access.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


def main():
    stops = json.load(open("stops.json", encoding="utf-8"))
    data = json.load(open("access.json", encoding="utf-8")) if os.path.exists("access.json") \
        else {"generated": time.strftime("%Y-%m-%d"), "stops": {}}
    failed = []
    for s in stops["stops"]:
        if s["name"] in data["stops"]:
            print("-- already done:", s["name"], file=sys.stderr)
            continue
        print("->", s["name"], file=sys.stderr)
        try:
            data["stops"][s["name"]] = enrich(s)
        except Exception as e:
            print("  FAILED, run again later:", e, file=sys.stderr)
            failed.append(s["name"])
            continue
        # keep each finished stop, even if a later one fails
        save(data)
        time.sleep(2)
    save(data)
    # access.json is the source of truth; merge applies it to stops.json
    import merge_data
    merge_data.main()
    print("missing:", ", ".join(failed) if failed else "none", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
