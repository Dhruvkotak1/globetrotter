import os
import uuid
from datetime import datetime, timezone
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# ---------------------------------------------------------
# 1. FLASK APP & DATABASE CONFIGURATION
# ---------------------------------------------------------
app = Flask(__name__)

# Base directory to ensure the DB is created in the right folder
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'globetrotter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-hackathon-key-change-later'

# Initialize Database
db = SQLAlchemy(app)

# ---------------------------------------------------------
# 2. DATABASE MODELS
# ---------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), default='default_avatar.png')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    trips = db.relationship('Trip', backref='traveler', lazy=True, cascade="all, delete-orphan")

class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    cover_image = db.Column(db.String(255), default='default_trip.jpg')
    description = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    share_slug = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    itinerary_items = db.relationship('ItineraryItem', backref='trip', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='trip', lazy=True, cascade="all, delete-orphan")

class ItineraryItem(db.Model):
    __tablename__ = 'itinerary_items'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    activity_date = db.Column(db.Date, nullable=True)
    time_of_day = db.Column(db.String(50), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    estimated_cost = db.Column(db.Float, default=0.0)

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False) 
    amount = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    description = db.Column(db.String(150), nullable=True)

# ---------------------------------------------------------
# 3. AUTOMATIC TABLE CREATION
# ---------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        # This creates globetrotter.db and all tables if they don't exist
        db.create_all()
        print("Database 'globetrotter.db' and all tables created successfully!")