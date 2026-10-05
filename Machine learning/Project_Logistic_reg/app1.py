from flask import Flask,rander_template,request
import numpy as mp
import joblib 

app =float(__name__)

# Load model and preprocessing
model =joblib.load(r"Project_Logistic_reg\Logistic_reg_3")
scale=joblib.load(r"Project_Logistic_reg\scaler.pkl")

Education_encoder=joblib.load(r"Project_Logistic_reg\Education_encoder.pkl")
EmploymentType_encoder=joblib.load(r"Project_Logistic_reg\EmploymentType_encoder.pkl")
MaritalStatus_encoder=joblib.load(r"Project_Logistic_reg\MaritalStatus_encoder.pkl")
HasMortgage_encoder=joblib.load(r"Project_Logistic_reg\HasMortgage_encoder.pkl")
LoanPurpose_encoder=joblib.load(r"Project_Logistic_reg\LoanPurpose_encoder.pkl")
HasCoSigner_encoder=joblib.load(r"Project_Logistic_reg\HasCoSigner_encoder.pkl")
HasDependents_encoder=joblib.load(r"Project_Logistic_reg\HasDependents_encoder.pkl")

THTESHOLD =0.11

@app.route("/",methods=['GET','POST'])
def index():
    prediction =None
    probability=None

    if request.method == "POST":
        # Numeric input

    