# Rightside

Rightside helps newcomers to Switzerland (immigrants, refugees, international students and tourists) find **which side of the road to wait on** for their bus or tram.

Many Swiss stops have two or more poles with the same name, often facing each other across a street, with buses leaving in opposite directions. A navigation app tells you the stop name. Rightside tells you which pole.

**Try it:** https://jithajothinadh.github.io/rightside/ (opens on Bern, Zytglogge. "Use my location" works on this address.)

## What it does

- **Pick a stop and a destination.** Rightside answers "Wait at stop D", with the line, the direction and the next stop.
- **Look-alike warning.** If a same-named pole a few metres away goes the other way, the page warns you. It also gives a check you can do on the spot without reading German: *"The sign must show line 12 towards Zentrum Paul Klee. If it shows Holligen, cross to the other side."*
- **Street side.** "Kramgasse, south side", worked out from the OpenStreetMap street geometry. It is shown only where it actually tells the two poles apart.
- **Street plan.** A drawn map of the stop with every pole, the direction each bus leaves, and pedestrian crossings. It zooms in on your pole and its look-alike.
- **Walking help.** Tap where you are standing, or use GPS. Rightside says "stay here" or "cross to stop D, 13 m, use the zebra crossing".
- **Live location.** It finds your closest stop and pole from GPS, or from pasted coordinates or a map link when GPS is unavailable.
- **20 languages.** These cover the languages most spoken by immigrants, refugees and students in Switzerland: English, German, French, Italian, Portuguese, Albanian, Spanish, Bosnian/Croatian/Serbian, Macedonian, Turkish, Kurdish (Kurmanji), Arabic, Persian/Dari, Tamil, Tigrinya, Ukrainian, Russian, Polish, Romanian and Chinese. The page picks one from the phone's language. Arabic and Persian display right to left. Kurdish, Tamil and Tigrinya are marked *beta* in the menu until a native speaker has reviewed them.
- **Read aloud.** "Listen" reads the answer in your language. "Play it aloud for them" speaks a question in the local language (German, French or Italian) to a passer-by.

## Run it

It is a static page with no build step.

```sh
python -m http.server 8000
# open http://localhost:8000
```

`index.html` loads `stops.json` from the same folder, so it needs to be served over HTTP. Opening the file directly will not work. Any static host works too, for example GitHub Pages or Netlify.

Reading aloud uses the browser's own voices (Web Speech API), which work offline on most phones. When the page runs as a claude.ai Artifact, it uses Claude's voice where available.

## Stops included

The prototype covers eight stops with confusing same-named poles:

| Stop | Poles |
|---|---|
| Basel, Aeschenplatz | 8 |
| Bern, Zytglogge | 8 |
| Fribourg, Tilleul/Cathédrale | 2 |
| Genève, Plainpalais | 6 |
| Lausanne, Chauderon | 3 |
| Luzern, Kantonalbank | 4 |
| Zürich, Bucheggplatz | 7 |
| Zürich, Schaffhauserplatz | 6 |

## Refresh or add stops

```sh
python build_data.py "Winterthur, Technikum" "Bern, Bahnhof"   # writes stops.json
mv stops.json stops_c.json                                       # keep each batch as stops_<x>.json
python merge_data.py                                             # merges every stops_*.json into stops.json
```

- `build_data.py` looks up each stop on [transport.opendata.ch](https://transport.opendata.ch) and then queries OpenStreetMap through the Overpass API. It collects the stop's poles, the bus and tram routes serving each one in stop order (which gives the direction), and the surrounding streets and crossings. Overpass is often busy. The script retries, but a stop can still time out, so run it again later. Set `OUT=stops_x.json` to write to another file.
- `merge_data.py` removes duplicate lines. It labels each pole with the letter on its real stop sign where OSM records one (`local_ref`), otherwise A, B, C. It also trims streets that fall outside the drawn map.
- `stops_a.json` and `stops_b.json` are the raw batches behind the current `stops.json`.

## Before real-world use

- **Data is a snapshot**, taken on the date shown in the page footer, and only as accurate as OpenStreetMap. Verify the stops you demo on site.
- **Translations need native review.** They were written without native-speaker checks. Have someone fluent in each language review them, especially the crossing instructions.
- **Not yet included:** live departure times and journeys with a change of line.
- **Read-aloud voices:** Listen only uses a voice of the selected language and shows which one it used. Many devices have no voice for Albanian, Bosnian, Macedonian, Kurdish, Tamil or Tigrinya, and the page then says so rather than reading in another language. On Android, iPhone, Windows and Mac it also says where to add a voice and links to the vendor's own guide (Google's opens in the reader's language). For Kurdish and Tigrinya, which almost no device has a voice for, it says that plainly instead.
- **Offline install:** the page works without a connection once loaded. Opening it for the first time offline needs a service worker, which has not been added yet.

## Data and licences

- Stop positions, routes and streets: © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, available under the Open Database License (ODbL). `stops.json` is derived from OSM data, so it is also under the ODbL. Keep the attribution, and share changes to the data under the same licence.
- Stop names and coordinates: [opentransportdata.swiss](https://opentransportdata.swiss/) via [transport.opendata.ch](https://transport.opendata.ch).
- Code: no licence chosen yet. Add a `LICENSE` file before making the repository public if you want others to reuse the code.
