
#### Contains the steamlite Code 

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def tam_top_down(market_cap, cagr, years=5):
    return [market_cap * ((1 + cagr) ** t) for t in range(1, years + 1)]

def tam_bottom_up(price, adoption_rate, users):
    return price * adoption_rate * users

def scenario_builder(base_projection, optimistic_factor=1.2, conservative_factor=0.8):
    optimistic = [val * optimistic_factor for val in base_projection]
    conservative = [val * conservative_factor for val in base_projection]
    return optimistic, base_projection, conservative

def monte_carlo_sam_som(tam, sims=1000, sam_mean=0.4, sam_std=0.1, som_mean=0.25, som_std=0.08):
    sam_samples = np.random.normal(sam_mean, sam_std, sims).clip(0, 1)
    som_samples = np.random.normal(som_mean, som_std, sims).clip(0, 1)
    sam = tam * sam_samples
    som = sam * som_samples
    return sam, som

df = pd.read_csv("TaM.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
st.title(" TAM / SAM / SOM Simulator")
sector_list = df["sector"].unique()
sector = st.selectbox("Choose a Sector", sector_list)

company = df[df["sector"] == sector].iloc[0]

price = st.number_input("Price (per user/year USD)", value=float(company["avg_size"]))
adoption = st.slider("Adoption Rate (%)", 1, 100, int(company["adoption_rate"]*100)) / 100
users = st.number_input("Customer Base (users)", value=int(company["target_user"]))
cagr = st.number_input("CAGR (%)", value=float(company["cagr"]*100)) / 100
market_cap = st.number_input("Base Market Size / Cap (USD)", value=float(company["market_cap"]))
regime = st.selectbox("Macro Regime", ["Stable Growth", "High Inflation", "Recession"])
if regime == "High Inflation":
    adoption *= 0.7
elif regime == "Recession":
    market_cap *= 0.85
topdown_proj = tam_top_down(market_cap, cagr, years=5)
opt, base, cons = scenario_builder(topdown_proj)
bottomup_val = tam_bottom_up(price, adoption, users)
sam, som = monte_carlo_sam_som(bottomup_val, sims=5000)

st.subheader(f"Key Metrics for {sector}")
col1, col2, col3 = st.columns(3)
col1.metric("TAM (B USD)", round(bottomup_val/1e9, 2))
col2.metric("SAM (B USD)", round(np.mean(sam)/1e9, 2))
col3.metric("SOM (B USD)", round(np.mean(som)/1e9, 2))

st.subheader("Line Chart: TAM Projections")
years = list(range(1, len(base)+1))
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=years, y=[x/1e9 for x in base], mode="lines+markers", name="Base"))
fig1.add_trace(go.Scatter(x=years, y=[x/1e9 for x in opt], mode="lines+markers", name="Optimistic"))
fig1.add_trace(go.Scatter(x=years, y=[x/1e9 for x in cons], mode="lines+markers", name="Conservative"))
fig1.update_layout(template="plotly_white", xaxis_title="Years", yaxis_title="Market Size (B USD)")
st.plotly_chart(fig1)

st.subheader(" Funnel Chart: TAM → SAM → SOM")
values = [bottomup_val/1e9, np.mean(sam)/1e9, np.mean(som)/1e9]
labels = ["TAM", "SAM", "SOM"]
fig2 = px.funnel(y=labels, x=values, title=f"Market Funnel for {sector}")
st.plotly_chart(fig2)

st.subheader(" Heatmap: TAM / SAM / SOM Across All Sectors")
heatmap_data = []
for _, row in df.iterrows():
    bu_val = tam_bottom_up(row["avg_size"], row["adoption_rate"], row["target_user"])
    sam_, som_ = monte_carlo_sam_som(bu_val, sims=2000)
    heatmap_data.append([row["sector"], bu_val/1e9, np.mean(sam_)/1e9, np.mean(som_)/1e9])

heatmap_df = pd.DataFrame(heatmap_data, columns=["sector","TAM","SAM","SOM"])
heatmap_df.set_index("sector", inplace=True)

fig3 = px.imshow(
    heatmap_df.T,
    labels=dict(x="Sector", y="Stage", color="B USD"),
    title="TAM → SAM → SOM Heatmap",
    aspect="auto",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig3)

st.subheader(" Export Results")
csv = heatmap_df.reset_index().to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "market_sizing.csv", "text/csv")

