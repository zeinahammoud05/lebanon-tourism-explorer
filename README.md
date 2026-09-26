# Lebanon Tourism Explorer

A single-page Streamlit assignment exploring tourism establishments in Lebanese towns. It rebuilds two charts from the supplied Plotly assignment as interactive Plotly figures.

Public Streamlit app: **[Insert public URL after deployment]**

## Visualizations and linked interactions

1. **Top towns:** up to 12 towns by `total_establishments`, shown as horizontal bars colored by `tourism_index` using the original Tealgrn palette. Hover shows district, governorate, index, the four establishment types, and total.
2. **Governorate profiles:** filled radar polygons for Tourism Index, Cafés, Restaurants, Hotels, and Guest houses. Each metric is the mean across a governorate's recorded towns.

The governorate multiselect changes both the radar traces and the district options. The district multiselect then filters the town ranking, metrics, and town/district insights. This is a **Governorate → District → Town** drill-down. The radar retains whole-governorate context.

An empty district selection means all districts in the selected governorates. Invalid district selections are removed before the district widget is rendered. Clearing all governorates shows guidance and disables districts.

The original radar defaults are preserved: Akkar, Baalbek-Hermel, Nabatieh, and North. Three dynamic insights identify the leading town, district, and governorate average. An expander explains the interaction choices.

## Dataset and normalization

`lebanon_tourism_data.csv` is copied unchanged from the supplied assignment. It has 1,137 town records, 26 districts, and 7 governorates. Beirut is absent. Fields include location, Tourism Index, cafés, restaurants, hotels, guest houses, total establishments, attraction flag, tourism group, and an observation identifier. Observation identifiers point to AUB-linked CODEC Tourism records; the supplied CSV is the data source used here. No observation date, index formula, or source license was supplied.

Inspection found no missing cells or duplicate town/district/governorate records. All supplied totals equal the sum of the four establishment types. Numeric fields are converted with `pd.to_numeric(errors="coerce")`; invalid required values produce a clear message instead of being silently replaced with zeros. Original totals and names are retained.

The original notebook and radar HTML agree on this method:

```text
governorate mean = mean of each metric across recorded towns
normalized score = 100 × (governorate mean − full-data minimum mean)
                         / (full-data maximum mean − full-data minimum mean)
```

Minima and maxima are calculated across **all seven governorates before filtering**, separately for each metric. A constant metric is assigned zero by replacing a zero denominator with one. A normalized score of zero means the lowest governorate mean; it does not necessarily mean no establishments. Radar hover includes the unscaled means. The bar color scale is also fixed to the dataset's 0–10 index range.

Establishment counts are not visitor totals or population-adjusted tourism intensity. District totals can be higher because more towns are recorded. Ranking ties at the 12-town cutoff retain CSV order.

## Run locally

Use Python 3.11 (the tested version) in a terminal opened in this folder:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux instead: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Keep `app.py`, `requirements.txt`, and the CSV together. The CSV path is resolved relative to the app, so launch location does not affect loading.

## Option 2: Reproduce in Google Colab

Upload `Colab_Workflow.ipynb` into Google Colab and execute its six code cells in order:

1. Install the pinned dependencies.
2. Upload the original CSV (names with `(1)` are accepted), inspect it, and save the canonical filename.
3. A Streamlit dashboard is the output of cell 6.

