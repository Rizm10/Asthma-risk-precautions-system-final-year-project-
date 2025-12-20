import numpy as py 

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



    
