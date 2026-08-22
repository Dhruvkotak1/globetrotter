from datetime import datetime, date, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), default='')
    last_name = db.Column(db.String(64), default='')
    phone = db.Column(db.String(32), default='')
    city = db.Column(db.String(64), default='')
    country = db.Column(db.String(64), default='')
    bio = db.Column(db.Text, default='')
    avatar = db.Column(db.String(256), default='default_avatar.png')
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    saved_destinations = db.relationship('SavedDestination', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    likes = db.relationship('TripLike', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        if self.reset_token == token and self.reset_token_expiration > datetime.utcnow():
            return True
        return False

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def __repr__(self):
        return f"<User {self.username}>"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    country = db.Column(db.String(100), nullable=False, index=True)
    region = db.Column(db.String(100), nullable=False, default='Global') # Europe, Asia, Americas, Africa, Oceania
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    cost_index = db.Column(db.Float, default=3.0) # 1 (Budget) - 5 (Luxury)
    popularity = db.Column(db.Integer, default=80) # 1-100 score
    recommended_days = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    activities = db.relationship('Activity', back_populates='city', cascade='all, delete-orphan', lazy='dynamic')
    stops = db.relationship('TripStop', back_populates='city', lazy='dynamic')
    saved_by = db.relationship('SavedDestination', back_populates='city', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'region': self.region,
            'description': self.description,
            'image_url': self.image_url,
            'cost_index': self.cost_index,
            'popularity': self.popularity,
            'recommended_days': self.recommended_days
        }

    def __repr__(self):
        return f"<City {self.name}, {self.country}>"


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Sightseeing') # Sightseeing, Food & Dining, Adventure, Culture & History, Leisure & Wellness, Transport, Nightlife
    estimated_cost = db.Column(db.Float, default=0.0) # USD
    duration_hours = db.Column(db.Float, default=2.0)
    image_url = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, default=4.5)

    # Relationships
    city = db.relationship('City', back_populates='activities')
    trip_activities = db.relationship('TripActivity', back_populates='activity', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'city_id': self.city_id,
            'city_name': self.city.name if self.city else '',
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'estimated_cost': self.estimated_cost,
            'duration_hours': self.duration_hours,
            'image_url': self.image_url,
            'rating': self.rating
        }

    def __repr__(self):
        return f"<Activity {self.title}>"


class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default='')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    target_budget = db.Column(db.Float, default=0.0)
    cover_image = db.Column(db.String(500), default='https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80')
    visibility = db.Column(db.String(20), default='private') # 'private', 'public', 'shared'
    share_slug = db.Column(db.String(64), unique=True, nullable=False, default=secrets.token_urlsafe)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='trips')
    stops = db.relationship('TripStop', back_populates='trip', cascade='all, delete-orphan', order_by='TripStop.order_index')
    custom_expenses = db.relationship('CustomExpense', back_populates='trip', cascade='all, delete-orphan', order_by='CustomExpense.expense_date')
    likes = db.relationship('TripLike', back_populates='trip', cascade='all, delete-orphan')

    @property
    def status(self):
        today = date.today()
        if self.end_date < today:
            return 'completed'
        elif self.start_date <= today <= self.end_date:
            return 'ongoing'
        else:
            return 'upcoming'

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 1

    @property
    def total_cost(self):
        breakdown = self.breakdown_by_category
        return sum(breakdown.values())

    @property
    def breakdown_by_category(self):
        transport = 0.0
        stay = 0.0
        activities = 0.0
        meals = 0.0
        other = 0.0

        for stop in self.stops:
            transport += (stop.transport_cost or 0.0)
            stay += (stop.accommodation_cost or 0.0)
            for act in stop.activities:
                cat = (act.category or '').lower()
                cost = act.cost or 0.0
                if 'food' in cat or 'dining' in cat or 'meal' in cat:
                    meals += cost
                elif 'transport' in cat:
                    transport += cost
                elif 'stay' in cat or 'hotel' in cat:
                    stay += cost
                else:
                    activities += cost

        for exp in self.custom_expenses:
            cat = (exp.category or '').lower()
            amt = exp.amount or 0.0
            if 'transport' in cat:
                transport += amt
            elif 'stay' in cat or 'hotel' in cat or 'accommodation' in cat:
                stay += amt
            elif 'meal' in cat or 'food' in cat:
                meals += amt
            elif 'activity' in cat or 'activities' in cat or 'sightseeing' in cat:
                activities += amt
            else:
                other += amt

        return {
            'transport': round(transport, 2),
            'stay': round(stay, 2),
            'activities': round(activities, 2),
            'meals': round(meals, 2),
            'other': round(other, 2)
        }

    @property
    def per_day_cost(self):
        days = self.duration_days
        if days > 0:
            return round(self.total_cost / days, 2)
        return round(self.total_cost, 2)

    @property
    def is_overbudget(self):
        if self.target_budget and self.target_budget > 0:
            return self.total_cost > self.target_budget
        return False

    @property
    def budget_percentage(self):
        if self.target_budget and self.target_budget > 0:
            return min(100, round((self.total_cost / self.target_budget) * 100, 1))
        return 0

    def __repr__(self):
        return f"<Trip {self.title}>"


