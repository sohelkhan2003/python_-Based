from flask import Flask,render_template

app=Flask(__name__)

@app.route("/") #static
def home():
    return "<h1>This is about the  home page </h1>"



@app.route("/hello/name") #dynamic
def hello(name):
    return "This is about page"

@app.route("/user/<name>") #dynamic
def greet(name):
    return f"Hello {name}!"


if __name__ == "__main__":
    app.run(debug=True)