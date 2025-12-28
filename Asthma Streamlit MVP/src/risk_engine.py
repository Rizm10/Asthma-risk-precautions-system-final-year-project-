import numpy as np

weights = {
    "pollution": 1.0,
      "temp": 0.8,
    "pollen": 0.7,
    "humidity": 0.5,
    "wind": 0.4,
}

def risk_band(score_0_10: float) -> str:
    if score_0_10 < 3.0:
        return "low:"
    
    elif score_0_10 < 6.0:
        return "moderate"
    
    return "high"

def medical_applifier(n_factors: int) -> float:
    if n_factors <= 0:
        return 1.0
    if n_factors == 1:
        return 1.2
    return 1.4

# --- Sub-indices (0–10 style, but you use bucket values which is fine) ---
def temp_index_c(t: float | None) -> int:
    if t is None:
        return 3
    t = float(t)
    if 10 <= t <= 20:
        return 1
    if 5 <= t < 10 or 20 < t <= 25:
        return 3
    if 0 <= t < 5 or 25 < t <= 30:
        return 6
    return 9


def humidity_index(rh: float | None) -> int:
    if rh is None:
        return 3
    rh = float(rh)
    if 40 <= rh <= 60:
        return 1
    if 30 <= rh < 40 or 60 < rh <= 70:
        return 3
    if 20 <= rh < 30 or 70 < rh <= 80:
        return 6
    return 9


def wind_index_ms(w: float | None) -> int:
    # wind_speed_10m from Open-Meteo is typically m/s.
    # Higher wind can disperse pollution, so lower risk at higher wind.
    if w is None:
        return 3
    w = float(w)
    if w > 6:
        return 1
    if 4 < w <= 6:
        return 3
    if 2 < w <= 4:
        return 6
    return 9


def eu_aqi_to_0_10(eu_aqi: float | None) -> int:
    # European AQI is commonly 1–5 (sometimes 0–100 depending on endpoint).
    # This mapping is intentionally conservative + clipped.
    if eu_aqi is None:
        return 3
    x = float(eu_aqi)

    # If it's the 1–5 style, scale it.
    if 0 < x <= 5:
        return int(np.clip(np.ceil((x / 5.0) * 10.0), 1, 10))

    # Otherwise assume 0–100-ish and scale.
    return int(np.clip(np.ceil((x / 100.0) * 10.0), 1, 10))


def pollen_subindex(pollen_dict: dict | None) -> int:
    # Open-Meteo pollen values can be None. We filter properly.
    if not pollen_dict:
        return 2  # mild default

    vals = []
    for v in pollen_dict.values():
        if v is None:
            continue
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            continue

    if not vals:
        return 2

    m = max(vals)
    if m <= 10:
        return 2
    if m <= 50:
        return 4
    if m <= 100:
        return 7
    return 9


def weighted_dominance(sub_idx: dict) -> tuple[float, str, dict]:
    weighted = {k: weights[k] * sub_idx[k] for k in sub_idx.keys()}
    dominant = max(weighted, key=weighted.get)
    base_score = float(weighted[dominant])
    return base_score, dominant, weighted


def compute_risk(vals: dict, n_med_factors: int) -> dict:
    sub = {
        "pollution": eu_aqi_to_0_10(vals.get("eu_aqi")),
        "temp": temp_index_c(vals.get("temp_c")),
        "humidity": humidity_index(vals.get("rh")),
        "wind": wind_index_ms(vals.get("wind")),
        "pollen": pollen_subindex(vals.get("pollen")),
    }

    base_score, dominant, weighted = weighted_dominance(sub)
    A = medical_applifier(n_med_factors)
    final_score = float(min(10.0, A * base_score))
    category = risk_band(final_score)

    pollen_dict = vals.get("pollen") or {}
    pollen_vals = [float(v) for v in pollen_dict.values() if v is not None]
    pollen_max = max(pollen_vals) if pollen_vals else None

    return {
        "sub": sub,
        "weighted": weighted,
        "dominant": dominant,
        "base_score": base_score,
        "amplifier": A,  # IMPORTANT: this must be A, not base_score
        "final_score": final_score,
        "category": category,
        "pollen_max": pollen_max,
    }


def build_recommendations(category: str, dominant: str, vals: dict, pollen_max: float | None) -> list[str]:
    recs: list[str] = []
    recs.append("Decision support only. Not diagnosis. Use your asthma plan and trusted clinical guidance.")

    if category == "HIGH":
        recs.append("Reduce strenuous outdoor activity today if possible.")
        recs.append("If symptoms worsen or you’re using reliever more than usual, follow your action plan and seek medical advice if needed.")
    elif category == "MEDIUM":
        recs.append("Monitor symptoms and consider limiting exposure during peak trigger times.")
    else:
        recs.append("Lower environmental risk signal today. Still follow your usual asthma plan.")

    if dominant == "pollution":
        pm25 = vals.get("pm2_5")
        recs.append("Main driver: air quality / pollution.")
        if pm25 is not None:
            recs.append(f"PM2.5 now ≈ {float(pm25):.1f} µg/m³.")
        recs.append("Consider staying away from busy roads at peak traffic; ventilate smartly (when air is better).")

    elif dominant == "pollen":
        recs.append("Main driver: pollen proxy.")
        if pollen_max is not None:
            recs.append(f"Max pollen proxy (current) ≈ {float(pollen_max):.0f}.")
        recs.append("If you’re pollen-sensitive: keep windows closed during peak times, shower/change clothes after being outside.")

    elif dominant == "temp":
        t = vals.get("temp_c")
        recs.append("Main driver: temperature.")
        if t is not None:
            recs.append(f"Temperature now ≈ {float(t):.1f}°C.")
        recs.append("Cold/dry air can trigger symptoms for some people: consider scarf/face covering in cold air.")

    elif dominant == "humidity":
        rh = vals.get("rh")
        recs.append("Main driver: humidity.")
        if rh is not None:
            recs.append(f"Humidity now ≈ {float(rh):.0f}%.")
        recs.append("If indoor air feels irritating, aim for comfortable indoor humidity and avoid damp/mould exposure.")

    elif dominant == "wind":
        w = vals.get("wind")
        recs.append("Main driver: wind / stagnation.")
        if w is not None:
            recs.append(f"Wind now ≈ {float(w):.1f} m/s.")
        recs.append("Low wind can trap pollutants locally. Prefer routes away from traffic hotspots.")

    return recs


    
