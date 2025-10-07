import os
os.system("clear") 

from .recipe_tracker import db
from datetime import datetime, timezone

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"User('{self.email}')"
    

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Recipe('{self.title}')"

class CookEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    date_cooked = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)