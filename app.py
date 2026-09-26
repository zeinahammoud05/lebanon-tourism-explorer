from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# Page setup
st.set_page_config(page_title="Lebanon Tourism Explorer", page_icon="🇱🇧", layout="wide")
st.title("🇱🇧 Lebanon Tourism Explorer")
st.write(
    "Explore where tourism establishments are concentrated in the supplied Lebanon "
    "dataset. Compare governorate profiles, then narrow the town ranking by district. "
    "Each row represents a town and records its Tourism Index and numbers of cafés, "
    "restaurants, hotels, and guest houses."
)

# Load data. Keep the supplied totals and original town names.
data_path = Path(__file__).parent / "lebanon_tourism_data.csv"
try:
    df = pd.read_csv(data_path)
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
    st.error(f"Could not read lebanon_tourism_data.csv. Place it beside app.py. Details: {error}")
    st.stop()

metrics = ["tourism_index", "cafes", "restaurants", "hotels", "guest_houses"]
metric_labels = ["Tourism Index", "Cafés", "Restaurants", "Hotels", "Guest houses"]
numeric_columns = metrics + ["total_establishments"]
required_columns = ["town", "district", "governorate"] + numeric_columns
missing_columns = sorted(set(required_columns) - set(df.columns))
if missing_columns:
    st.error("The CSV is missing required columns: " + ", ".join(missing_columns))
    st.stop()
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
if df.empty or df[required_columns].isna().any().any():
    st.error("The dataset is empty or contains missing/invalid required values. Check the CSV; unknown values are not treated as zero.")
    st.stop()

# Full-dataset reference: calculated BEFORE either filter is applied.
# Preserve the original notebook's mean-per-town and min–max normalization.
governorate_averages = df.groupby("governorate")[metrics].mean()
metric_min = governorate_averages.min()
metric_ranges = (governorate_averages.max() - metric_min).replace(0, 1)
normalized = (governorate_averages - metric_min).div(metric_ranges).mul(100)
all_governorates = sorted(governorate_averages.index.tolist())
default_governorates = ["Akkar", "Baalbek-Hermel", "Nabatieh", "North"]

# Interactions: Governorate → District → Town
st.sidebar.header("Explore by area")
selected_governorates = st.sidebar.multiselect(
    "1. Governorates to compare",
    options=all_governorates,
    default=[g for g in default_governorates if g in all_governorates],
    key="governorates",
    help="Updates the radar chart and the available districts below.",
)
governorate_rows = df[df["governorate"].isin(selected_governorates)]
district_options = sorted(governorate_rows["district"].unique().tolist())

# Remove invalid selections BEFORE creating the dependent district widget.
previous_districts = st.session_state.get("districts", [])
st.session_state["districts"] = [d for d in previous_districts if d in district_options]
selected_districts = st.sidebar.multiselect(
    "2. Districts to examine",
    options=district_options,
    key="districts",
    disabled=not selected_governorates,
    placeholder="All available districts",
    help="Leave empty to include all districts in the selected governorates.",
)
st.sidebar.caption("Governorate → District → Town")
st.sidebar.caption("An empty district selection includes all available districts. The radar always compares whole governorates.")

# Filtering
filtered = governorate_rows.copy()
if selected_districts:
    filtered = filtered[filtered["district"].isin(selected_districts)]

if not selected_governorates:
    st.info("Select at least one governorate in the sidebar to explore its towns and tourism profile.")
