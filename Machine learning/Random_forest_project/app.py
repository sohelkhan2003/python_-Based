from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the trained model
model = joblib.load('rf.pkl')  # change name if different

# Load label encoder (if used during training)
try:
    le = joblib.load('le.pkl')
except:
    le = None  # fallback if not used

# Exactly the same 8 features used during training
FEATURES = [
    'traffic_congestion_level',
    'weather_condition_severity',
    'port_congestion_level',
    'route_risk_level',
    'disruption_likelihood_score',
    'supplier_reliability_score',
    'eta_variation_hours',
    'fuel_consumption_rate'
]

# Load dataset once to get real min/max for input fields
DATASET_PATH = 'dynamic_supply_chain_logistics_dataset.csv'  # ← update path if needed
df = pd.read_csv(DATASET_PATH)

# Calculate real min/max/step for form validation
feature_ranges = {}
for col in FEATURES:
    if col in df.columns:
        feature_ranges[col] = {
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'step': 0.01 if df[col].dtype == float else 1.0
        }
    else:
        feature_ranges[col] = {'min': 0.0, 'max': 10.0, 'step': 0.01}

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    suggestions = []
    probability = None

    if request.method == 'POST':
        try:
            # Collect form data
            input_data = {}
            for feature in FEATURES:
                value = float(request.form.get(feature, 0))
                input_data[feature] = value

            # Create DataFrame (same format as training)
            df_input = pd.DataFrame([input_data])

            # Predict
            pred_encoded = model.predict(df_input)[0]

            # Get class name
            if le is not None:
                risk_class = le.inverse_transform([pred_encoded])[0]
            else:
                risk_class = {0: 'Low Risk', 1: 'Moderate Risk', 2: 'High Risk'}.get(pred_encoded, 'Unknown')

            # Confidence
            probas = model.predict_proba(df_input)[0]
            probability = round(probas.max() * 100, 1)

            # Business suggestions
            if risk_class == 'High Risk':
                suggestions = [
                    "HIGH RISK DETECTED – Immediate action recommended",
                    "Consider switching to an alternate route or faster mode",
                    "Add extra buffer time to the driver's schedule",
                    "Pre-notify warehouse team to prepare loading/unloading",
                    "Prioritize this shipment to avoid penalties and delays"
                ]
            elif risk_class == 'Moderate Risk':
                suggestions = [
                    "MODERATE RISK – Proceed with caution",
                    "Current route is acceptable – monitor traffic conditions",
                    "Keep 2–3 hours buffer in the expected arrival time",
                    "Stay in regular contact with the driver"
                ]
            else:  # Low Risk
                suggestions = [
                    "LOW RISK – Normal operations can continue",
                    "Maintain standard speed and route",
                    "Opportunity to optimize fuel and resource usage"
                ]

            prediction = {
                'risk_class': risk_class,
                'probability': probability,
                'suggestions': suggestions
            }

        except Exception as e:
            prediction = {'error': str(e)}

    return render_template('index.html',
                         features=FEATURES,
                         feature_ranges=feature_ranges,
                         prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)