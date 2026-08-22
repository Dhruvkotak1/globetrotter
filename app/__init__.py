import os
from flask import Flask, render_template
from config import Config
from app.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.trips.routes import trips_bp
    from app.itinerary.routes import itinerary_bp
    from app.budget.routes import budget_bp
    from app.community.routes import community_bp
    from app.admin.routes import admin_bp
    from app.currency.routes import currency_bp
    from app.feedback.routes import feedback_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(currency_bp)
    app.register_blueprint(feedback_bp)

    # Main landing page
    @app.route('/')
    def index():
        from app.models import City, Trip, Feedback
        popular_cities = City.query.order_by(City.popularity.desc()).limit(8).all()
        featured_trips = Trip.query.filter_by(visibility='public').order_by(Trip.created_at.desc()).limit(4).all()
        featured_feedbacks = Feedback.query.filter_by(is_featured=True).order_by(Feedback.created_at.desc()).limit(3).all()
        if not featured_feedbacks:
            featured_feedbacks = Feedback.query.order_by(Feedback.rating.desc(), Feedback.created_at.desc()).limit(3).all()
        return render_template(
            'index.html',
            popular_cities=popular_cities,
            featured_trips=featured_trips,
            featured_feedbacks=featured_feedbacks
        )

    # Custom template filters
    @app.template_filter('currency')
    def format_currency(value):
        try:
            val = float(value or 0.0)
            return f"${val:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter('date_format')
    def format_date(value, format='%b %d, %Y'):
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return str(value)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
