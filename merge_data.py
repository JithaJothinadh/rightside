"""Merge stops_*.json into stops.json: dedupe lines, give every pole a unique label,
then apply the accessibility details kept in access.json (add_access.py owns that file)."""
import glob, json, os

ACCESS = "access.json"


def load_batches():
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
    return stops, gen


def apply_access(stops):
    """Attach acc and xings from access.json. Returns its generated date, or None."""
    if not os.path.exists(ACCESS):
        return None
    acc = json.load(open(ACCESS, encoding="utf-8"))
    for name, a in acc.get("stops", {}).items():
        s = stops.get(name)
        if not s:
            continue
        for p in s["platforms"]:
            p["acc"] = a.get("poles", {}).get(p["id"], {})
        s["xings"] = a.get("xings", [])
    return acc.get("generated")


def main():
    stops, gen = load_batches()
    gen = max(gen, apply_access(stops) or "")
    out = sorted(stops.values(), key=lambda s: s["name"])
    json.dump({"generated": gen, "stops": out}, open("stops.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    for s in out:
        print(s["name"], [p["label"] for p in s["platforms"]])


if __name__ == "__main__":
    main()
