# ESPEN–CIFF PCT Progress Indicators Dashboard

A web-based, shareable dashboard for monitoring Preventive Chemotherapy (PCT)
NTD programme progress across the WHO African Region (AFRO).

Built in collaboration between **ESPEN** (Expanded Special Project for the
Elimination of NTDs) and **CIFF** (Children's Investment Fund Foundation).

---

## Dashboard Structure

| Tab | Content |
|-----|---------|
| **WHO AFRO Region** | Aggregated indicators for all 47 AFRO Member States, filterable by year |
| **Lymphatic Filariasis** | Country-level indicators for LF, year & country filters |
| **Onchocerciasis** | Country-level indicators for ONC, year & country filters |
| **STH** | Country-level indicators for soil-transmitted helminthiases |
| **Schistosomiasis** | Country-level indicators for SCH |
| **Trachoma** | Country-level indicators for TRA |
| **Elimination Map** | Choropleth map of ESPEN Performance Scores (Ind. 36–39) |

Each disease tab includes, at the bottom:
- **Cross-cutting indicators** – Ind. 33 (Integrated Treatment Coverage Index)
  and Ind. 35 (Number of eliminated PC-NTDs)
- **NTD System Integration** – Q1, Q2, Q3 responses for 2024 and 2025

---

## Data Sources

| File | Description |
|------|-------------|
| `PCT_Indicators_CIFF_<date>.xlsx` | Main country- and AFRO-level indicators |
| `NTD_System_Integration.xlsx` | System integration questionnaire responses (Q1–Q3) |

---

## Deployment

### GitHub Pages (recommended — shareable URL)

1. Push this repository to GitHub (see below).
2. Go to **Settings → Pages → Source**: set to `GitHub Actions`.
3. The `deploy.yml` workflow will publish the site automatically on every push
   to `main`. The URL will be:
   `https://<your-org>.github.io/ESPEN-CIFF-Progress-Indicators/`

### Local preview

The dashboard loads data via `fetch()`, which requires a web server:

```bash
# Python (from the repo root)
python -m http.server 8000
# Then open: http://localhost:8000
```

> **Note:** Opening `index.html` directly (`file://`) will fail due to
> browser CORS restrictions on local file fetches.

---

## Updating with New Data

When new annual data become available:

1. Replace or add the updated Excel files to the `data-sources/` directory.
2. Run the data preparation script:

```bash
pip install pandas openpyxl
python prepare_data.py --src-dir data-sources/ --out-dir data/
```

3. Commit and push:

```bash
git add data/*.json
git commit -m "Update PCT indicators – <year>"
git push
```

GitHub Pages will redeploy automatically.

---

## Repository Structure

```
ESPEN-CIFF-Progress-Indicators/
│
├── index.html              Main dashboard (single-page application)
├── prepare_data.py         Data preparation script (Excel → JSON)
│
├── data/
│   ├── country_indicators.json     Country-level indicator data
│   ├── afro_indicators.json        WHO AFRO aggregated indicators
│   ├── system_integration.json     NTD system integration responses
│   └── dictionaries.json           Indicator label definitions
│
├── assets/
│   ├── CIFF.png            CIFF institutional logo
│   └── ESPEN-Bleu.png      ESPEN institutional logo
│
├── data-sources/           (place source Excel files here for updates)
│
└── .github/
    └── workflows/
        └── deploy.yml      Automatic GitHub Pages deployment
```

---

## Technical Notes

- The dashboard is a **static single-page application** — no server-side
  processing required after deployment.
- Libraries loaded from CDN: Bootstrap 5.3, Chart.js 4.4, Leaflet 1.9,
  topojson-client 3.1.
- The choropleth map uses the Natural Earth 110m world dataset
  (via [world-atlas@2](https://github.com/topojson/world-atlas)) filtered to
  African countries.
- Population-scale indicators (Ind. 1, 5, 6, 10, 13, 14, 17, 18, 21, 22) are
  displayed in units of ×1,000 throughout.
- Missing values are displayed as **N/A**.

---

*ESPEN — WHO Regional Office for Africa | Last updated: April 2026*
