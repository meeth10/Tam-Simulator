
### BAsic code to run tam , sam , som 
## Edit the csv file values to your needs 

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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

def plot_line_chart(sector, base, optimistic, conservative):
    years = list(range(1, len(base) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=[x/1e9 for x in base], mode="lines+markers", name="Base"))
    fig.add_trace(go.Scatter(x=years, y=[x/1e9 for x in optimistic], mode="lines+markers", name="Optimistic"))
    fig.add_trace(go.Scatter(x=years, y=[x/1e9 for x in conservative], mode="lines+markers", name="Conservative"))
    fig.update_layout(title=f"TAM Projections for {sector}",
                      xaxis_title="Years", yaxis_title="Market Size (B USD)",
                      template="plotly_white")
    fig.show()

def plot_funnel(sector, tam, sam, som):
    values = [tam/1e9, np.mean(sam)/1e9, np.mean(som)/1e9]
    labels = ["TAM", "SAM", "SOM"]
    fig = px.funnel(y=labels, x=values, title=f"Market Funnel for {sector}")
    fig.update_layout(template="plotly_white")
    fig.show()

def plot_heatmap(summary_df):
    heatmap_df = summary_df.set_index("sector")[["bottom_up_TAM_BUSD","mean_SAM_BUSD","mean_SOM_BUSD"]]
    fig = px.imshow(
        heatmap_df.T,
        labels=dict(x="Sector", y="Stage", color="B USD"),
        title="TAM → SAM → SOM Heatmap Across Sectors",
        aspect="auto",
        color_continuous_scale="Blues"
    )
    fig.show()

df = pd.read_csv("TaM.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
results = []

for _, row in df.iterrows():
    topdown_proj = tam_top_down(row["market_cap"], row["cagr"], years=5)
    opt, base, cons = scenario_builder(topdown_proj)
    bottomup_val = tam_bottom_up(row["avg_size"], row["adoption_rate"], row["target_user"])
    sam, som = monte_carlo_sam_som(bottomup_val, sims=5000)
    
    results.append({
        "sector": row["sector"],
        "bottom_up_TAM_BUSD": round(bottomup_val/1e9, 2),
        "top_down_TAM_Yr5_BUSD": round(topdown_proj[-1]/1e9, 2),
        "optimistic_Yr5_BUSD": round(opt[-1]/1e9, 2),
        "conservative_Yr5_BUSD": round(cons[-1]/1e9, 2),
        "mean_SAM_BUSD": round(np.mean(sam)/1e9, 2),
        "mean_SOM_BUSD": round(np.mean(som)/1e9, 2),
        "top_down_path_BUSD": [round(x/1e9, 2) for x in topdown_proj]
    })

summary_df = pd.DataFrame(results)
print(summary_df)

company = df[df["sector"] == "Gaming"].iloc[0]
topdown_proj = tam_top_down(company["market_cap"], company["cagr"], years=5)
opt, base, cons = scenario_builder(topdown_proj)
bottomup_val = tam_bottom_up(company["avg_size"], company["adoption_rate"], company["target_user"])
sam, som = monte_carlo_sam_som(bottomup_val, sims=5000)

plot_line_chart(company["sector"], base, opt, cons)
plot_funnel(company["sector"], bottomup_val, sam, som)
plot_heatmap(summary_df)

