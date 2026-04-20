from src.risk_engine import compute_risk
import pandas as pd

results = []

for i in range(10):
    print(f"\n--- Scenario {i + 1} ---")
    vals = {
        "temp_c": float(input("Temperature (°C): ")),
        "rh":     float(input("Humidity (%): ")),
        "wind":   float(input("Wind (m/s): ")),
        "eu_aqi": float(input("EU AQI: ")),
        "pollen": {"grass": float(input("Grass pollen (grains/m³): "))}
    }
    n_med = int(input("Medical factors (0/1/2): "))

    out = compute_risk(vals, n_med)

    print(f"→ {out['category']} | dominant={out['dominant']} | score={out['final_score']:.2f}")

    results.append({
        "scenario": i + 1,
        "temp_c": vals["temp_c"],
        "rh": vals["rh"],
        "wind": vals["wind"],
        "eu_aqi": vals["eu_aqi"],
        "n_med": n_med,
        "dominant": out["dominant"],
        "final_score": out["final_score"],
        "category": out["category"],
    })

pd.DataFrame(results).to_csv("validation_results.csv", index=False)
print("\nSaved to validation_results.csv")
