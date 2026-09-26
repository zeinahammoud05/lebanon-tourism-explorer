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

## Reproduce in Google Colab

Upload `Colab_Workflow.ipynb` into Google Colab and execute its six code cells in order:

1. Install the pinned dependencies.
2. Upload the original CSV (names with `(1)` are accepted), inspect it, and save the canonical filename.
3. Write the complete `app.py`.
4. Write `requirements.txt`, `README.md`, and `.gitignore`.
5. Compile the app, check the data and files, and exercise linked filters with Streamlit AppTest. Download the GitHub-ready ZIP when prompted.
6. Start Streamlit with `python -m streamlit run app.py` through the runtime's Python executable and open a Cloudflare Quick Tunnel. The cell prints a clickable temporary URL. Keep the runtime running.

The temporary URL is for testing; it is not the permanent submission link. The Colab tunnel requires outbound network access and downloads Cloudflare's official Linux binary. This workflow was prepared and its Python source validated locally; an actual Google Colab runtime and external tunnel still need your live test.

## Push to GitHub

Create an empty repository on GitHub. Upload these files to its root using **Add file → Upload files**, or run the commands below in this folder (replace the example URL):

```bash
git init
git add app.py requirements.txt lebanon_tourism_data.csv README.md .gitignore verify_app.py
git commit -m "Add Lebanon tourism Streamlit assignment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/lebanon-tourism-explorer.git
git push -u origin main
```

You may also upload `Colab_Workflow.ipynb` for reproducibility. No repository has been created or pushed automatically. Keep the submission report outside the public repository unless your instructor requests it.

## Deploy to Streamlit Community Cloud

Sign in at [Streamlit Community Cloud](https://share.streamlit.io/), connect GitHub, and choose **Create app**. Select your repository, `main` branch, and `app.py` as the main file. Under advanced settings select Python 3.11, then deploy. Dependencies are read from `requirements.txt`. Copy the actual public URL into this README and the Moodle report after deployment, test both filters, and capture the deployed page.

References: [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), [Cloudflare Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).

## Verification

```bash
python verify_app.py
```

This checks compilation, data integrity, default charts, dependent district options, district filtering, removal of stale selections, empty selections, radar trace updates, and stable normalization. The original delivered project also includes `Verification.md` with local development results.

Manual demonstration: select Mount Lebanon, inspect its available districts, choose Baabda, then clear districts. Next select North and compare the radar. Finally clear all governorates and confirm the guidance message.

## Submission and AI disclosure

Use the separate `Moodle_Report.txt` as paste-ready report text. Fill in your name, real links, screenshot, and only the personal review/testing actions you actually complete. Codex/ChatGPT assisted with code, charts, filters, testing, troubleshooting, and documentation. No course AI-policy document was supplied; adapt the disclosure to your instructor's requirements.
