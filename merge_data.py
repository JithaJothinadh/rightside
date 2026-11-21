"""Merge stops_*.json into stops.json: dedupe lines, give every pole a unique label."""
import glob, json

stops, gen = {}, ""
for f in sorted(glob.glob("stops_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    gen = max(gen, d["generated"])
    for s in d["stops"]:
        stops[s["name"]] = s

for s in stops.values():
    for p in s["platforms"]:
        seen, rs = set(), []
        for r in p["routes"]:
            k = (r["line"], r["to"])
            if k not in seen:
                seen.add(k); rs.append(r)
        p["routes"] = rs
    # real sign letters (OSM local_ref) win; the rest get the next free letter
    used = {p["pole"] for p in s["platforms"] if p.get("pole")}
    free = (c for c in "ABCDEFGHJKLMNPQRSTUVWXYZ" if c not in used)
    for p in sorted(s["platforms"], key=lambda p: p["lon"]):
        p["label"] = p["pole"] if p.get("pole") else next(free)
    s["platforms"].sort(key=lambda p: p["label"])
    # keep only streets that reach into the drawn 300 m square
    s["streets"] = [w for w in s["streets"] if any(abs(x) < 160 and abs(y) < 160 for x, y in w["p"])]

out = sorted(stops.values(), key=lambda s: s["name"])
json.dump({"generated": gen, "stops": out}, open("stops.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
for s in out:
    print(s["name"], [p["label"] for p in s["platforms"]])
