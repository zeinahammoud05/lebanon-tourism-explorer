# Verification results

Tested locally on 25 September 2026 with Python 3.11.6, Streamlit 1.55.0, pandas 2.3.3, and Plotly 6.6.0.

| Check | Result |
| --- | --- |
| App compilation and execution under Streamlit AppTest | Passed |
| CSV loads with 1,137 rows, 26 districts, 7 governorates | Passed |
| Missing cells and duplicate town/district/governorate records | None |
| Four establishment-type counts equal each supplied total | Passed for every row |
| Packaged CSV matches original SHA-256 | Passed; copied byte-for-byte |
| Original all-data top-12 town names and counts match bar HTML | Passed |
| Four original normalized radar polygons match HTML values | Passed within 1e-10 |
| Original four default governorates and two charts | Passed |
| Mount Lebanon limits districts to Aley, Baabda, Byblos, Chouf, Keserwan, Matn | Passed |
| Selecting Baabda changes bar chart to its expected top towns | Passed |
| Adding North retains a still-valid Baabda selection | Passed |
| Removing Mount Lebanon removes stale Baabda selection | Passed |
| Empty districts include all towns in selected governorates | Passed |
| Empty governorates disable districts and show guidance | Passed |
| Governorate changes update radar traces | Passed for one, four, and seven governorates |
| North's radar coordinates unchanged when other governorates are removed | Passed |
| All radar values agree with full-dataset mean/min–max calculation | Passed |
| Empty town view | Passed using an in-memory test-only empty subset; radar retained |
| Three insights and both interaction explanations | Verified |
| Local Streamlit HTTP server and browser rendering | Started and viewed successfully |
| Town-chart and radar labels | Visually reviewed in the browser |
| Single-governorate legend | Explicitly enabled after visual review |
| Colab notebook | Six code cells; Python source compiled locally, app cell matches final app.py |

The repeated town name Mansoura occurs in two different districts; these are distinct location records, not duplicate town/district/governorate rows. Original names and records are retained.

Actual development issues: the initial environment lacked dependencies, network restrictions blocked the first download, and an early verification attempt before installation completed raised a pandas import error. Installation in the project virtual environment and rerunning verification resolved this. Visual review found that the default Plotly legend disappeared with one trace; explicitly setting `showlegend=True` resolved this.

Not performed here: a Google Colab session, a live external Cloudflare tunnel, GitHub publication, Streamlit Community Cloud deployment, or the student's personal review. Public links and a deployed screenshot remain placeholders. No course AI-use policy was supplied.

Reproduce the main checks with `python verify_app.py`. The source-HTML comparison and forced empty-data check were additional local development checks; the original HTML files are not needed to run the app.
