# Water Loss Financial Impact Engine 💧
### A bilingual (Arabic / English) water-loss analytics dashboard

> A showcase project prepared for **Abunayyan Holding**, built around the
> company's core water business (Abunayyan Trading, **Saudi Meters**, **WETICO**)
> rather than as a generic data-science demo.

**🔗 Live demo:** https://incredible-malasada-3fccf0.netlify.app
_(Redeploy the latest `index.html` to Netlify / GitHub Pages so the link shows the current version: 3 tabs, bilingual, updated data.)_

<!-- Add a screenshot named preview.png, then uncomment: -->
<!-- ![preview](preview.png) -->

## What it is

A single, self-contained web page (`index.html`) with **three tabs**, fully
offline-capable and **bilingual** (an «English / العربية» switch that flips the
whole interface between LTR and RTL at runtime):

- **National Gap** — **officially published real data**: the water-consumption
  gap between Saudi regions and the Vision 2030 target, and its illustrative
  economic value at the official tariff.
- **Leak Detection** — an engine that builds a per-site baseline, flags
  anomalies (statistically **and** economically), converts each into a **SAR
  loss**, and projects the next 30 days of loss if a leak is left untreated
  (on simulated meter data).
- **Network Simulation** — a modeled slice of Riyadh (source → pumps → District
  Metered Areas → a meter per home) grounded in the real studies. It applies the
  **water balance** to detect and localize losses to a district, and shows the
  **path to Vision 2030** plus a sample sensor feed.

**Tech:** Python (pandas / numpy) for the analysis, Streamlit for the interactive
dashboards, and a self-contained HTML / JS + Chart.js page for deployment — with
no external cloud dependency at runtime.

## ⚠️ Two clearly separated layers

The project is deliberately split so no number is mistaken for something it isn't:

1. **Real layer** (`real_data.py`, `real_analysis.py`, `real_dashboard.py`) —
   100% officially published data: the 2022 census, real per-capita consumption
   per region, the official tariff tiers, and the declared national network loss.
   **This is the layer to present to the company.** Run: `streamlit run real_dashboard.py`.
2. **Engine layer** (`generate_data.py`, `analysis.py`, `dashboard.py`) — a
   meter-level anomaly-detection algorithm **tested on simulated data**, because
   real per-meter telemetry isn't available as open data in Saudi Arabia yet. The
   code is engineering-ready but **does not represent real results** — it must not
   be presented as such. See `PRESENTATION_NOTES.md`.

> **Unified site (`index.html`):** both layers plus the network simulation are
> merged into **one bilingual page** with three tabs (no duplication), built from
> `site_template.html` via `python build_html.py`, and it runs with no internet
> (Chart.js is inlined). This page is the one to host on GitHub Pages. The
> Streamlit dashboards are the interactive local version — they can't run on
> GitHub Pages because they need a Python server.

## Methodology (brief)

1. **Baseline:** a trailing, backward-looking rolling-median per site — it only
   ever sees the past, exactly as a live on-premise monitor would.
2. **Anomaly detection:** a day is flagged as a probable leak only when it is
   both a statistical outlier (a robust, MAD-based z-score that a sustained leak
   can't suppress) **and** economically significant (more than 15% over baseline)
   — which cuts false alarms.
3. **Financial conversion:** excess volume × each site's water tariff (SAR/m³) =
   daily loss, summed to monthly / annual.
4. **Projection:** if a leak is active in the final days of the data, project the
   additional loss over the next 30 days if it stays unresolved.

Precision / Recall are **computed live** in `evaluate.py` (never hardcoded):
currently ~100% precision / ~69% recall on the simulated data — these will change
on real, noisier data. Run `python evaluate.py` to see the current values.

## Project structure

```
├── generate_data.py            # dynamic simulated data for the last 90 days ending today
├── analysis.py                 # engine: baseline + anomaly detection + SAR conversion + 30-day projection (writes dashboard_data.json)
├── evaluate.py                 # Precision/Recall vs. ground truth (computed, not hardcoded)
├── real_data.py / real_analysis.py     # real published data + analysis (writes real_dashboard_data.json)
├── generate_network_data.py    # simulates source→pumps→DMAs→home-meters + water balance (writes network_data.json)
├── dashboard.py / real_dashboard.py    # two interactive Streamlit dashboards — bilingual
├── i18n.py                     # shared translations + language switch + RTL/LTR for the Streamlit apps
├── site_template.html          # template for the unified site (3 tabs, bilingual)
├── build_html.py               # builds the unified index.html from the template + the 3 JSON files
├── index.html                  # the ready unified site (host on GitHub Pages)
├── export_powerbi.py           # exports clean CSVs to powerbi/ for Power BI import
├── powerbi/                    # CSV files (UTF-8) + a Power BI import guide
├── vendor/chart.umd.min.js     # Chart.js locally (no CDN) so it runs with no internet
└── requirements.txt / Dockerfile / .nojekyll
```

## Run

> **On Windows use `py` instead of `python`** (a bare `python` may open the Microsoft Store).

```bash
pip install -r requirements.txt
python generate_data.py           # simulated data for the last 90 days ending today
python analysis.py                # loss summary + 30-day projection (+ dashboard_data.json)
python real_analysis.py           # builds the real-layer data (real_dashboard_data.json)
python generate_network_data.py   # builds the network-simulation data (network_data.json)
python evaluate.py                # evaluates the model (real Precision/Recall)
python build_html.py              # builds the unified index.html (3 tabs)
streamlit run real_dashboard.py   # the interactive dashboard at http://localhost:8501
```

To view the unified site: open `index.html` directly, or serve it with `python -m http.server`.

## Deploy to GitHub Pages

`index.html` is a static, self-contained page, so it hosts for free on GitHub Pages:

1. In the repo: **Settings → Pages → Source = branch `main`, folder `/root`** → Save.
2. You get a link like `https://<username>.github.io/<repo>/`.

The Streamlit apps can't run on GitHub Pages (they need a Python server) — use the free **Streamlit Community Cloud** for those.

## Power BI

There is no Python library that renders data inside Power BI without an account /
license. The practical path is importing clean CSVs:

```bash
python export_powerbi.py     # writes UTF-8 CSVs into powerbi/
```

Then in Power BI Desktop: **Get Data → Text/CSV** and import the `powerbi/` files
(a bilingual guide is in `powerbi/HOW_TO_IMPORT.md`).

---
*Prepared by Mubarak Almudarra — Computer Science (Artificial Intelligence) graduate.*
*GitHub: [github.com/MubarkALmudarra](https://github.com/MubarkALmudarra)*
