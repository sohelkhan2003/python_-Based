from flask import Flask

app=Flask(__name__)

@app.route("/") #static
def home():
    return "<h1>This is the home page </h1>"


@app.route("/about") #dynamic
def about():
    return "This is about page"

@app.route("/user/<name>") #dynamic
def greet(name):
    return f"Hello {name}!"


if __name__ == "__main__":
    app.run(debug=True)