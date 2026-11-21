# Roadmap

Open work from the November 2026 review, highest impact first. The P0 trust fixes and the
P1 data-pipeline fixes are done; read `AGENTS.md` before picking anything up.

## Next: correctness and comprehension

- [ ] **Destination matching resolves a stop name to a street.** In Basel, "Bahnhof"
  matches "Bahnhofstrasse" through the `startsWith` fallback and answers "14 stops to
  Bahnhofstrasse". Match whole words, and say "no direct connection" instead of guessing.
  Repro: stop Basel, Aeschenplatz, destination "Bahnhof".
- [ ] **Check the isolated poles.** `python check_data.py` flags Basel Aeschenplatz M
  (nearest pole 90 m) and Lausanne Chauderon A (84 m). Confirm on site whether they belong
  to the stop or are separate waiting points.
- [ ] **Four Basel routes have no next stop** (`next: "?"`, lines 8, 10, 11, 12). Find the
  next stop in the OSM relation or drop the line from that pole.
- [ ] **FAQ is English only** while its link label is translated. Translate `faq.html` or
  mark the link "(in English)".
- [ ] **Shareable links.** No URL carries stop and destination, so a volunteer cannot send
  "Bern, Zytglogge to Worb Dorf". Add a hash route and restore it on load.

## Accessibility and standards

- [ ] Add `<!doctype html><html lang="en"><head>...<body>` to `index.html`. It currently
  loads in quirks mode (`document.compatMode` is `BackCompat`).
- [ ] Move `aria-live` off `#answer`. The whole card is replaced on every keystroke, so a
  screen reader re-reads it per character. Announce the verdict from a separate node,
  debounced.
- [ ] Map markers are `<g tabindex="0" role="button">` with no visible focus. Add
  `.mk:focus-visible`.
- [ ] In RTL, the coordinate input renders `7.5949 ,47.5513`. Numeric and Latin fields need
  `dir="ltr"`.
- [ ] The all-poles section is `h4` before `h3` pole cards; fix the heading order.
- [ ] Check contrast and target size on the smallest phones; the 12 px route text in the
  pole cards is at the lower limit.

## Performance, privacy, offline

- [ ] Street labels render at about 6.6 CSS px at 390 px width, independent of zoom
  (font size scales with the viewBox). Set a screen-space minimum near 10 px.
- [ ] Self-host the four font files. Google Fonts costs two extra origins, is unreachable
  in mainland China, and blocks a service worker. Self-hosting also enables offline.
- [ ] Vendor Tesseract.js or add `integrity` to its jsdelivr URL. It is the only
  third-party script, and sign scanning downloads it on first use.
- [ ] Add a service worker precaching `index.html`, `faq.html`, `stops.json`, the logo and
  the fonts, so first load offline works.
- [ ] `faq.html` says nothing is stored, but `ws-lang` and `ws-wc` are kept in
  localStorage. Correct the text or stop storing the wheelchair preference.
- [ ] Add `LICENSE` before making the repository public.
- [ ] Add a translation check (all 20 languages share the `en` key set) and a small test
  runner. It would have caught the dead `take` key, which is present in 6 languages and
  missing in 14; delete it.

## Product

- [ ] Live departure times and journeys with a change of line. Both need a timetable API
  and are outside what the OSM snapshot can answer.
- [ ] More stops. The build pipeline handles any number; the page loads all of
  `stops.json` (56 KB gzipped for 8 stops), so split per stop once the list grows.
- [ ] Native-speaker review for Kurdish, Tamil and Tigrinya, then drop the beta label.
