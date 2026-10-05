# app.py
from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the trained model and preprocessors
model = joblib.load(r'C:\Users\HP\OneDrive\Desktop\python\Machine learning\Bike_price\used_bike_price_model.pkl')
scaler = joblib.load(r'C:\Users\HP\OneDrive\Desktop\python\Machine learning\Bike_price\scaler.pkl')
le_brand = joblib.load(r'C:\Users\HP\OneDrive\Desktop\python\Machine learning\Bike_price\brand_encoder.pkl')
le_owner = joblib.load(r'C:\Users\HP\OneDrive\Desktop\python\Machine learning\Bike_price\owner_encoder_pkl')
le_city = joblib.load(r'C:\Users\HP\OneDrive\Desktop\python\Machine learning\Bike_price\city_encoder.pkl')

# List of options for dropdowns (you can expand these)
BRANDS = ['Bajaj', 'Royal Enfield', 'Hero', 'Yamaha', 'Honda', 'TVS', 'KTM', 'Suzuki', 
          'Ducati', 'Harley-Davidson', 'Triumph', 'Benelli', 'Kawasaki', 'Mahindra', 'Indian']
OWNERS = ['First Owner', 'Second Owner', 'Third Owner', 'Fourth Owner Or More']
CITIES = ['Delhi', 'Bangalore', 'Mumbai', 'Hyderabad', 'Pune', 'Chennai', 'Jaipur', 
          'Ahmedabad', 'Kolkata', 'Lucknow', 'Gurgaon', 'Noida', 'Thane', 'Faridabad', 'Ghaziabad']

@app.route('/')
def home():
    return render_template('index.html', brands=BRANDS, owners=OWNERS, cities=CITIES)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        kms_driven = float(request.form['kms_driven'])
        age = float(request.form['age'])
        power = float(request.form['power'])
        brand = request.form['brand']
        owner = request.form['owner']
        city = request.form['city']

        # Feature engineering
        #depreciation = original_price - (original_price * 0.7)  # rough estimate if not direct
        #depreciation_rate = depreciation / original_price if original_price > 0 else 0
        #kms_per_year = kms_driven / (age + 1)

        # Encode categorical features
        try:
            brand_encoded = le_brand.transform([brand])[0]
        except:
            brand_encoded = 0  # fallback
        try:
            owner_encoded = le_owner.transform([owner])[0]
        except:
            owner_encoded = 0
        try:
            city_encoded = le_city.transform([city])[0]
        except:
            city_encoded = 0

        # Create feature array
        features = np.array([[kms_driven, age, power, owner_encoded, brand_encoded, city_encoded]])

        # Scale features
        features_scaled = scaler.transform(features)

        # Predict
        prediction = model.predict(features_scaled)[0]
        prediction = max(prediction, 0)  # no negative price

        result = f"Estimated Used Bike Price: ₹{int(prediction):,}"
    except Exception as e:
        result = f"Error: {str(e)}. Please check your inputs."

    return render_template('index.html', prediction=result, brands=BRANDS, owners=OWNERS, cities=CITIES)

if __name__ == '__main__':
    app.run(debug=True)
    