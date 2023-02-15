import requests
from flask import send_from_directory, make_response
from flask import Flask, request, jsonify
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import timedelta, datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
from data_sheet import  get_sheet

from user import bp as user_bp
from search import bp as search_bp
from user_history import  bp as user_history_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)




#data和down的id



get_sheet()



app.register_blueprint(user_bp)
app.register_blueprint(search_bp)
app.register_blueprint(user_history_bp)
app.run(host="0.0.0.0", port=8000)