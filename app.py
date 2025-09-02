import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Optional map libraries
try:
    from streamlit_folium import st_folium
    import folium
    HAS_MAP = True
except Exception:
    HAS_MAP = False

# Page setup
st.set_page_config(page_title="Riyadh Urban Mobility Insights", layout="wide")
st.title("🚇 Riyadh Urban Mobility Insights")
st.markdown("Explore commute times between districts, identify hotspots, and test what-if scenarios (carpooling / metro).")

# Data loading
DATA_PATH = "data/sample_commute.csv"
GEO_PATH = "data/geo_commute.csv"

def load_commute(path: str) -> pd.DataFrame:
    """Load commute data from CSV or provide fallback sample data."""
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        # fallback sample data (used if no CSV available)
        df = pd.DataFrame({
            "origin": ["Olaya","Olaya","Diriyah","Malaz","Malaz","King Fahd","Airport"],
            "destination": ["King Fahd","Diriyah","King Fahd","Olaya","Diriyah","Airport","Olaya"],
            "avg_minutes": [35,25,30,40,38,50,55]
        })

    # basic cleanup
    df = df.dropna()
    df["origin"] = df["origin"].astype(str)
    df["destination"] = df["destination"].astype(str)
    df["avg_minutes"] = df["avg_minutes"].astype(float)
    return df

def load_geo(path: str) -> pd.DataFrame:
    """Load geographic commute data (lat/lon for mapping)."""
    if os.path.exists(path):
        gdf = pd.read_csv(path)
    else:
        # fallback map data
        gdf = pd.DataFrame({
            "lat":[24.7136,24.7500,24.7440,24.6869,24.9578],
            "lon":[46.6753,46.6100,46.5760,46.7229,46.6981],
            "avg_minutes":[42,38,30,40,50],
            "label":["Olaya","King Fahd","Diriyah","Malaz","Airport"]
        })
    return gdf

df = load_commute(DATA_PATH)
gdf = load_geo(GEO_PATH)

# Sidebar controls
st.sidebar.header("Filters")
districts = sorted(set(df["origin"]).union(set(df["destination"])))
selected = st.sidebar.multiselect("Districts", districts, default=districts)
carpool_pct = st.sidebar.slider("Carpooling increase (%)", 0, 50, 10, step=5)
metro_pct = st.sidebar.slider("Metro adoption impact (%)", 0, 30, 5, step=5)
show_table = st.sidebar.checkbox("Show raw table", value=False)

# Data filtering
st.subheader("Commute Data (sample)")
st.dataframe(df)

filt = df[df["origin"].isin(selected) & df["destination"].isin(selected)].copy()

# KPI metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Routes", len(filt))
col2.metric("Avg minutes", f"{filt['avg_minutes'].mean():.1f}" if len(filt) else "—")
col3.metric("Max minutes", f"{filt['avg_minutes'].max():.0f}" if len(filt) else "—")

# apply carpool + metro impact sequentially (not additive)
scenario_minutes = filt["avg_minutes"] * (1 - carpool_pct/100)
scenario_minutes = scenario_minutes * (1 - metro_pct/100)
improvement = (filt["avg_minutes"].mean() - scenario_minutes.mean()) if len(filt) else 0
col4.metric("Scenario improvement", f"{improvement:.1f} min")

# Charts
st.subheader("Average Commute Times")
if len(filt):
    fig = px.bar(
        filt,
        x="origin",
        y="avg_minutes",
        color="destination",
        barmode="group",
        title="Average minutes by route"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No routes match the current filters.")

# Scenario comparison (current vs. adjusted)
if len(filt):
    comp = filt.copy()
    comp["scenario_minutes"] = scenario_minutes.values
    c1, c2 = st.columns(2)
    with c1:
        fig2 = px.bar(
            comp,
            x="origin",
            y="avg_minutes",
            color="destination",
            barmode="group",
            title="Current"
        )
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        fig3 = px.bar(
            comp,
            x="origin",
            y="scenario_minutes",
            color="destination",
            barmode="group",
            title=f"Scenario: +{carpool_pct}% carpool, +{metro_pct}% metro"
        )
        st.plotly_chart(fig3, use_container_width=True)

# Raw data table (optional)
if show_table:
    st.subheader("Raw Data (filtered)")
    st.dataframe(filt)

# Hotspot map
st.subheader("Traffic Hotspot Map (sample data)")
if HAS_MAP:
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=11)
    for _, r in gdf.iterrows():
        folium.CircleMarker(
            location=[float(r["lat"]), float(r["lon"])],
            radius=max(4, float(r["avg_minutes"]) / 2),
            tooltip=f'{r["label"]}: {int(r["avg_minutes"])} min',
            fill=True,
        ).add_to(m)
    st_folium(m, height=520, width=None)
else:
    st.warning("Map libraries not installed. Add `folium` and `streamlit-folium` to requirements.txt to enable the map.")

# Insights
st.markdown("### Key Insights (auto-generated from current view)")
if len(filt):
    worst = filt.sort_values("avg_minutes", ascending=False).head(3)
    st.write("- Top congested routes right now:")
    for _, r in worst.iterrows():
        st.write(f"  • {r['origin']} → {r['destination']}: {int(r['avg_minutes'])} min")
    st.write(f"- With the scenario sliders, avg route time improves by ~{improvement:.1f} min.")
else:
    st.write("- Adjust filters to see insights.")

st.caption("Data shown here is sample/simulated. Replace with live sources when available.")
