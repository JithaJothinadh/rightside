# Right Side

A static page that tells a newcomer to Switzerland which **pole** of a bus or tram stop to
wait at, in 20 languages, with a drawn street plan, walking help, a camera view and a sign
scanner. Prototype: eight stops, data snapshot in `stops.json`.

## Files

| File | Role |
|---|---|
| `index.html` | The whole app: CSS, 20 translation tables, map drawing, route finder, speech, AR and OCR. No build step and no framework. |
| `faq.html` | Static FAQ, English only. |
| `stop*.json` | `stops.json` is served; `stops_a.json`, `stops_b.json` are raw build batches. Never hand-edit `stops.json`. |
| `access.json` | Accessibility data keyed by stop name and platform id. Owned by `add_access.py`. |
| `build_data.py` | Queries transport.opendata.ch and Overpass; writes one batch file. |
| `merge_data.py` | Merges `stops_*.json`, labels poles, then applies `access.json`. The only writer of `stops.json`. |
| `add_access.py` | Enriches `access.json` from OSM, then calls the merge. |
| `check_data.py` | Validates `stops.json`; see `ROADMAP.md`. |
| `ROADMAP.md` | Open work from the November 2026 review. |

## Data model

`stops.json` = `{generated, stops[]}`. A stop has `name`, `sbbId`, `lat`, `lon`,
`platforms[]`, `streets[]` (OSM ways with kind, name and points) and `xings[]` (crossings
with `sig` and `kerb`). A platform has `id` (`node/...` or `way/...`), `x`, `y` in metres on
a local grid centred on the stop, `label`, `routes[]` and, once enriched, `acc`.
A route has `line`, `mode`, `to`, `next`, `bearing` and `via` (stops in order; `via[0]` is
the boarding stop, so the index plus one is the number of stops).

Invariants, all checked by `check_data.py`: pole labels unique within a stop, platform ids
unique, every platform has a position and at least one route, `label` matches the sign
letter when OSM records one. Coordinates are metres, and the same grid is used by the map,
the route finder and the crossing search; never store lat/lon in a platform.

## Pipeline

```sh
python build_data.py "Winterthur, Technikum"   # writes stops.json
mv stops.json stops_c.json                      # keep each batch as stops_<x>.json
python merge_data.py                            # batches + access.json -> stops.json
python add_access.py                            # Overpass -> access.json -> merge
python check_data.py                            # 0 errors, warnings for a human
```

Overpass is public and often busy. Both scripts retry and save after each stop, so a run
that times out can simply be repeated. `add_access.py` skips stops already in `access.json`.

## Running and verifying

```sh
python -m http.server 8000    # then open http://localhost:8000
```

`index.html` fetches `stops.json`, so it must be served over HTTP. Verify a change in a
browser, not by reading the code: load the page, check the console for errors, then check
at 390x844 as well as desktop. The behaviour that has broken before: a claimed "you are
here" without a tap or GPS, a lost destination after using the location button, map labels
at an unreadable size, and RTL layouts that reverse numbers.

Do not add a framework or a build step. Keep `index.html` self-contained; the only external
runtime dependency is Tesseract.js for the sign scanner and Google Fonts for the type.

## Working rules

- Work in a git worktree under `.worktrees/<topic>`; `.worktrees/` is gitignored.
- Commit atomically, in English, imperative subject. Never push to GitHub without an
  explicit instruction from the human; local commits are always expected.
- No em dashes, smart quotes or emoji in files. Plain hyphens and straight quotes. Unicode
  letters and CJK are fine.
- Adding a UI string means adding it to all 20 language tables. A string missing from a
  table renders as `undefined`.
- Stop data is ODbL: keep the OpenStreetMap attribution in the footer and in the data.
