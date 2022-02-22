# project: p4
# submitter: tzhao86
# partner: none
# hours: 4.0

import re
import pandas as pd
from io import BytesIO
from matplotlib import pyplot as plt
from flask import Flask, request, jsonify, Response
from urllib.robotparser import RobotFileParser

# main.csv's data come from https://www.kaggle.com/mavezdabas/nychourlytemperature

app = Flask(__name__)
# df = pd.read_csv("main.csv")

n = 0 # number of people subscribed 
counter = 0 # number of time webpage being visited
donation_from_A = 0 # number of donations from A
donation_from_B = 0 # number of donations from B

@app.route('/')
def home():
    global counter
    counter += 1 # increment number of visits
    if counter <= 10:
        if counter % 2 == 0:
            with open("indexA.html") as f:
                html = f.read()
        else:
            with open("indexB.html") as f:
                html = f.read()
    elif donation_from_A > donation_from_B:
        with open("indexA.html") as f:
            html = f.read()
    else:
        with open("indexB.html") as f:
            html = f.read()
       
    return html

@app.route('/browse.html')
def browse():
    return f"<html><h1>Browse</h1>{pd.read_csv('main.csv').to_html()}</html>"

@app.route('/donate.html')
def donate():
    if "from" in request.args and request.args["from"] == "A":
        global donation_from_A
        donation_from_A += 1
    else:
        global donation_from_B
        donation_from_B += 1
    with open("donate.html") as f:
        html = f.read()
    return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    suffix = r"\.(edu|com|org|net|gov)"
    if re.match(r"\w+@\w+" + suffix, email):
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n")
        global n
        n += 1 # increment of subscribers
        return jsonify(f"thanks, you're subscriber number {n}!")
    return jsonify("Invalid email!")

@app.route('/temp_derterminants.svg')
def dashboard_1():
    fig, ax = plt.subplots()
    df = pd.read_csv('main.csv')
    if "ylabel" in request.args and request.args["ylabel"] == "Humidity": 
        df.plot(x = "TemperatureF", y = "Humidity", style = 'o', ax = ax)
        ax.set_ylabel("Humidity")
    else:
        df.plot(x = "TemperatureF", y = "Wind SpeedMPH", style = 'o', ax = ax)
        ax.set_ylabel("Wind Speed(MPH)")
    ax.set_xlabel("Temperature(F)")
    plt.tight_layout()
    f = BytesIO()
    fig.savefig(f, format = "svg")
    plt.close(fig)
    return Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route('/temp_hourly.svg')
def dashboard_2():
    fig, ax = plt.subplots()
    df = pd.read_csv('main.csv')
    df.plot.bar(x = "TimeEST", y = "TemperatureF", ax = ax)
    ax.set_xlabel("TimeEST")
    ax.set_ylabel("Tempearture(F)")
    plt.tight_layout()
    f = BytesIO()
    fig.savefig(f, format = "svg")
    plt.close(fig)
    return Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route("/robots.txt")
def robot():
    return Response("\n".join(["User-Agent: hungrycaterpillar", "Disallow: /browse",
                     "User-Agent: busyspider", "Disallow: /"]), headers = {'Content-Type': 'text/plain'})
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
    
# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.