# City Memory: Novosibirsk

Digital Humanities project on commemorative street names in Novosibirsk.

Live dashboard: https://ostvald-city-memory-project-novosibirsk.static.hf.space/index.html

The project asks a simple question: **who does the city commemorate through its street names?**

We combined OpenStreetMap street data with Wikidata/Wikipedia biographical data, manually verified ambiguous cases and built an interactive dashboard for exploring gender, occupation, historical period and repeated commemoration.

## Dataset

- **2,783** streets in the city dataset
- **536** streets named after people
- **433** unique commemorated people
- about **92% / 91%** Wikipedia / Wikidata coverage
- **95% men / 5% women** among commemorated people
- the four largest groups — military figures, writers, scientists and politicians — account for about **73%** of named individuals

## Dashboard

The browser dashboard includes:

- an interactive Leaflet map of commemorative streets
- filters by gender, occupation and historical period
- Chart.js visualizations
- a street ↔ person network graph built with Vis.js
- search across streets and people
- person cards with biographical context

![Map view](docs/map-view.png)

| Memory wall | Person card |
| --- | --- |
| ![Memory wall](docs/memory-wall.png) | <img src="docs/person-card.png" alt="Person card" width="320"> |

## Research pipeline

The repository contains both the research output and the code used to collect and analyze the data:

```text
OpenStreetMap → street dataset → Wikidata/Wikipedia enrichment → manual verification → analysis → dashboard
```

Main files:

- `osm_collector.py` — Overpass API collection
- `data_collector.ipynb` — data collection and enrichment
- `analysis/analysis.ipynb` — analysis
- `analysis/build_figures.py` — reproducible chart generation
- `dashboard/` — interactive web interface
- `RESEARCH.md` — research text
- `data/novosibirsk_streets.json` — final dataset used by the dashboard

## Run locally

The dashboard is static but should be served through a local HTTP server because it loads JSON data with `fetch()`.

```bash
git clone https://github.com/ostvaldtim/city-memory-project-novosibirsk.git
cd city-memory-project-novosibirsk
python -m http.server 8080
```

Then open:

```text
http://localhost:8080/dashboard/
```

To reproduce the analysis:

```bash
pip install -r requirements.txt
jupyter notebook data_collector.ipynb
jupyter notebook analysis/analysis.ipynb
python analysis/build_figures.py
```

Map tiles and some external libraries/assets require an internet connection.

## Data and verification

Sources: OpenStreetMap, Wikidata and Wikipedia. Ambiguous commemorative street names were additionally checked manually against open and local sources.

Licensing and source attribution are documented in `ATTRIBUTION.md` and `dashboard/photos/PHOTO_CREDITS.md`.

## Authors

**Tim Ostvald** · **Artem Borisov**  
HSE University · Digital Humanities · 2026
