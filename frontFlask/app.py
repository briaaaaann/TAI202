from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)

API_URL = "http://127.0.0.1:5000/v1/usuarios/"

@app.route('/')
def index():
    response = requests.get(API_URL)
    data = response.json()
    return render_template('index.html', usuario = data['usuarios'], total=data['total_data'])