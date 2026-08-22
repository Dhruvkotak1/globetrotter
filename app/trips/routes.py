import os
import secrets
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Trip, TripStop, TripActivity, CustomExpense, City, Activity
from app.trips import trips_bp

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@trips_bp.route('/')
@login_required
def my_trips():
    """Screen 4: My Trips (Trip List) with tabs Ongoing / Upcoming / Completed"""
    search_query = request.args.get('q', '').strip().lower()
    sort_by = request.args.get('sort', 'start_asc') # start_asc, start_desc, budget_desc, title_asc
    
    # Query current user's trips
    query = current_user.trips
    
    if search_query:
        query = query.filter(Trip.title.ilike(f'%{search_query}%') | Trip.description.ilike(f'%{search_query}%'))
        
    if sort_by == 'start_desc':
        query = query.order_by(Trip.start_date.desc())
    elif sort_by == 'title_asc':
        query = query.order_by(Trip.title.asc())
    elif sort_by == 'budget_desc':
        query = query.order_by(Trip.target_budget.desc())
    else: # start_asc
        query = query.order_by(Trip.start_date.asc())
        
    all_trips = query.all()
    
    today = date.today()
    ongoing_trips = [t for t in all_trips if t.start_date <= today <= t.end_date]
    upcoming_trips = [t for t in all_trips if t.start_date > today]
    completed_trips = [t for t in all_trips if t.end_date < today]
    
    return render_template(
        'trips/list.html',
        all_trips=all_trips,
        ongoing_trips=ongoing_trips,
        upcoming_trips=upcoming_trips,
        completed_trips=completed_trips,
        search_query=search_query,
        sort_by=sort_by
    )


