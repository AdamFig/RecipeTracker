import os
os.system("clear") 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

#MySQL Database Connection

load_dotenv()

#Flask App

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DB_User = os.getenv('DB_USER')
DB_Password = os.getenv('DB_PASSWORD')
DB_Host = os.getenv('DB_HOST')
DB_Name = os.getenv('DB_NAME')
DB_Port = os.getenv('DB_PORT')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_User}:{DB_Password}@{DB_Host}:{DB_Port}/{DB_Name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"User('{self.email}')"
    
