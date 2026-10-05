from flask import Flask, render_template, request
import pickle
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "model")

model = pickle.load(open(os.path.join(model_path,"model.pkl"),"rb"))
scaler = pickle.load(open(os.path.join(model_path,"scaler.pkl"),"rb"))
model_columns = pickle.load(open(os.path.join(model_path,"columns.pkl"),"rb"))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict',methods=['POST'])
def predict():

    input_data = {
        'Gender':request.form.get('Gender'),
        'Married':request.form.get('Married'),
        'Dependents':request.form.get('Dependents'),
        'Education':request.form.get('Education'),
        'Self_Employed':request.form.get('Self_Employed'),
        'ApplicantIncome':float(request.form.get('ApplicantIncome')),
        'CoapplicantIncome':float(request.form.get('CoapplicantIncome')),
        'LoanAmount':float(request.form.get('LoanAmount')),
        'Loan_Amount_Term':float(request.form.get('Loan_Amount_Term')),
        'Credit_History':float(request.form.get('Credit_History')),
        'Property_Area':request.form.get('Property_Area')
    }

    mapping = {
        'Gender':{'Male':1,'Female':0},
        'Married':{'Yes':1,'No':0},
        'Education':{'Graduate':1,'Not Graduate':0},
        'Self_Employed':{'Yes':1,'No':0}
    }

    processed={}

    for key,val in input_data.items():
        if key in mapping:
            processed[key]=mapping[key].get(val,0)
        else:
            processed[key]=val

    if processed['Dependents']=="3+":
        processed['Dependents']=3
    else:
        processed['Dependents']=int(processed['Dependents'])

    df=pd.DataFrame([processed])

    df=pd.get_dummies(df,columns=['Property_Area'])

    for col in model_columns:
        if col not in df.columns:
            df[col]=0

    df=df[model_columns]

    scaled=scaler.transform(df)

    pred=model.predict(scaled)

    result="Approved" if pred[0]==1 else "Rejected"

    return render_template("index.html",prediction_text=f"Loan Status: {result}")

if __name__=="__main__":
    app.run(debug=True)