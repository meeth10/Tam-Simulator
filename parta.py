import pandas as pd 

df = pd.read_csv("TaM.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(df.columns)
print(df)

def tam_top_down(market_cap, cagr, years=5):
    tam = [market_cap * ((1 + cagr) ** t) for t in range(1, years + 1)]
    return tam

def tam_bottom_up(price, adoption_rate, users):
    tam = price * adoption_rate * users
    return tam

def scenario_builder(base_projection, optimistic_factor=1.2, conservative_factor=0.8):
    optimistic = [val * optimistic_factor for val in base_projection]
    conservative = [val * conservative_factor for val in base_projection]
    return optimistic, base_projection, conservative

results = []

for _, company in df.iterrows():
    topdown_proj = tam_top_down(company["market_cap"], company["cagr"], years=5)
    bottomup_val = tam_bottom_up(company["avg_size"], company["adoption_rate"], company["target_user"])
    optimistic, base, conservative = scenario_builder(topdown_proj)
    results.append({
        "sector": company["sector"],
        "bottom_up_TAM": round(bottomup_val/1e9, 2),
        "top_down_TAM_Yr5": round(topdown_proj[-1]/1e9, 2),
        "optimistic_Yr5": round(optimistic[-1]/1e9, 2),
        "conservative_Yr5": round(conservative[-1]/1e9, 2) 
    })
summary_df = pd.DataFrame(results)
print(summary_df)

