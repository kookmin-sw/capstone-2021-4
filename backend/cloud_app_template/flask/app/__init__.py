from flask import Flask, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import time

# CONFIG
app = Flask(__name__, instance_relative_config=True)

# from app.myapi.views import myapi_blueprint
 
# app.register_blueprint(myapi_blueprint,url_prefix="/myapi")

# ROUTES
@app.route('/', methods=['GET', 'POST']) 
def home():
    return render_template('home.html')
