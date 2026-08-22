from functools import wraps
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from sqlalchemy import func
from app.extensions import db
from app.models import User, Trip, TripStop, Activity, City, CustomExpense, Feedback
from app.admin import admin_bp

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Screen 13: Admin / Analytics Dashboard"""
    total_users = User.query.count()
    total_trips = Trip.query.count()
    total_activities = Activity.query.count()
    total_cities = City.query.count()
    
    # Calculate estimated platform budget planned
    all_trips = Trip.query.all()
    total_platform_budget = sum(t.total_cost for t in all_trips)
    
    # Top visited cities based on trip stops count
    top_cities_query = db.session.query(
        City.name, City.country, func.count(TripStop.id).label('stop_count')
    ).join(TripStop, City.id == TripStop.city_id, isouter=True)\
     .group_by(City.id)\
     .order_by(func.count(TripStop.id).desc())\
     .limit(5).all()
     
    # Trip creation distribution / trends
    trips_by_month = {}
    for trip in all_trips:
        month_label = trip.created_at.strftime('%b %Y') if trip.created_at else 'Recent'
        trips_by_month[month_label] = trips_by_month.get(month_label, 0) + 1
        
    trend_labels = list(trips_by_month.keys()) or ['Recent']
    trend_data = list(trips_by_month.values()) or [total_trips]
    
    # User management list
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Recent trips for moderation
    recent_trips = Trip.query.order_by(Trip.created_at.desc()).limit(10).all()

    # Feedbacks & ratings for moderation
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    
    # City stop names and counts for chart
    city_chart_labels = [f"{c[0]}, {c[1]}" for c in top_cities_query] if top_cities_query else ['Tokyo', 'Paris', 'New York', 'Rome', 'Bali']
    city_chart_counts = [max(1, c[2]) for c in top_cities_query] if top_cities_query else [5, 4, 3, 3, 2]
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_trips=total_trips,
        total_activities=total_activities,
        total_cities=total_cities,
        total_platform_budget=total_platform_budget,
        top_cities=top_cities_query,
        users=users,
        recent_trips=recent_trips,
        feedbacks=feedbacks,
        trend_labels=trend_labels,
        trend_data=trend_data,
        city_chart_labels=city_chart_labels,
        city_chart_counts=city_chart_counts
    )


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    if user_id == current_user.id:
        flash('You cannot change your own admin role.', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'Admin status for {user.username} changed to {"Admin" if user.is_admin else "Standard User"}.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete your own account from the admin dashboard.', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" and all their trips have been deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/trips/<int:trip_id>/delete', methods=['POST'])
@admin_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    title = trip.title
    db.session.delete(trip)
    db.session.commit()
    flash(f'Trip "{title}" deleted by administrator.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/feedback/<int:feedback_id>/toggle-featured', methods=['POST'])
@admin_required
def toggle_feedback_featured(feedback_id):
    fb = Feedback.query.get_or_404(feedback_id)
    fb.is_featured = not fb.is_featured
    db.session.commit()
    flash(f'Feedback "{fb.title}" is now {"Featured on Homepage" if fb.is_featured else "Unfeatured"}.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@admin_required
def delete_feedback(feedback_id):
    fb = Feedback.query.get_or_404(feedback_id)
    title = fb.title
    db.session.delete(fb)
    db.session.commit()
    flash(f'Feedback "{title}" deleted successfully.', 'info')
    return redirect(url_for('admin.dashboard'))
