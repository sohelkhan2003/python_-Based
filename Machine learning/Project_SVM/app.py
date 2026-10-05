from flask import Flask, render_template, request
import numpy as np
import joblib

app = Flask(__name__)

# Load trained objects (same folder me hone chahiye)
model = joblib.load("svm_model.pkl")
scaler = joblib.load("scaler.pkl")
le = joblib.load("label_encoder.pkl")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Read inputs from form
        quantity = float(request.form["quantity"])
        unit_price = float(request.form["unit_price"])
        purchase_price = float(request.form["purchase_price"])
        revenue = float(request.form["revenue"])
        profit = float(request.form["profit"])

        # SAME ORDER as training
        X = np.array([[quantity, unit_price, purchase_price, revenue, profit]])

        # Scale input
        X_scaled = scaler.transform(X)

        # Predict
        pred = model.predict(X_scaled)[0]

        # Confidence
        prob = model.predict_proba(X_scaled)
        confidence = float(np.max(prob) * 100)

        # Decode category
        category = le.inverse_transform([pred])[0]

        return render_template(
            "index.html",
            prediction=category,
            confidence=f"{confidence:.2f}%"
        )

    except Exception as e:
        return render_template(
            "index.html",
            prediction=None,
            confidence=None,
            error=str(e)
        )

if __name__ == "__main__":
    app.run(debug=True)

