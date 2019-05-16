from flask import Flask, request
import sys
sys.path.append('../')
from update_db import *

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/lightnings/update")
def update_lightnings_table():
    return add_lightnings()

@app.route("/lightnings/get")
def get():
    lat = request.args['lat']
    lng = request.args['lng']
    return get_lightnings(lat, lng)

@app.route("/posts/update")
def update_posts_table():
    return add_posts()

@app.route("/posts/update/<tag>")
def update_tag_posts_table(tag):
    return add_posts(tag)

if __name__ == "__main__":
    app.run()
