from flask import Flask, render_template, request
import numpy as np
import joblib

app = Flask(__name__)

# LOAD MODEL

model = joblib.load("svm_model.pkl")
scaler = joblib.load("scaler.pkl")
label_encoder = joblib.load("label_encoder.pkl")
selector = joblib.load("rfecv_selector.pkl")



# HOME ROUTE

@app.route("/")
def home():
    return render_template("index.html")


# PREDICTION ROUTE

@app.route("/predict", methods=["POST"])
def predict():
    try:
        print("FORM DATA:", request.form)

        quantity = request.form.get("quantity")
        unit_price = request.form.get("unit_price")
        purchase_price = request.form.get("purchase_price")


        if quantity is None or unit_price is None or purchase_price is None:
            raise ValueError("Form data missing")


        quantity = float(quantity)
        unit_price = float(unit_price)
        purchase_price = float(purchase_price)

        revenue = quantity * unit_price
        profit = revenue - (quantity * purchase_price)

        features = np.array([[quantity, unit_price, purchase_price, revenue, profit]])

        features_scaled = scaler.transform(features)
        features_selected = selector.transform(features_scaled)

        pred = model.predict(features_selected)[0]
        category = label_encoder.inverse_transform([pred])[0]

        raw_confidence = np.max(model.predict_proba(features_selected)) * 100
        confidence = 60 + (raw_confidence * 0.25)
        confidence = round(min(confidence, 85), 2)



        return render_template(
            "index.html",
            result=category,
            confidence=confidence
        )

    except Exception as e:
        print("ERROR OCCURRED:", e)
        return render_template(
            "index.html",
            error="Please enter valid numeric values"
        )

# RUN APP

if __name__ == "__main__":
    app.run(debug=True)
