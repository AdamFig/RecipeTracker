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
    session.clear() 
    return redirect(url_for('routes.login'))

# Recipes routes

@routes.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', '')
    direction = request.args.get('direction', 'asc')

    conn = db_connect()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Recipes"
    params = []

    if search_query:
        query += " WHERE Title LIKE %s"
        params.append(f"%{search_query}%")

    valid_sort_columns = {
        'rating': 'Rating', 
        'date': 'Recipe_ID'
    }
    
    if sort_by in valid_sort_columns:
        column = valid_sort_columns[sort_by]
        dir_sql = "DESC" if direction == "desc" else "ASC"
        query += f" ORDER BY {column} {dir_sql}"
    
    cursor.execute(query, tuple(params))
    all_recipes = cursor.fetchall()
    cursor.close()
    conn.close()
        
    return render_template('recipes.html', recipes=all_recipes)

@routes.route('/recipe/<int:recipe_id>')
@login_required
def recipe_detail(recipe_id):
    search_query = request.args.get('search', '')
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Recipes WHERE Recipe_ID = %s", (recipe_id,))
    
    if search_query:
        cursor.execute("SELECT * FROM Recipes WHERE Title LIKE %s", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM Recipes")
    
    recipe = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('recipe_detail.html', recipe=recipe)


@routes.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        image_url = request.form['image_url']
        instructions = request.form['instructions']
        description = request.form['description']
        cooking_time = request.form['cooking_time']
        required_ingredients = request.form['required_ingredients']
        servings = request.form['servings']
        rating = request.form['rating']
        difficulty = request.form['difficulty']
        
        
        conn = db_connect()
        cursor = conn.cursor()
        query = """INSERT INTO Recipes (User_ID, Title, Image_URL, Instructions, Description, Cooking_Time, required_ingredients, Servings, Rating, Difficulty ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (current_user.id, title, image_url, instructions, description, cooking_time, required_ingredients, servings, rating, difficulty))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('routes.recipes'))

    return render_template('add_recipe.html')

@routes.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    rating_min = request.args.get('rating_min')
    rating_max = request.args.get('rating_max')
    months_min = request.args.get('months_min')
    months_max = request.args.get('months_max')
    
    if not rating_min and not rating_max and not months_min and not months_max:
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Recipes ORDER BY Rating DESC LIMIT 3")
        recipes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('recipes.html', recipes=recipes)
    
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM Recipes WHERE 1=1"
    params = []
    
# Code below was modified from bruno desthuilliers on Stack Overflow 
# (JohnnyCc and Desthuilliers)
    
    if rating_min:
        query += " AND Rating >= %s"
        params.append(rating_min)
    if rating_max:
        query += " AND Rating <= %s"
        params.append(rating_max)

    if months_min:
        query += " AND DATE(Created_At) >= %s"
        params.append(months_min)
    if months_max:
        query += " AND DATE(Created_At) <= %s"
        params.append(months_max)
        
    cursor.execute(query, tuple(params))
    recipes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('recipes.html', recipes=recipes)