class TripStop(db.Model):
    __tablename__ = 'trip_stops'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    custom_city_name = db.Column(db.String(100), default='')
    order_index = db.Column(db.Integer, default=0)
    arrival_date = db.Column(db.Date, nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    accommodation_name = db.Column(db.String(150), default='')
    accommodation_cost = db.Column(db.Float, default=0.0)
    transport_mode = db.Column(db.String(50), default='Flight') # Flight, Train, Bus, Car, Cruise, Other
    transport_cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, default='')

    # Relationships
    trip = db.relationship('Trip', back_populates='stops')
    city = db.relationship('City', back_populates='stops')
    activities = db.relationship('TripActivity', back_populates='stop', cascade='all, delete-orphan', order_by='TripActivity.order_index')

    @property
    def display_city_name(self):
        if self.city:
            return f"{self.city.name}, {self.city.country}"
        return self.custom_city_name or "Custom Stop"

    @property
    def stop_image(self):
        if self.city and self.city.image_url:
            return self.city.image_url
        return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80'

    @property
    def duration_days(self):
        if self.arrival_date and self.departure_date:
            return max(1, (self.departure_date - self.arrival_date).days + 1)
        return 1

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'city_id': self.city_id,
            'display_city_name': self.display_city_name,
            'stop_image': self.stop_image,
            'order_index': self.order_index,
            'arrival_date': self.arrival_date.isoformat() if self.arrival_date else '',
            'departure_date': self.departure_date.isoformat() if self.departure_date else '',
            'accommodation_name': self.accommodation_name,
            'accommodation_cost': self.accommodation_cost,
            'transport_mode': self.transport_mode,
            'transport_cost': self.transport_cost,
            'notes': self.notes,
            'activities': [act.to_dict() for act in self.activities]
        }

    def __repr__(self):
        return f"<TripStop {self.display_city_name}>"


class TripActivity(db.Model):
    __tablename__ = 'trip_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('trip_stops.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=True)
    custom_title = db.Column(db.String(150), default='')
    custom_description = db.Column(db.Text, default='')
    day_number = db.Column(db.Integer, default=1)
    activity_date = db.Column(db.Date, nullable=True)
    time_slot = db.Column(db.String(30), default='Morning') # e.g., '09:00 AM', 'Morning', 'Afternoon', 'Evening'
    cost = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), default='Sightseeing')
    order_index = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, default='')

    # Relationships
    stop = db.relationship('TripStop', back_populates='activities')
    activity = db.relationship('Activity', back_populates='trip_activities')

    @property
    def display_title(self):
        if self.custom_title:
            return self.custom_title
        elif self.activity:
            return self.activity.title
        return 'Untitled Activity'

    @property
    def display_description(self):
        if self.custom_description:
            return self.custom_description
        elif self.activity:
            return self.activity.description
        return ''

    @property
    def display_image(self):
        if self.activity and self.activity.image_url:
            return self.activity.image_url
        return 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80'

    def to_dict(self):
        return {
            'id': self.id,
            'stop_id': self.stop_id,
            'activity_id': self.activity_id,
            'title': self.display_title,
            'description': self.display_description,
            'image_url': self.display_image,
            'day_number': self.day_number,
            'activity_date': self.activity_date.isoformat() if self.activity_date else '',
            'time_slot': self.time_slot,
            'cost': self.cost,
            'category': self.category,
            'order_index': self.order_index,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<TripActivity {self.display_title}>"


class CustomExpense(db.Model):
    __tablename__ = 'custom_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    category = db.Column(db.String(50), default='Other') # Transport, Stay, Activities, Meals, Shopping, Insurance, Other
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    expense_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, default='')

    # Relationships
    trip = db.relationship('Trip', back_populates='custom_expenses')

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'category': self.category,
            'title': self.title,
            'amount': self.amount,
            'expense_date': self.expense_date.isoformat() if self.expense_date else '',
            'notes': self.notes
        }

    def __repr__(self):
        return f"<CustomExpense {self.title} (${self.amount})>"


class SavedDestination(db.Model):
    __tablename__ = 'saved_destinations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='saved_destinations')
    city = db.relationship('City', back_populates='saved_by')

    def __repr__(self):
        return f"<SavedDestination User:{self.user_id} City:{self.city_id}>"


class TripLike(db.Model):
    __tablename__ = 'trip_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    trip = db.relationship('Trip', back_populates='likes')
    user = db.relationship('User', back_populates='likes')

    def __repr__(self):
        return f"<TripLike Trip:{self.trip_id} User:{self.user_id}>"
