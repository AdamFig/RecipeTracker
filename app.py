import os
import sys
import logging
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, url_for, session
from routes import init_routes

os.system("clear")

# Logging to file 

logging.basicConfig(
    filename = 'db_status.log',
    filemode = 'a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load virtual environment and define DB variables

load_dotenv()

DB_User = os.getenv('DB_USER')
DB_Password = os.getenv('DB_PASSWORD')
DB_Host = os.getenv('DB_HOST')
DB_Name = os.getenv('DB_NAME')
DB_Port = os.getenv('DB_PORT')

# Connect to the database

def db_connect():
    try:
        conn = mysql.connector.connect(
            user=DB_User,
            password=DB_Password,
            host=DB_Host,
            database=DB_Name,
            port=DB_Port
        )
        if conn.is_connected():
            logging.info("Connection Established Successfully")
            return conn
    except Error as e: 
        logging.error(f"Connection Failed: {e}")
        print(f"ERROR: Could not connect to Database titled {DB_Name}")
        sys.exit(1)
        
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#––––––––––EVERYTHING BELOW IS RELATED TO THE MAIN FLASK APPLICATION–––––––––––––––––––––––––––
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


bcrypt = Bcrypt()
login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

bcrypt.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login.html'

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






# Keep this at the bottom

init_routes(app)

if __name__ == "__main__":
    conn = db_connect()
    if conn:
        print("Successfully Connected to the Database!")
        conn.close()
    app.run(debug=True)
