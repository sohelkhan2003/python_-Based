from flask import Flask,render_template,request
import joblib
import numpy as np
import pandas as pd

app=Flask(__name__)


# load the the training model and prepocessing
model=joblib.load(r"Project_Logistic_reg\Logistic_reg_3")
scaler=joblib.load(r"Project_Logistic_reg\scaler.pkl")
Education_encoder=joblib.load(r"Project_Logistic_reg\Education_encoder.pkl")
EmploymentType_encoder=joblib.load(r"Project_Logistic_reg\EmploymentType_encoder.pkl")
MaritalStatus_encoder=joblib.load(r"Project_Logistic_reg\MaritalStatus_encoder.pkl")
HasMortgage_encoder=joblib.load(r"Project_Logistic_reg\HasMortgage_encoder.pkl")
LoanPurpose_encoder=joblib.load(r"Project_Logistic_reg\LoanPurpose_encoder.pkl")
HasCoSigner_encoder=joblib.load(r"Project_Logistic_reg\HasCoSigner_encoder.pkl")
HasDependents_encoder=joblib.load(r"Project_Logistic_reg\HasDependents_encoder.pkl")


# ✅ Load SAME scaler used in training
scaler = joblib.load(r"Project_Logistic_reg\scaler.pkl")



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Numerical inputs
        Income = float(request.form["Income"])
        LoanAmount = float(request.form["LoanAmount"])
        CreditScore = float(request.form["CreditScore"])
        MonthsEmployed = float(request.form["MonthsEmployed"])
        NumCreditLines = float(request.form["NumCreditLines"])
        InterestRate = float(request.form["InterestRate"])
        LoanTerm = float(request.form["LoanTerm"])
        DTIRatio = float(request.form["DTIRatio"])

        # Categorical inputs
        Education = Education_encoder.transform([request.form["Education"].lower()])[0]
        EmploymentType = EmploymentType_encoder.transform([request.form["EmploymentType"].lower()])[0]
        MaritalStatus = MaritalStatus_encoder.transform([request.form["MaritalStatus"].lower()])[0]
        HasMortgage = HasMortgage_encoder.transform([request.form["HasMortgage"].lower()])[0]
        HasDependents = HasDependents_encoder.transform([request.form["HasDependents"].lower()])[0]
        LoanPurpose = LoanPurpose_encoder.transform([request.form["LoanPurpose"].lower()])[0]
        HasCoSigner = HasCoSigner_encoder.transform([request.form["HasCoSigner"].lower()])[0]

        # Feature order SAME as training
        input_data = np.array([[
            Income, LoanAmount, CreditScore, MonthsEmployed,
            NumCreditLines, InterestRate, LoanTerm, DTIRatio,
            Education, EmploymentType, MaritalStatus,
            HasMortgage, HasDependents, LoanPurpose, HasCoSigner
        ]])

        # Scale data
        input_scaled = scaler.transform(input_data)

        # Probability
        prob = model.predict_proba(input_scaled)[0][1]

        # Threshold (same as training: 0.11)
        prediction = "Loan Will Default" if prob > 0.11 else "Loan Will Not Default"

        return render_template("index.html", prediction=prediction)

    except Exception as e:
        return render_template("index.html", prediction="Error: Check Input Values")


if __name__ == "__main__":
    app.run(debug=True)