# Changelog

Dates are CalVer `YYYY.MM.DD.hhmm` in local time, each with the short commit hash it records.

## [2026.11.21.1739] - 28f0f3e

- `AGENTS.md` corrected: `via[0]` is the next stop, platforms keep lat/lon for GPS distance
  as well as x/y for drawing, and `check_data.py` does not compare labels with OSM
  `local_ref`. The demo pole on first load is documented as intended.

## [2026.11.21.1739] - 0e4b8e4

- Restored the demo pole on first load by request. The map again shows "you are here", the
  walking route and the crossing advice, so the first screen explains what is confusing
  about a stop with several poles. A tap, GPS or a scanned sign replaces the demo pole.

## [2026.11.21.1737] - 8d848b3

- `stops.json` now carries step-free, tactile, bench, shelter and crossing details for all
  eight stops. The wheelchair switch and the crossing advice work everywhere; Genève and
  Luzern poles without an OSM `wheelchair` tag are reported as unknown.

## [2026.11.21.1737] - 5d3f738

- Accessibility data moved to `access.json`, keyed by stop and platform id. `merge_data.py`
  re-applies it on every merge, so refreshing the raw batches no longer drops it.
  `add_access.py` writes only `access.json` and then merges.

## [2026.11.21.1728] - a1452a6

- `ROADMAP.md` records the remaining accessibility, standards, performance, privacy and
  offline work, plus the data review items and the destination matching bug.

## [2026.11.21.1728] - 5276dd5

- `AGENTS.md` describes the app, the data model and its invariants, the pipeline, browser
  verification and the working rules.

## [2026.11.21.1727] - 058dbac

- `check_data.py` fails on structural problems and warns on unknown route names, isolated
  poles and stops without accessibility data. `--strict` fails on warnings too.

## [2026.11.21.1727] - 55f59e8

- Removed a `build_data.py` comment that described platform merging code which does not
  exist. Distance-based merging would be wrong: Basel G and H are distinct poles 5.5 m apart.

## [2026.11.21.1725] - ac34fbe

- On phones the order is now inputs, location, answer, street plan. The answer starts at
  419 px in an 844 px viewport instead of below the fold.

## [2026.11.21.1725] - 1ebeb8d

- Using the location button or pasted coordinates no longer clears the typed destination.

## [2026.11.21.1725] - aadb8e7

- The page no longer invents a current position. The map, walking help and answer wait for
  a tap, GPS or a scanned sign instead of showing a demo pole as "you are here".

## [2026.11.21.1724] - 940c026

- `.worktrees/` is gitignored.
