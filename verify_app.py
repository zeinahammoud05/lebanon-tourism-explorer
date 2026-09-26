"""Run with python verify_app.py; no extra test packages are required."""
import json
from pathlib import Path
import py_compile

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).parent
py_compile.compile(str(ROOT / "app.py"), doraise=True)
df = pd.read_csv(ROOT / "lebanon_tourism_data.csv")
assert len(df) == 1137
assert not df.isna().any().any()
assert not df.duplicated(["town", "district", "governorate"]).any()
assert df["total_establishments"].equals(df[["cafes", "restaurants", "hotels", "guest_houses"]].sum(axis=1))
for name in ["app.py", "requirements.txt", "README.md", "lebanon_tourism_data.csv"]:
    assert (ROOT / name).is_file(), name


def charts(app):
    return [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")]


app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
assert not app.exception, app.exception
assert app.multiselect[0].value == ["Akkar", "Baalbek-Hermel", "Nabatieh", "North"]
assert len(charts(app)) == 2
original_radar = {trace["name"]: trace["r"] for trace in charts(app)[1]["data"]}
assert len(original_radar) == 4
assert any(e.label == "Why these interaction choices?" for e in app.expander)
assert sum("**" in m.value for m in app.markdown) >= 5

app.multiselect[0].set_value(["Mount Lebanon"]).run()
assert not app.exception, app.exception
expected_options = sorted(df.loc[df.governorate == "Mount Lebanon", "district"].unique())
assert app.multiselect[1].options == expected_options
assert [t["name"] for t in charts(app)[1]["data"]] == ["Mount Lebanon"]
before = charts(app)[0]
app.multiselect[1].set_value(["Baabda"]).run()
assert not app.exception, app.exception
after = charts(app)[0]
assert before != after
assert all(row[0] == "Baabda" for row in after["data"][0]["customdata"])
expected_top = df[(df.governorate == "Mount Lebanon") & (df.district == "Baabda")].nlargest(12, "total_establishments").sort_values("total_establishments")
assert list(after["data"][0]["y"]) == expected_top.town.tolist()
assert app.metric[0].value == str(len(df[df.district == "Baabda"]))

# Retain valid selections when another governorate is added.
app.multiselect[0].set_value(["Mount Lebanon", "North"]).run()
assert app.multiselect[1].value == ["Baabda"]
# Remove stale districts when their governorate is removed.
app.multiselect[0].set_value(["North"]).run()
assert not app.exception, app.exception
assert app.multiselect[1].value == []
assert app.metric[0].value == str(len(df[df.governorate == "North"]))
assert charts(app)[1]["data"][0]["r"] == original_radar["North"]

app.multiselect[0].set_value([]).run()
assert not app.exception, app.exception
assert not app.multiselect[1].options and app.multiselect[1].disabled
assert not charts(app)
assert any("Select at least one governorate" in i.value for i in app.info)
assert len(app.expander) == 1

app.multiselect[0].set_value(sorted(df.governorate.unique())).run()
assert not app.exception, app.exception
assert len(charts(app)[1]["data"]) == 7
means = df.groupby("governorate")[["tourism_index", "cafes", "restaurants", "hotels", "guest_houses"]].mean()
expected_normalized = 100 * (means - means.min()) / (means.max() - means.min()).replace(0, 1)
for trace in charts(app)[1]["data"]:
    expected = expected_normalized.loc[trace["name"]].tolist()
    assert all(abs(a - b) < 1e-10 for a, b in zip(trace["r"], expected + [expected[0]]))

print("PASS: compilation, CSV integrity, required files, charts, linked filters, stale-state cleanup, empty selections, insights, justification, and full-data radar normalization.")
