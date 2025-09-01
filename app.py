import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Riyadh Urban Mobility Insights", layout="wide")

st.title("🚇 Riyadh Urban Mobility Insights")
st.markdown("Explore commute times between districts and identify traffic hotspots.")

# Load data
df = pd.read_csv("data/sample_commute.csv")

# Show table
st.subheader("Commute Data (sample)")
st.dataframe(df)

# Bar chart
fig = px.bar(df, x="origin", y="avg_minutes", color="destination",
             title="Average Commute Times (minutes)", barmode="group")
st.plotly_chart(fig, use_container_width=True)

# Simple scenario: carpooling reduces time by 10%
st.subheader("Scenario Simulation")
reduction = st.slider("Carpooling Increase (%)", 0, 50, 10, step=5)
df["reduced_minutes"] = df["avg_minutes"] * (1 - reduction/100)
fig2 = px.bar(df, x="origin", y="reduced_minutes", color="destination",
              title=f"Commute Times with {reduction}% Carpooling")
st.plotly_chart(fig2, use_container_width=True)