else:
    st.caption("Town view: " + ", ".join(selected_governorates) + " · " +
               (", ".join(selected_districts) if selected_districts else "All available districts"))
    col1, col2, col3 = st.columns(3)
    col1.metric("Towns in view", f"{len(filtered):,}")
    col2.metric("Establishments in view", f"{filtered['total_establishments'].sum():,.0f}")
    col3.metric("Average town Tourism Index", f"{filtered['tourism_index'].mean():.2f}" if not filtered.empty else "—")

    # Chart 1: Top towns by total establishments
    st.subheader("Where are tourism establishments concentrated?")
    if filtered.empty:
        st.info("No town records match this selection. Choose another district or clear the district filter.")
    else:
        top_towns = filtered.nlargest(12, "total_establishments").sort_values("total_establishments")
        bar = px.bar(
            top_towns,
            x="total_establishments",
            y="town",
            orientation="h",
            color="tourism_index",
            color_continuous_scale="Tealgrn",
            range_color=[df["tourism_index"].min(), df["tourism_index"].max()],
            text="total_establishments",
            labels={"town": "Town", "total_establishments": "Total tourism establishments",
                    "tourism_index": "Tourism Index", "district": "District",
                    "governorate": "Governorate", "cafes": "Cafés", "restaurants": "Restaurants",
                    "hotels": "Hotels", "guest_houses": "Guest houses"},
            hover_data=["district", "governorate", "cafes", "restaurants", "hotels", "guest_houses"],
            title=f"Top {len(top_towns)} towns by number of tourism establishments",
        )
        bar.update_traces(textposition="outside", cliponaxis=False)
        bar.update_layout(template="plotly_white", height=560, margin=dict(l=10, r=40, t=65, b=45))
        bar.update_yaxes(categoryorder="array", categoryarray=top_towns["town"].tolist(), automargin=True)
        bar.update_xaxes(range=[0, max(1, top_towns["total_establishments"].max() * 1.16)])
        st.plotly_chart(bar, width="stretch", key="town_bar")
        st.caption("Counts and bar colors come directly from the CSV. Hover for establishment types and location. Ties at the top-12 cutoff follow CSV row order.")

    # Chart 2: Governorate profiles on a stable common scale
    st.subheader("How do the selected governorates compare?")
    st.caption("Whole-governorate averages per town. District selections affect the town view only.")
    radar = go.Figure()
    palette = px.colors.qualitative.Plotly
    for governorate in selected_governorates:
        values = normalized.loc[governorate].tolist()
        raw_values = governorate_averages.loc[governorate].tolist()
        radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=metric_labels + [metric_labels[0]],
            customdata=raw_values + [raw_values[0]],
            fill="toself",
            name=governorate,
            opacity=0.55,
            line=dict(color=palette[all_governorates.index(governorate) % len(palette)]),
            hovertemplate="%{theta}<br>Normalized: %{r:.1f}/100<br>Raw mean per town: %{customdata:.2f}<extra>%{fullData.name}</extra>",
        ))
    radar.update_layout(
        title="Selected governorates have different tourism profiles",
        template="plotly_white",
        height=570,
        showlegend=True,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], dtick=25)),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        margin=dict(l=65, r=65, t=75, b=90),
    )
    st.plotly_chart(radar, width="stretch", key="governorate_radar")
    st.caption(
        "For each measure: 100 × (governorate mean − lowest governorate mean) ÷ "
        "(highest − lowest governorate mean), using all seven governorates in the CSV. "
        "0 means the lowest average, not necessarily zero establishments; 100 means the highest. "
        "A measure identical across all governorates is shown as 0. The reference stays fixed when filters change."
    )

    # Insights: compute from the current selection, with explicit scope.
    st.subheader("Key insights")
    if not filtered.empty:
        largest = filtered["total_establishments"].max()
        leaders = filtered[filtered["total_establishments"] == largest]
        leader_names = "; ".join(leaders["town"] + " (" + leaders["district"] + ")")
        st.markdown(f"**Town concentration:** The highest town count is **{largest:,.0f} establishments**, recorded in {leader_names}.")
        district_totals = filtered.groupby("district")["total_establishments"].sum()
        strongest = district_totals[district_totals == district_totals.max()]
        st.markdown(f"**District concentration:** The highest district total is **{strongest.iloc[0]:,.0f} establishments**, recorded in {', '.join(strongest.index)}. Districts with more recorded towns can rank higher because these are totals.")
    selected_means = governorate_averages.loc[selected_governorates, "tourism_index"]
    highest = selected_means[selected_means == selected_means.max()]
    st.markdown(f"**Governorate profile:** {', '.join(highest.index)} has the highest average Tourism Index among the selected governorates: **{highest.iloc[0]:.2f}**. This uses all recorded towns in each selected governorate.")

# Design justification remains visible even when no governorate is selected.
with st.expander("Why these interaction choices?"):
    st.markdown("**Interaction 1 – Governorate Multiselect**")
    st.write(
        'This control answers, “Which governorates do I want to compare?” A multiselect '
        "lets the reader place several profiles on the same radar chart. A single dropdown "
        "would require remembering one profile while viewing another. Choosing a smaller "
        "set focuses attention and reduces overlapping shapes, while the fixed scale keeps "
        "the wider dataset as context. The same choice also controls which districts are available."
    )
    st.markdown("**Interaction 2 – District Multiselect**")
    st.write(
        'This control answers, “Within the selected governorates, which districts do I want '
        'to examine?” A multiselect supports comparing towns across one or several districts. '
        "Showing every district in Lebanon would add irrelevant choices and could create "
        "confusing combinations. Limiting the options to the selected governorates creates "
        "a Governorate → District → Town drill-down, reduces clutter, and focuses attention "
        "on a meaningful subset. Leaving it empty gives an overview of all available districts."
    )

# Data source and interpretation
st.caption(
    "Source: the supplied lebanon_tourism_data.csv from the original Plotly assignment; "
    "its observation column contains AUB-linked CODEC Tourism identifiers. "
    "Coverage: 1,137 town records, 26 districts, 7 governorates; Beirut is not included. "
    "The CSV provides no observation date or Tourism Index formula. Counts describe the supplied "
    "records, not visitor numbers or a current tourism census."
)
