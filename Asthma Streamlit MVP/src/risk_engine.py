"""
Asthma Environmental Risk Index (FYP)

This system computes a same-day environmental asthma risk score (0–10) using
real-time weather, air quality, and pollen data.

A rule-based (heuristic) approach was selected over machine learning due to
empirical failure of regression models (R² ≈ 0), indicating no learnable
same-day signal when using population-level proxy targets.

This is a non-diagnostic decision-support tool and does not replace clinical advice.
"""

import numpy as np


# Relative importance of environmental triggers (heuristic, literature-informed)
weights = {
    "pollution": 1.0,  # Strongest direct respiratory hazard
    "temp": 0.8,       # Temperature extremes affect respiratory conditions
    "pollen": 0.7,     # Known allergic asthma trigger
    "humidity": 0.5,   # Affects airway comfort and allergen environment
    "wind": 0.4,       # Lower wind → stagnation, higher wind → dispersion
}


def risk_band(score_0_10: float) -> str:
    """
    Maps numerical score to categorical risk.

    LOW      — score < 3.0  : Minimal environmental trigger activity.
    MODERATE — score < 6.0  : Moderate trigger presence.
    HIGH     — score >= 6.0 : Strong trigger dominance.

    Strict less-than thresholds are used deliberately — this is a
    clinical tool and conservative classification is appropriate.
    Thresholds are heuristic and designed for interpretability.
    """
    if score_0_10 < 3.0:
        return "LOW"
    elif score_0_10 < 6.0:
        return "MODERATE"
    return "HIGH"


def medical_amplifier(n_factors: int) -> float:
    """
    Applies a bounded multiplier to reflect increased vulnerability.

    Individuals with prior exacerbations or poorer symptom control may experience
    greater effects at the same environmental exposure level.

    Multiplier values (1.0 / 1.2 / 1.4) are heuristic and not clinically validated.
    """
    if n_factors <= 0:
        return 1.0
    if n_factors == 1:
        return 1.2
    return 1.4


def temp_index_c(t: float | None) -> int:
    """
    Temperature sub-index.

    Cold air can irritate airways, while higher temperatures may worsen
    respiratory conditions. Lowest-risk range is 10–20°C.

    Bands:
        1 — 10 to 20°C        : Optimal range.
        3 — 5–10°C or 20–25°C : Mild thermal stress.
        6 — 0–5°C or 25–30°C  : Moderate thermal stress.
        9 — Below 0 or above 30°C : High trigger risk.

    Returns 3 (moderate default) if input is None.
    """
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
    """
    Humidity sub-index.

    Low humidity can dry airways; high humidity can increase allergen exposure
    (dust mites, mould). Lowest-risk range is 40–60% RH.

    Bands:
        1 — 40–60% RH        : Optimal range.
        3 — 30–40% or 60–70% : Mild deviation.
        6 — 20–30% or 70–80% : Moderate risk.
        9 — Below 20% or above 80% : High risk.

    Returns 3 (moderate default) if input is None.
    """
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
    """
    Wind sub-index.

    Inverse logic:
    Higher wind disperses pollutants → lower risk.
    Lower wind increases stagnation → higher risk.

    Bands:
        1 — Above 6 m/s : Strong dispersal, lowest accumulation risk.
        3 — 4–6 m/s     : Moderate dispersal.
        6 — 2–4 m/s     : Limited dispersal.
        9 — Below 2 m/s : Stagnant conditions, highest accumulation risk.

    Returns 3 (moderate default) if input is None.
    """
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
    """
    Maps EU Air Quality Index to a 0–10 sub-index.

    Supports two AQI formats returned by Open-Meteo:
        - 1–5 scale  : scaled proportionally to 0–10.
        - 0–100 scale: scaled proportionally to 0–10.

    Limitation:
        Very small values on the 0–100 scale (e.g. AQI = 3) may be
        misclassified as the 1–5 scale. Future versions should enforce
        explicit scale declaration at the API call level.

    Returns 3 (moderate default) if input is None.
    """
    if eu_aqi is None:
        return 3

    x = float(eu_aqi)

    if 0 < x <= 5:
        return int(np.clip(np.ceil((x / 5.0) * 10.0), 1, 10))

    return int(np.clip(np.ceil((x / 100.0) * 10.0), 1, 10))


def pollen_subindex(pollen_dict: dict | None) -> int:
    """
    Pollen sub-index.

    Uses maximum pollen value across all species (worst-case approach).
    Averaging is avoided — a single high-count species poses real risk
    even if other species are low.

    Bands follow UK Met Office NPARU pollen banding guidance:
        2 — Max <= 10  : Low season or off-season.
        4 — Max <= 50  : Moderate pollen load.
        7 — Max <= 100 : High pollen load.
        9 — Max > 100  : Very high, significant allergen risk.

    Returns 2 (mild off-season default) if input is None or empty.
    """
    if not pollen_dict:
        return 2

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
    """
    Aggregates risk using a weighted dominant-factor approach.

    The highest weighted sub-index determines the base score.
    Averaging is deliberately avoided — it would mask a dangerous
    reading with benign values from other factors.

    Returns:
        base_score (float): Weighted score of the dominant factor.
        dominant   (str)  : Name of the dominant factor.
        weighted   (dict) : All weighted scores, retained for audit.
    """
    weighted = {k: weights[k] * sub_idx[k] for k in sub_idx.keys()}
    dominant = max(weighted, key=weighted.get)
    base_score = float(weighted[dominant])
    return base_score, dominant, weighted


