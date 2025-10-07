import os
os.system("clear") 

from flask import current_app as app, Blueprint, Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv
routes = Blueprint('routes', __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()

def db_connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class User(UserMixin):
    def __init__(self, user_id, email):
        self.id = user_id  
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT User_ID, Email FROM Users WHERE User_ID = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(row['User_ID'], row['Email'])
    return None

# Routes definitions

@routes.route('/')
def home():
    return render_template("home.html")

@routes.route('/register')
def register():
    return render_template("register.html")

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "Login POST received"
    return render_template("login.html")
        
def init_routes(app):
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login' 
    app.register_blueprint(routes)