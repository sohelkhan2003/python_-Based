from flask import Flask, request, render_template
import numpy as np

app=Flask(__name__)

@app.route("/") #static
def home():
    return render_template("index2.html")



@app.route("/predict",methods=['post']) #dynamic
def predict():
   sl=float(request.form.get('sepal_length'))
   sw=float(request.form.get('sepal_length'))
   pl=float(request.form.get('sepal_length'))
   pw=float(request.form.get('sepal_length'))

   features =np.array([[sl,sw,pl,pw]])
   prediction='Iris-setosa'

   return render_template('index2.html',
                          prediction=species,
                          sl=sl,sw=sw,pl=pl,pw=pw)


if __name__ == "__main__":
    app.run(debug=True)