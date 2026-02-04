Asthma Environmental Risk Index (FYP)

🔗 Live Streamlit App: https://asthmafypmvp.streamlit.app/

Final Year Project for BSc (Hons) Data Science & Analytics.
An interpretable, rule-based system that provides same-day asthma environmental risk assessment using real-time weather, air quality, and pollen data.

⸻

Project Aim

To design and implement an environment-first asthma risk assessment system that supports informed decision-making by translating environmental trigger data into a transparent and interpretable risk index.

⸻

Project Overview

This project implements a rule-based asthma environmental risk index that:
	•	Uses real-time environmental data rather than retrospective clinical outcomes
	•	Produces a bounded risk score (0–10) and categorical risk level
	•	Prioritises interpretability and plausibility over predictive accuracy
	•	Avoids clinical diagnosis or outcome prediction

The system is deployed as a Streamlit web application and evaluated as part of the Final Year Project.

⸻

System Features
	•	Real-time data ingestion via Open-Meteo APIs
	•	Environmental trigger modelling:
	•	Air quality (EU AQI)
	•	Temperature
	•	Humidity
	•	Wind (stagnation proxy)
	•	Pollen exposure
	•	Standardised sub-indices mapped to a 0–10 scale
	•	Weighted dominant-factor aggregation
	•	Optional self-reported vulnerability amplification
	•	Interactive dashboard and recommendations view

⸻

Methodology (Summary)
	1.	Data Acquisition
Environmental data is fetched at runtime using open, public APIs.
	2.	Sub-Index Construction
Each environmental variable is converted into a discrete severity band based on domain-informed thresholds.
	3.	Weighting Strategy
Relative importance is assigned to environmental factors based on established clinical and epidemiological evidence.
	4.	Aggregation
A weighted dominant-factor approach is used to ensure the most harmful active trigger drives the final risk score.
	5.	Output
The system outputs a risk score (0–10), risk category, dominant factor, and a transparent factor breakdown.

Technology Stack
	•	Python
	•	Streamlit
	•	Open-Meteo APIs (Weather, Air Quality, Pollen)
	•	NumPy
	•	Pandas

asthma_risk_app/
├── Home.py
├── pages/
│   ├── 1_Dashboard.py
│   └── 2_Recommendations.py
├── src/
│   ├── openmeteo_client.py
│   └── risk_engine.py
├── requirements.txt

Data Sources
	•	Open-Meteo Weather API
	•	Open-Meteo Air Quality API
	•	Open-Meteo Pollen API

All data is publicly available and retrieved dynamically at runtime.

⸻

Ethical Considerations
	•	No personal health data is collected or stored
	•	Outputs are non-diagnostic and informational
	•	System logic is transparent and interpretable
	•	Clear separation between environmental risk assessment and clinical decision-making

⸻

Use of Generative AI

Generative AI tools were used to assist with code structuring and implementation support.
All methodological decisions, system logic, weighting strategies, and evaluation design were defined and validated by the author.

⸻

Author

Rizwaan Miah
BSc (Hons) Data Science & Analytics
University of Westminster