@trips_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_trip():
    """Screen 3: Create Trip Screen"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        target_budget_str = request.form.get('target_budget', '0')
        visibility = request.form.get('visibility', 'private')
        preset_image = request.form.get('preset_image', '')
        
        if not title or not start_date_str or not end_date_str:
            flash('Trip title, start date, and end date are required.', 'danger')
            return render_template('trips/create.html')
            
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('trips/create.html')
            
        if end_date < start_date:
            flash('End date cannot be earlier than start date.', 'danger')
            return render_template('trips/create.html')
            
        try:
            target_budget = float(target_budget_str) if target_budget_str else 0.0
        except ValueError:
            target_budget = 0.0
            
        # Cover photo handling
        cover_image = preset_image or 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80'
        if 'cover_image_file' in request.files:
            file = request.files['cover_image_file']
            if file and file.filename and allowed_file(file.filename):
                safe_name = secure_filename(file.filename)
                unique_name = f"trip_{secrets.token_hex(8)}_{safe_name}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
                cover_image = url_for('static', filename=f'uploads/{unique_name}')
                
        trip = Trip(
            user_id=current_user.id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            target_budget=target_budget,
            cover_image=cover_image,
            visibility=visibility,
            share_slug=secrets.token_urlsafe(16)
        )
        
        db.session.add(trip)
        db.session.commit()
        
        flash(f'Trip "{trip.title}" created successfully! Now add stops and activities.', 'success')
        return redirect(url_for('itinerary.builder', trip_id=trip.id))
        
    # Suggested destinations for inspiration on create screen
    suggested_cities = City.query.order_by(City.popularity.desc()).limit(6).all()
    return render_template('trips/create.html', suggested_cities=suggested_cities)


@trips_bp.route('/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    if request.method == 'POST':
        trip.title = request.form.get('title', '').strip()
        trip.description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        target_budget_str = request.form.get('target_budget', '0')
        trip.visibility = request.form.get('visibility', 'private')
        preset_image = request.form.get('preset_image', '')
        
        if not trip.title or not start_date_str or not end_date_str:
            flash('Trip title, start date, and end date are required.', 'danger')
            return render_template('trips/edit.html', trip=trip)
            
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if end_date < start_date:
                flash('End date cannot be earlier than start date.', 'danger')
                return render_template('trips/edit.html', trip=trip)
            trip.start_date = start_date
            trip.end_date = end_date
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('trips/edit.html', trip=trip)
            
        try:
            trip.target_budget = float(target_budget_str) if target_budget_str else 0.0
        except ValueError:
            pass
            
        if preset_image:
            trip.cover_image = preset_image
            
        if 'cover_image_file' in request.files:
            file = request.files['cover_image_file']
            if file and file.filename and allowed_file(file.filename):
                safe_name = secure_filename(file.filename)
                unique_name = f"trip_{secrets.token_hex(8)}_{safe_name}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
                trip.cover_image = url_for('static', filename=f'uploads/{unique_name}')
                
        db.session.commit()
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('itinerary.view_itinerary', trip_id=trip.id))
        
    return render_template('trips/edit.html', trip=trip)


@trips_bp.route('/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    title = trip.title
    db.session.delete(trip)
    db.session.commit()
    flash(f'Trip "{title}" has been deleted.', 'info')
    return redirect(url_for('trips.my_trips'))


@trips_bp.route('/<int:trip_id>/clone', methods=['POST'])
@login_required
def clone_trip(trip_id):
    """Clones an existing shared or public trip into the current user's profile"""
    source_trip = Trip.query.get_or_404(trip_id)
    
    # Check accessibility: must be public, shared, or owned by user
    if source_trip.visibility not in ('public', 'shared') and source_trip.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    new_trip = Trip(
        user_id=current_user.id,
        title=f"Copy of {source_trip.title}",
        description=source_trip.description,
        start_date=source_trip.start_date,
        end_date=source_trip.end_date,
        target_budget=source_trip.target_budget,
        cover_image=source_trip.cover_image,
        visibility='private',
        share_slug=secrets.token_urlsafe(16)
    )
    db.session.add(new_trip)
    db.session.flush() # get new_trip.id
    
    # Clone stops and activities
    for stop in source_trip.stops:
        new_stop = TripStop(
            trip_id=new_trip.id,
            city_id=stop.city_id,
            custom_city_name=stop.custom_city_name,
            order_index=stop.order_index,
            arrival_date=stop.arrival_date,
            departure_date=stop.departure_date,
            accommodation_name=stop.accommodation_name,
            accommodation_cost=stop.accommodation_cost,
            transport_mode=stop.transport_mode,
            transport_cost=stop.transport_cost,
            notes=stop.notes
        )
        db.session.add(new_stop)
        db.session.flush()
        
        for act in stop.activities:
            new_act = TripActivity(
                stop_id=new_stop.id,
                activity_id=act.activity_id,
                custom_title=act.custom_title,
                custom_description=act.custom_description,
                day_number=act.day_number,
                activity_date=act.activity_date,
                time_slot=act.time_slot,
                cost=act.cost,
                category=act.category,
                order_index=act.order_index,
                notes=act.notes
            )
            db.session.add(new_act)
            
    # Clone custom expenses
    for exp in source_trip.custom_expenses:
        new_exp = CustomExpense(
            trip_id=new_trip.id,
            category=exp.category,
            title=exp.title,
            amount=exp.amount,
            expense_date=exp.expense_date,
            notes=exp.notes
        )
        db.session.add(new_exp)
        
    db.session.commit()
    flash(f'Successfully copied trip "{source_trip.title}" to your trips! You can now customize it.', 'success')
    return redirect(url_for('itinerary.builder', trip_id=new_trip.id))


@trips_bp.route('/<int:trip_id>/toggle-visibility', methods=['POST'])
@login_required
def toggle_visibility(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    new_vis = request.form.get('visibility', 'private')
    if new_vis in ('private', 'public', 'shared'):
        trip.visibility = new_vis
        db.session.commit()
        flash(f'Trip visibility updated to {new_vis.capitalize()}.', 'success')
    return redirect(request.referrer or url_for('itinerary.view_itinerary', trip_id=trip.id))
