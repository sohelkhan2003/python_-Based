from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the model, scaler, and training columns
model = pickle.load(open('model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))
model_columns = pickle.load(open('columns.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # 1. Capture inputs from the form
    input_data = {
        'Gender': request.form.get('Gender'),
        'Married': request.form.get('Married'),
        'Dependents': request.form.get('Dependents'),
        'Education': request.form.get('Education'),
        'Self_Employed': request.form.get('Self_Employed'),
        'ApplicantIncome': float(request.form.get('ApplicantIncome')),
        'CoapplicantIncome': float(request.form.get('CoapplicantIncome')),
        'LoanAmount': float(request.form.get('LoanAmount')),
        'Loan_Amount_Term': float(request.form.get('Loan_Amount_Term')),
        'Credit_History': float(request.form.get('Credit_History')),
        'Property_Area': request.form.get('Property_Area')
    }

    # 2. Preprocess / Map Inputs (Matching Training Logic)
    # Mapping categorical values to numeric
    mapping = {
        'Gender': {'Male': 1, 'Female': 0},
        'Married': {'Yes': 1, 'No': 0},
        'Education': {'Graduate': 1, 'Not Graduate': 0},
        'Self_Employed': {'Yes': 1, 'No': 0},
        'Dependents': {'3+': 3} # Other numbers stay as they are
    }

    processed_data = {}
    for key, val in input_data.items():
        if key in mapping:
            processed_data[key] = mapping[key].get(val, val)
        else:
            processed_data[key] = val
    
    # Ensure Dependents is int
    processed_data['Dependents'] = int(processed_data['Dependents'])

    # 3. Create DataFrame and Handle One-Hot Encoding for Property_Area
    df_input = pd.DataFrame([processed_data])
    df_input = pd.get_dummies(df_input, columns=['Property_Area'])

    # 4. Align with training columns (add missing dummy columns with 0)
    for col in model_columns:
        if col not in df_input.columns:
            df_input[col] = 0
    
    # Ensure column order matches training exactly
    df_input = df_input[model_columns]

    # 5. Scale and Predict
    input_scaled = scaler.transform(df_input)
    prediction = model.predict(input_scaled)
    
    result = "Approved" if prediction[0] == 1 else "Rejected"
    color = "green" if result == "Approved" else "red"

    return render_template('index.html', 
                           prediction_text=f'Loan Status: {result}',
                           result_color=color)

if __name__ == "__main__":
    app.run(debug=True)