def compute_risk(vals: dict, n_med_factors: int) -> dict:
    """
    Main scoring pipeline.

    Steps:
        1. Convert each environmental input to a 0–10 sub-index.
        2. Identify the dominant weighted factor and derive base score.
        3. Apply medical amplifier for clinically vulnerable users.
        4. Cap final score at 10.0 and classify into risk band.

    Expected input keys in vals:
        eu_aqi  (float | None): EU Air Quality Index.
        temp_c  (float | None): Temperature in degrees Celsius.
        rh      (float | None): Relative humidity (%).
        wind    (float | None): Wind speed in m/s.
        pollen  (dict  | None): Pollen species counts.
        pm2_5   (float | None): PM2.5 value (used in recommendations only).

    Returns dict containing:
        sub, weighted, dominant, base_score, amplifier,
        final_score, category, pollen_max.
    """
    sub = {
        "pollution": eu_aqi_to_0_10(vals.get("eu_aqi")),
        "temp": temp_index_c(vals.get("temp_c")),
        "humidity": humidity_index(vals.get("rh")),
        "wind": wind_index_ms(vals.get("wind")),
        "pollen": pollen_subindex(vals.get("pollen")),
    }

    base_score, dominant, weighted = weighted_dominance(sub)
    amplifier = medical_amplifier(n_med_factors)
    final_score = float(min(10.0, amplifier * base_score))
    category = risk_band(final_score)

    pollen_dict = vals.get("pollen") or {}
    pollen_vals = [float(v) for v in pollen_dict.values() if v is not None]
    pollen_max = max(pollen_vals) if pollen_vals else None

    return {
        "sub": sub,
        "weighted": weighted,
        "dominant": dominant,
        "base_score": base_score,
        "amplifier": amplifier,
        "final_score": final_score,
        "category": category,
        "pollen_max": pollen_max,
    }


def build_recommendations(
    category: str,
    dominant: str,
    vals: dict,
    pollen_max: float | None
) -> list[str]:
    """
    Generates plain-language recommendations based on risk category
    and dominant environmental trigger.

    Design principles:
        1. Disclaimer first — always the first item, by design.
           This ensures the indicative-only status of the system is
           communicated before any advice is presented.
        2. Category advice — general behavioural guidance per risk band.
        3. Dominant-factor advice — specific guidance traceable directly
           to the environmental factor driving the score.

    Args:
        category   : "LOW", "MODERATE", or "HIGH".
        dominant   : Dominant factor name from compute_risk().
        vals       : Original environmental readings dict.
        pollen_max : Maximum pollen count from compute_risk().

    Returns:
        list[str]: Ordered recommendations. First item is always the disclaimer.
    """
    recs: list[str] = []

    # Safety disclaimer — always first
    recs.append("Decision support only. Not diagnosis. Follow your asthma plan and trusted clinical guidance.")

    if category == "HIGH":
        recs.append("Reduce strenuous outdoor activity today if possible.")
        recs.append("If symptoms worsen, follow your action plan and seek medical advice if needed.")
    elif category == "MODERATE":
        recs.append("Monitor symptoms and consider limiting exposure during peak trigger times.")
    else:
        recs.append("Lower environmental risk signal today. Continue usual management.")

    if dominant == "pollution":
        pm25 = vals.get("pm2_5")
        recs.append("Main driver: air quality.")
        if pm25 is not None:
            recs.append(f"PM2.5 ≈ {float(pm25):.1f} µg/m³.")
        recs.append("Avoid high-traffic areas where possible.")

    elif dominant == "pollen":
        recs.append("Main driver: pollen.")
        if pollen_max is not None:
            recs.append(f"Max pollen ≈ {float(pollen_max):.0f}.")
        recs.append("Limit exposure during peak times and change clothes after being outdoors.")

    elif dominant == "temp":
        t = vals.get("temp_c")
        recs.append("Main driver: temperature.")
        if t is not None:
            recs.append(f"Temperature ≈ {float(t):.1f}°C.")
        recs.append("Protect airways in extreme temperatures.")

    elif dominant == "humidity":
        rh = vals.get("rh")
        recs.append("Main driver: humidity.")
        if rh is not None:
            recs.append(f"Humidity ≈ {float(rh):.0f}%.")
        recs.append("Maintain comfortable indoor humidity where possible.")

    elif dominant == "wind":
        w = vals.get("wind")
        recs.append("Main driver: wind conditions.")
        if w is not None:
            recs.append(f"Wind ≈ {float(w):.1f} m/s.")
        recs.append("Low wind may increase pollutant concentration locally.")

    return recs
    
