import os
os.system("clear") 

from flask import current_app as app, g, Blueprint, Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

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

# Initialization of app

def init_routes(app):
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login' 
    app.register_blueprint(routes)

    @app.before_request
    def load_logged_in_user():
        if current_user.is_authenticated:
            g.user = current_user
        else:
            g.user = None

# ^^^ Initialization of app ^^^

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

@routes.route('/')
def home():
    return render_template("home.html")

# User routes

@routes.route('/register', methods=["GET", "POST"])
def register():
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        password_confirmation = request.form['password_confirmation']
        
        if password != password_confirmation:
            error = "Passwords do not match"
            return render_template("register.html", error=error)
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return render_template("register.html", error="This email is already registered. Please log in instead.")
        
        query = "INSERT INTO Users (Name, Email, Role, Password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, role, hashed_password))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        
        return redirect(url_for('routes.login'))
    return render_template("register.html")

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']
        
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user is not None and bcrypt.check_password_hash(user['Password'], password):
            login_user(User(user['User_ID'], user['Email']))
            
            return redirect(url_for('routes.recipes'))
        else:
            return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")

@routes.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

# Recipes routes

@routes.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    return render_template('recipes.html')

@routes.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        image_url = request.form['image_url']
        description = request.form['description']
        cooking_time = request.form['cooking_time']
        
        conn = db_connect()
        cursor = conn.cursor()
        query = """INSERT INTO Recipes (User_ID, Title, Image_URL, Description, Cooking_Time) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (current_user.id, title, image_url, description, cooking_time))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('routes.recipes'))

    return render_template('add_recipe.html')