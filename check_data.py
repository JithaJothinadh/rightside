"""Check stops.json after a merge and list data problems.

    python check_data.py            # structural errors fail, warnings only print
    python check_data.py --strict   # warnings fail too

Errors: a stop with fewer than two poles, duplicate labels or ids, a platform without
position or routes. Warnings: unknown names in a route ("?"), an isolated pole, a stop
without accessibility data.
"""
import json, math, sys

FAR = 70  # metres to the nearest other pole; an isolated pole is probably another waiting point


def main(strict=False):
    d = json.load(open("stops.json", encoding="utf-8"))
    errors, warns = [], []
    if not d.get("generated"):
        errors.append("no generated date")
    for s in d.get("stops", []):
        name = s.get("name", "?")
        ps = s.get("platforms", [])
        if len(ps) < 2:
            errors.append(f"{name}: fewer than two poles")
        labels = [p.get("label") for p in ps]
        if len(set(labels)) != len(labels):
            errors.append(f"{name}: duplicate pole labels {labels}")
        if len({p.get("id") for p in ps}) != len(ps):
            errors.append(f"{name}: duplicate platform ids")
        for p in ps:
            lab = p.get("label", "?")
            if not p.get("id") or "x" not in p or "y" not in p or not p.get("routes"):
                errors.append(f"{name} {lab}: incomplete platform")
                continue
            for r in p["routes"]:
                if "?" in (r.get("line"), r.get("to"), r.get("next")):
                    warns.append(f"{name} {lab}: unknown name in line {r.get('line')} ({r.get('to')} -> {r.get('next')})")
            near = min(math.hypot(p["x"] - q["x"], p["y"] - q["y"]) for q in ps if q is not p)
            if near > FAR:
                warns.append(f"{name} {lab}: nearest pole is {round(near)} m away, check that it belongs to this stop")
        if "xings" not in s or not all("acc" in p for p in ps):
            warns.append(f"{name}: no accessibility data (run add_access.py)")

    for w in warns:
        print("warn:", w)
    for e in errors:
        print("error:", e)
    print(f"{len(d.get('stops', []))} stops, {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv[1:]))
